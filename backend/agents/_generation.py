import asyncio
import logging
import os
from importlib import metadata
from time import perf_counter
from collections.abc import AsyncIterator
from typing import Any

from dotenv import load_dotenv

from core.logging_utils import log_event

load_dotenv()

try:
    from google import genai as google_genai
    from google.genai import errors as genai_errors
    from google.genai import types as genai_types
except ImportError:  # pragma: no cover - depends on local environment setup
    google_genai = None
    genai_errors = None
    genai_types = None

DEFAULT_CONNECT_TIMEOUT_SECONDS = 25
DEFAULT_STREAM_CHUNK_TIMEOUT_SECONDS = 45
DEFAULT_PROVIDER_PROBE_TIMEOUT_SECONDS = 18
DEFAULT_PROVIDER_RUNTIME_MAX_SECONDS = 40
PREFERRED_MODEL_FAMILIES = ("gemini-1.5-flash", "gemini-1.5-pro")
MODEL_REJECTION_TOKENS = ("preview", "robotics", "embedding", "image", "vision", "experimental", "tts", "aqa", "live")
REQUIRED_GENERATION_ACTION = "generatecontent"
CONFIGURED_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "").strip()
PROVIDER_PROBE_PROMPT = "Reply with exactly OK."
PROVIDER_PROBE_MAX_OUTPUT_TOKENS = 8
EMBEDDING_MODEL_NAME = "gemini-embedding-001"

PROVIDER_STATE: dict[str, Any] = {
    "configured": False,
    "ready": False,
    "selected_model": None,
    "model_name": None,
    "provider_status": "unknown",
    "provider_error_category": None,
    "available_models_count": 0,
    "available_models_sample": [],
    "candidate_models_count": 0,
    "rejected_models_count": 0,
    "model_selection_strategy": "uninitialized",
    "startup_validation_time_ms": None,
    "sdk_version": "unavailable",
}

logger = logging.getLogger("scholr.provider")
_CLIENT = None


class ScholrGenerationError(Exception):
    def __init__(self, user_message: str, *, retryable: bool = True, category: str = "provider"):
        super().__init__(user_message)
        self.user_message = user_message
        self.retryable = retryable
        self.category = category


def _sdk_version() -> str:
    try:
        return metadata.version("google-genai")
    except metadata.PackageNotFoundError:
        return "unavailable"


def _sdk_not_available_error() -> ScholrGenerationError:
    return ScholrGenerationError(
        "The Google GenAI SDK is not installed for this backend yet. Install dependencies and redeploy.",
        retryable=False,
        category="sdk_not_installed",
    )


def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ScholrGenerationError(
            "Scholr is not configured with a Gemini API key yet. Add a valid key in backend/.env and restart the backend.",
            retryable=False,
            category="invalid_api_key",
        )
    return api_key


def _normalize_model_name(model_name: str | None) -> str:
    normalized = (model_name or "").strip()
    if normalized.startswith("models/"):
        return normalized.replace("models/", "", 1)
    return normalized


def _normalize_action_name(action_name: Any) -> str:
    text = str(getattr(action_name, "name", action_name) or "").strip().lower()
    return "".join(character for character in text if character.isalnum())


def _extract_supported_actions(model: Any) -> list[str]:
    supported_actions: set[str] = set()

    for attribute in ("supported_actions", "supported_generation_methods", "supported_methods", "actions"):
        raw_value = getattr(model, attribute, None)
        if not raw_value:
            continue

        values = raw_value if isinstance(raw_value, (list, tuple, set)) else [raw_value]
        for value in values:
            normalized = _normalize_action_name(value)
            if normalized:
                supported_actions.add(normalized)

    return sorted(supported_actions)


def _matches_model_family(model_name: str, family: str) -> bool:
    lowered_name = model_name.lower()
    lowered_family = family.lower()
    return lowered_name == lowered_family or lowered_name.startswith(f"{lowered_family}-")


def _get_preferred_family(model_name: str) -> str | None:
    for family in PREFERRED_MODEL_FAMILIES:
        if _matches_model_family(model_name, family):
            return family
    return None


def _model_sort_key(model_name: str) -> tuple[int, str]:
    preferred_family = _get_preferred_family(model_name)
    if preferred_family is None:
        return (len(PREFERRED_MODEL_FAMILIES), model_name)

    exact_match_bonus = 0 if model_name.lower() == preferred_family.lower() else 1
    family_index = PREFERRED_MODEL_FAMILIES.index(preferred_family)
    return (family_index, f"{exact_match_bonus}:{model_name}")


def _reject_model_reasons(model_name: str, supported_actions: list[str]) -> list[str]:
    lowered = model_name.lower()
    reasons: list[str] = []

    if not lowered.startswith("gemini"):
        reasons.append("non_gemini_model")

    for token in MODEL_REJECTION_TOKENS:
        if token in lowered:
            reasons.append(f"excluded_token:{token}")
            break

    if REQUIRED_GENERATION_ACTION not in supported_actions:
        reasons.append("missing_generateContent")

    return reasons


def _classify_provider_error(exc: Exception) -> ScholrGenerationError:
    message = str(exc).lower()

    if isinstance(exc, asyncio.TimeoutError):
        return ScholrGenerationError(
            "Scholr took too long to get a response from Gemini. Please try again in a moment.",
            retryable=True,
            category="provider_timeout",
        )

    if genai_errors and isinstance(exc, genai_errors.APIError):
        code = getattr(exc, "code", None)
        provider_message = getattr(exc, "message", str(exc)).lower()
        message = provider_message or message

        if code in {400, 404} or ("model" in message and ("not found" in message or "supported" in message)):
            return ScholrGenerationError(
                "This Gemini model is unavailable for the current project. Switch to an active model and restart the backend.",
                retryable=False,
                category="invalid_model",
            )

        if code in {401, 403} or "api key" in message or "permission" in message or "unauth" in message:
            return ScholrGenerationError(
                "The Gemini API key looks missing, invalid, or does not have access to this model. Update backend/.env and restart the backend.",
                retryable=False,
                category="invalid_api_key",
            )

        if code == 429 or "quota" in message or "rate limit" in message or "resource exhausted" in message:
            return ScholrGenerationError(
                "Gemini is temporarily rate limited or out of quota for this project. Please wait a bit and try again.",
                retryable=True,
                category="quota_exceeded",
            )

        if code and code >= 500:
            return ScholrGenerationError(
                "AI provider error. Please retry.",
                retryable=True,
                category="provider_5xx",
            )

    if "deadline" in message or "timed out" in message or "timeout" in message:
        return ScholrGenerationError(
            "Gemini did not respond in time. Please retry once the connection is stable.",
            retryable=True,
            category="provider_timeout",
        )

    if "unsupported location" in message or "region" in message or "country" in message:
        return ScholrGenerationError(
            "The AI provider is not available for this deployment region right now.",
            retryable=False,
            category="blocked_region",
        )

    if "service unavailable" in message or "temporarily unavailable" in message or "internal" in message or "bad gateway" in message:
        return ScholrGenerationError(
            "AI provider error. Please retry.",
            retryable=True,
            category="provider_5xx",
        )

    return ScholrGenerationError(
        "AI provider error. Please retry.",
        retryable=True,
        category="provider_5xx",
    )


def _should_try_fallback(exc: ScholrGenerationError) -> bool:
    return exc.category in {"provider_5xx", "provider_timeout", "invalid_model", "empty_response"}


def _build_client():
    global _CLIENT

    if google_genai is None:
        raise _sdk_not_available_error()

    if _CLIENT is None:
        _CLIENT = google_genai.Client(api_key=_get_api_key())

    return _CLIENT


def _discover_models() -> list[dict[str, Any]]:
    client = _build_client()
    discovered: dict[str, dict[str, Any]] = {}

    for model in client.models.list():
        name = _normalize_model_name(getattr(model, "name", None))
        if not name:
            continue

        supported_actions = _extract_supported_actions(model)
        existing = discovered.get(name)
        if existing:
            existing["supported_actions"] = sorted(set(existing["supported_actions"]) | set(supported_actions))
            continue

        discovered[name] = {
            "name": name,
            "supported_actions": supported_actions,
        }

    return [discovered[name] for name in sorted(discovered)]


def _select_candidate_models(requested_model_name: str | None, discovered_models: list[dict[str, Any]]) -> dict[str, Any]:
    rejected_models: list[dict[str, Any]] = []
    allowed_models: list[dict[str, Any]] = []

    for descriptor in discovered_models:
        model_name = descriptor["name"]
        supported_actions = descriptor.get("supported_actions", [])
        rejected_reasons = _reject_model_reasons(model_name, supported_actions)

        if rejected_reasons:
            rejected_models.append(
                {
                    "name": model_name,
                    "reasons": rejected_reasons,
                }
            )
            continue

        allowed_models.append(descriptor)

    preferred_candidates = sorted(
        (descriptor for descriptor in allowed_models if _get_preferred_family(descriptor["name"])),
        key=lambda descriptor: _model_sort_key(descriptor["name"]),
    )
    fallback_candidates = sorted(
        (descriptor for descriptor in allowed_models if not _get_preferred_family(descriptor["name"])),
        key=lambda descriptor: descriptor["name"],
    )

    strategy = "no_supported_generation_model"
    selected_descriptors: list[dict[str, Any]] = []
    if preferred_candidates:
        selected_descriptors = preferred_candidates + fallback_candidates
        strategy = "allowlist-first"
        if fallback_candidates:
            strategy = "allowlist-first-with-filtered-fallback"
    elif fallback_candidates:
        selected_descriptors = fallback_candidates
        strategy = "filtered-discovery-fallback"

    candidates = tuple(descriptor["name"] for descriptor in selected_descriptors)

    log_event(
        logger,
        "provider_models_discovered",
        discovered_models=[descriptor["name"] for descriptor in discovered_models[:20]],
        discovered_models_count=len(discovered_models),
    )
    log_event(
        logger,
        "provider_models_filtered",
        candidate_models=list(candidates),
        candidate_models_count=len(candidates),
        rejected_models=rejected_models[:20],
        rejected_models_count=len(rejected_models),
        requested_model_name=_normalize_model_name(requested_model_name) or None,
        configured_model_name=_normalize_model_name(CONFIGURED_MODEL_NAME) or None,
        model_selection_strategy=strategy,
    )

    return {
        "candidates": candidates,
        "rejected_models": rejected_models,
        "strategy": strategy,
    }


def _extract_chunk_text(chunk: Any) -> str:
    text = getattr(chunk, "text", None)
    if text:
        return text

    candidates = getattr(chunk, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", None)
            if part_text:
                return part_text

    return ""


async def _probe_model_generation(model_name: str) -> None:
    client = _build_client()
    response = await asyncio.wait_for(
        client.aio.models.generate_content(
            model=model_name,
            contents=PROVIDER_PROBE_PROMPT,
            config=genai_types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=PROVIDER_PROBE_MAX_OUTPUT_TOKENS,
            ),
        ),
        timeout=DEFAULT_PROVIDER_PROBE_TIMEOUT_SECONDS,
    )
    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise ScholrGenerationError(
            "Gemini returned an empty response during provider startup validation.",
            retryable=True,
            category="empty_response",
        )


def _update_provider_state(
    *,
    configured: bool,
    ready: bool,
    selected_model: str | None,
    status: str,
    error_category: str | None,
    discovered_models: list[dict[str, Any]],
    candidate_models_count: int = 0,
    rejected_models_count: int = 0,
    model_selection_strategy: str = "unknown",
    startup_validation_time_ms: int | None = None,
) -> None:
    discovered_names = [descriptor["name"] for descriptor in discovered_models]
    PROVIDER_STATE.update(
        {
            "configured": configured,
            "ready": ready,
            "selected_model": selected_model,
            "model_name": selected_model,
            "provider_status": status,
            "provider_error_category": error_category,
            "available_models_count": len(discovered_names),
            "available_models_sample": discovered_names[:8],
            "candidate_models_count": candidate_models_count,
            "rejected_models_count": rejected_models_count,
            "model_selection_strategy": model_selection_strategy,
            "startup_validation_time_ms": startup_validation_time_ms,
            "sdk_version": _sdk_version(),
        }
    )


def get_provider_status() -> dict[str, Any]:
    return {
        "provider_configured": PROVIDER_STATE["configured"],
        "provider_ready": PROVIDER_STATE["ready"],
        "selected_model": PROVIDER_STATE["selected_model"],
        "model_name": PROVIDER_STATE["model_name"],
        "provider_status": PROVIDER_STATE["provider_status"],
        "provider_error_category": PROVIDER_STATE["provider_error_category"],
        "available_models_count": PROVIDER_STATE["available_models_count"],
        "available_models_sample": PROVIDER_STATE["available_models_sample"],
        "candidate_models_count": PROVIDER_STATE["candidate_models_count"],
        "rejected_models_count": PROVIDER_STATE["rejected_models_count"],
        "model_selection_strategy": PROVIDER_STATE["model_selection_strategy"],
        "provider_sdk_version": PROVIDER_STATE["sdk_version"],
        "startup_validation_time_ms": PROVIDER_STATE["startup_validation_time_ms"],
    }


async def validate_provider_startup() -> dict[str, Any]:
    started_at = perf_counter()
    discovered_models: list[dict[str, Any]] = []

    try:
        _get_api_key()
        _build_client()
    except ScholrGenerationError as exc:
        _update_provider_state(
            configured=False,
            ready=False,
            selected_model=None,
            status="not_configured",
            error_category=exc.category,
            discovered_models=[],
            candidate_models_count=0,
            rejected_models_count=0,
            model_selection_strategy="not_configured",
            startup_validation_time_ms=round((perf_counter() - started_at) * 1000),
        )
        return get_provider_status()

    try:
        discovered_models = _discover_models()
    except Exception as exc:
        classified = _classify_provider_error(exc)
        log_event(
            logger,
            "provider_model_discovery_failed",
            auth_configured=True,
            provider_exception_type=type(exc).__name__,
            provider_exception_message=str(exc),
            error_category=classified.category,
        )
        _update_provider_state(
            configured=True,
            ready=False,
            selected_model=None,
            status="not_ready",
            error_category=classified.category,
            discovered_models=[],
            candidate_models_count=0,
            rejected_models_count=0,
            model_selection_strategy="discovery_failed",
            startup_validation_time_ms=round((perf_counter() - started_at) * 1000),
        )
        return get_provider_status()

    selection = _select_candidate_models(CONFIGURED_MODEL_NAME, discovered_models)
    candidates = selection["candidates"]
    if not candidates:
        log_event(
            logger,
            "provider_generation_capability_mismatch",
            auth_configured=True,
            discovered_models=[descriptor["name"] for descriptor in discovered_models[:12]],
            available_models_count=len(discovered_models),
            rejected_models=selection["rejected_models"][:12],
            model_selection_strategy=selection["strategy"],
        )
        _update_provider_state(
            configured=True,
            ready=False,
            selected_model=None,
            status="not_ready",
            error_category="no_supported_generation_model",
            discovered_models=discovered_models,
            candidate_models_count=0,
            rejected_models_count=len(selection["rejected_models"]),
            model_selection_strategy=selection["strategy"],
            startup_validation_time_ms=round((perf_counter() - started_at) * 1000),
        )
        return get_provider_status()

    for candidate in candidates:
        try:
            await _probe_model_generation(candidate)
        except ScholrGenerationError as exc:
            log_event(
                logger,
                "provider_generation_failed",
                model_name=candidate,
                error_category=exc.category,
                stage="startup_probe",
            )
            continue
        except Exception as exc:
            classified = _classify_provider_error(exc)
            log_event(
                logger,
                "provider_generation_failed",
                model_name=candidate,
                error_category=classified.category,
                provider_exception_type=type(exc).__name__,
                provider_exception_message=str(exc),
                stage="startup_probe",
            )
            continue

        _update_provider_state(
            configured=True,
            ready=True,
            selected_model=candidate,
            status="ready",
            error_category=None,
            discovered_models=discovered_models,
            candidate_models_count=len(candidates),
            rejected_models_count=len(selection["rejected_models"]),
            model_selection_strategy=selection["strategy"],
            startup_validation_time_ms=round((perf_counter() - started_at) * 1000),
        )
        log_event(
            logger,
            "provider_model_selected",
            model_name=candidate,
            stage="startup_probe",
            available_models_count=len(discovered_models),
            candidate_models_count=len(candidates),
            model_selection_strategy=selection["strategy"],
        )
        return get_provider_status()

    _update_provider_state(
        configured=True,
        ready=False,
        selected_model=candidates[0],
        status="not_ready",
        error_category="invalid_model",
        discovered_models=discovered_models,
        candidate_models_count=len(candidates),
        rejected_models_count=len(selection["rejected_models"]),
        model_selection_strategy=selection["strategy"],
        startup_validation_time_ms=round((perf_counter() - started_at) * 1000),
    )
    log_event(
        logger,
        "provider_generation_capability_mismatch",
        auth_configured=True,
        discovered_models=[descriptor["name"] for descriptor in discovered_models[:12]],
        attempted_candidates=list(candidates),
        rejected_models=selection["rejected_models"][:12],
        error_category="invalid_model",
        model_selection_strategy=selection["strategy"],
    )
    return get_provider_status()


def resolve_model_name(requested_model_name: str) -> str:
    preferred = PROVIDER_STATE["selected_model"]
    if PROVIDER_STATE["ready"] and preferred:
        return preferred
    requested = _normalize_model_name(requested_model_name)
    return requested or _normalize_model_name(CONFIGURED_MODEL_NAME) or PREFERRED_MODEL_FAMILIES[0]


async def stream_gemini_response(
    *,
    model_name: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> AsyncIterator[str]:
    client = _build_client()

    discovered_models: list[dict[str, Any]] = []
    if not discovered_models:
        try:
            discovered_models = _discover_models()
        except Exception:
            discovered_models = []

    selection = _select_candidate_models(resolve_model_name(model_name), discovered_models)
    candidates = selection["candidates"]
    if not candidates:
        raise ScholrGenerationError(
            "This Gemini project does not currently expose any supported text generation models.",
            retryable=False,
            category="no_supported_generation_model",
        )

    last_error: ScholrGenerationError | None = None

    for index, candidate in enumerate(candidates):
        last_error = None

        try:
            log_event(
                logger,
                "provider_model_selected",
                model_name=candidate,
                stage="generation_open",
            )
            stream = await asyncio.wait_for(
                client.aio.models.generate_content_stream(
                    model=candidate,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_output_tokens,
                    ),
                ),
                timeout=DEFAULT_CONNECT_TIMEOUT_SECONDS,
            )
        except ScholrGenerationError as exc:
            last_error = exc
        except Exception as exc:
            last_error = _classify_provider_error(exc)

        if last_error:
            log_event(
                logger,
                "provider_generation_failed",
                model_name=candidate,
                error_category=last_error.category,
                stage="generation_open",
            )
            if _should_try_fallback(last_error) and index < len(candidates) - 1:
                log_event(
                    logger,
                    "provider_model_fallback",
                    attempted_model=candidate,
                    fallback_model=candidates[index + 1],
                    error_category=last_error.category,
                )
                continue
            raise last_error

        chunks_received = 0
        stream_deadline = perf_counter() + DEFAULT_PROVIDER_RUNTIME_MAX_SECONDS

        async for chunk in stream:
            if perf_counter() >= stream_deadline:
                last_error = ScholrGenerationError(
                    "Gemini did not finish responding in time. Please try again.",
                    retryable=True,
                    category="provider_timeout",
                )
                break

            text = _extract_chunk_text(chunk)
            if not text:
                continue

            chunks_received += 1
            yield text

        if last_error:
            log_event(
                logger,
                "provider_generation_failed",
                model_name=candidate,
                error_category=last_error.category,
                streamed_chunks=chunks_received,
                stage="stream",
            )
            if _should_try_fallback(last_error) and index < len(candidates) - 1:
                log_event(
                    logger,
                    "provider_model_fallback",
                    attempted_model=candidate,
                    fallback_model=candidates[index + 1],
                    error_category=last_error.category,
                    streamed_chunks=chunks_received,
                )
                continue
            raise last_error

        if chunks_received == 0:
            last_error = ScholrGenerationError(
                "Scholr did not receive any usable text from Gemini for this prompt. Please try rephrasing it.",
                retryable=True,
                category="empty_response",
            )
            log_event(
                logger,
                "provider_generation_failed",
                model_name=candidate,
                error_category=last_error.category,
                streamed_chunks=0,
                stage="stream",
            )
            if _should_try_fallback(last_error) and index < len(candidates) - 1:
                log_event(
                    logger,
                    "provider_model_fallback",
                    attempted_model=candidate,
                    fallback_model=candidates[index + 1],
                    error_category=last_error.category,
                    streamed_chunks=0,
                )
                continue
            raise last_error

        PROVIDER_STATE.update(
            {
                "ready": True,
                "selected_model": candidate,
                "model_name": candidate,
                "provider_status": "ready",
                "provider_error_category": None,
                "candidate_models_count": len(candidates),
                "rejected_models_count": len(selection["rejected_models"]),
                "model_selection_strategy": selection["strategy"],
            }
        )
        log_event(
            logger,
            "provider_generation_success",
            model_name=candidate,
            streamed_chunks=chunks_received,
        )
        return

    if last_error:
        raise last_error

    raise ScholrGenerationError(
        "AI provider error. Please retry.",
        retryable=True,
        category="provider_5xx",
    )


def embed_texts(texts: list[str], *, task_type: str) -> list[list[float]]:
    client = _build_client()

    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL_NAME,
            contents=texts,
            config=genai_types.EmbedContentConfig(task_type=task_type),
        )
    except Exception as exc:  # pragma: no cover - depends on provider runtime
        raise ScholrGenerationError(
            "Embeddings could not be generated for this document right now.",
            retryable=True,
            category="provider_5xx",
        ) from exc

    embeddings = getattr(response, "embeddings", None) or []
    values = [getattr(item, "values", None) for item in embeddings if getattr(item, "values", None)]
    if not values:
        raise ScholrGenerationError(
            "Embeddings returned in an unexpected format.",
            retryable=True,
            category="empty_response",
        )

    return values


async def run_provider_smoke_test(prompt: str = PROVIDER_PROBE_PROMPT) -> dict[str, Any]:
    provider_status = await validate_provider_startup()
    result: dict[str, Any] = {
        "provider_configured": provider_status["provider_configured"],
        "provider_ready": provider_status["provider_ready"],
        "provider_status": provider_status["provider_status"],
        "selected_model": provider_status["selected_model"],
        "model_name": provider_status["model_name"],
        "provider_error_category": provider_status["provider_error_category"],
        "provider_sdk_version": provider_status["provider_sdk_version"],
        "available_models_count": provider_status["available_models_count"],
        "available_models_sample": provider_status["available_models_sample"],
        "candidate_models_count": provider_status["candidate_models_count"],
        "rejected_models_count": provider_status["rejected_models_count"],
        "model_selection_strategy": provider_status["model_selection_strategy"],
        "startup_validation_time_ms": provider_status["startup_validation_time_ms"],
        "prompt": prompt,
    }

    if not provider_status["provider_ready"]:
        result["success"] = False
        return result

    try:
        collected: list[str] = []
        async for chunk in stream_gemini_response(
            model_name=provider_status["selected_model"] or PREFERRED_MODEL_FAMILIES[0],
            prompt=prompt,
            temperature=0.0,
            max_output_tokens=PROVIDER_PROBE_MAX_OUTPUT_TOKENS,
        ):
            collected.append(chunk)

        response_text = "".join(collected).strip()
        result.update(
            {
                "success": bool(response_text),
                "response_preview": response_text[:80],
                "response_length": len(response_text),
                "provider_error_category": None if response_text else "empty_response",
            }
        )
        if not response_text:
            result["provider_status"] = "not_ready"
        return result
    except ScholrGenerationError as exc:
        result.update(
            {
                "success": False,
                "provider_status": "not_ready",
                "provider_error_category": exc.category,
                "response_preview": None,
                "response_length": 0,
            }
        )
        return result
