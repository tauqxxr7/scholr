import asyncio
import logging
import os
import random
import json
from importlib import metadata
from time import perf_counter
from collections.abc import AsyncIterator
from typing import Any
from datetime import datetime, timedelta

from dotenv import load_dotenv
import httpx

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
DEFAULT_PROVIDER_PROBE_TIMEOUT_SECONDS = 5
DEFAULT_PROVIDER_RUNTIME_MAX_SECONDS = 40
DEFAULT_PROVIDER_RECOVERY_INTERVAL_SECONDS = 180
DEFAULT_PROVIDER_RECOVERY_JITTER_SECONDS = 25
DEFAULT_PROVIDER_VALIDATED_TTL_SECONDS = 900
DEFAULT_PROVIDER_DISCOVERY_TTL_SECONDS = 900
DEFAULT_PROVIDER_MIN_RETRY_SECONDS = 30
STRICT_MODEL_PRIORITY = (
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
)
MODEL_REJECTION_TOKENS = ("preview", "robotics", "embedding", "image", "vision", "experimental", "tts", "aqa", "live")
REQUIRED_GENERATION_ACTION = "generatecontent"
CONFIGURED_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "").strip()
CONFIGURED_OPENROUTER_MODEL_NAME = os.getenv("OPENROUTER_MODEL_NAME", "").strip()
PROVIDER_PROBE_PROMPT = "Reply with exactly OK."
PROVIDER_PROBE_MAX_OUTPUT_TOKENS = 4
EMBEDDING_MODEL_NAME = "gemini-embedding-001"
PROVIDER_COOLDOWN_SECONDS = 180
PROVIDER_QUOTA_COOLDOWN_THRESHOLD = 2
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://scholr-coral.vercel.app").strip()
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Scholr").strip()
OPENROUTER_MODEL_PRIORITY = (
    "google/gemini-1.5-flash",
    "google/gemini-1.5-pro",
    "google/gemini-2.0-flash-lite",
    "google/gemini-2.0-flash",
)
OPENROUTER_MODEL_REJECTION_TOKENS = ("preview", "experimental", "robotics", "embedding", "image", "vision", "audio")
OPENROUTER_DEFAULT_STREAM_CHUNK_SIZE = 180

PROVIDER_STATE: dict[str, Any] = {
    "configured": False,
    "ready": False,
    "active_provider": None,
    "fallback_provider": "academic_fallback_engine",
    "provider_failover_reason": None,
    "selected_model": None,
    "model_name": None,
    "provider_status": "unknown",
    "provider_error_category": None,
    "available_models_count": 0,
    "available_models_sample": [],
    "candidate_models_count": 0,
    "rejected_models_count": 0,
    "validated_models_count": 0,
    "failed_validation_models_count": 0,
    "selected_model_validation_status": "not_validated",
    "failed_model_reasons": [],
    "quota_failure_count": 0,
    "last_successful_generation_timestamp": None,
    "provider_recovery_state": "probing",
    "provider_recovery_attempts": 0,
    "provider_tier_strategy": ["gemini", "openrouter", "academic_fallback_engine"],
    "model_selection_strategy": "uninitialized",
    "startup_validation_time_ms": None,
    "sdk_version": "unavailable",
    "openrouter_fallback_configured": bool(os.getenv("OPENROUTER_API_KEY", "").strip()),
    "gemini_provider_ready": False,
    "openrouter_provider_ready": False,
    "last_validated_timestamp": None,
}

logger = logging.getLogger("scholr.provider")
_CLIENT = None
_PROVIDER_COOLDOWN_UNTIL: datetime | None = None
_RECOVERY_TASK: asyncio.Task | None = None
_LAST_RECOVERY_ATTEMPT_AT: datetime | None = None
_DISCOVERED_MODELS_CACHE: list[dict[str, Any]] | None = None
_DISCOVERED_MODELS_CACHE_AT: datetime | None = None
_OPENROUTER_DISCOVERED_MODELS_CACHE: list[dict[str, Any]] | None = None
_OPENROUTER_DISCOVERED_MODELS_CACHE_AT: datetime | None = None


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


def _yield_text_chunks(text: str, chunk_size: int = OPENROUTER_DEFAULT_STREAM_CHUNK_SIZE) -> AsyncIterator[str]:
    async def _iterator() -> AsyncIterator[str]:
        for start in range(0, len(text), chunk_size):
            yield text[start : start + chunk_size]

    return _iterator()


def _utc_now() -> datetime:
    return datetime.utcnow()


def _utc_timestamp() -> str:
    return _utc_now().isoformat(timespec="seconds") + "Z"


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _validated_state_is_fresh() -> bool:
    validated_at = _parse_timestamp(PROVIDER_STATE.get("last_validated_timestamp"))
    if validated_at is None or not PROVIDER_STATE["ready"] or not PROVIDER_STATE["selected_model"]:
        return False
    return (_utc_now() - validated_at).total_seconds() < DEFAULT_PROVIDER_VALIDATED_TTL_SECONDS


def _discovery_cache_is_fresh() -> bool:
    if _DISCOVERED_MODELS_CACHE_AT is None or _DISCOVERED_MODELS_CACHE is None:
        return False
    return (_utc_now() - _DISCOVERED_MODELS_CACHE_AT).total_seconds() < DEFAULT_PROVIDER_DISCOVERY_TTL_SECONDS


def _openrouter_discovery_cache_is_fresh() -> bool:
    if _OPENROUTER_DISCOVERED_MODELS_CACHE_AT is None or _OPENROUTER_DISCOVERED_MODELS_CACHE is None:
        return False
    return (_utc_now() - _OPENROUTER_DISCOVERED_MODELS_CACHE_AT).total_seconds() < DEFAULT_PROVIDER_DISCOVERY_TTL_SECONDS


def _provider_recovery_sleep_seconds() -> int:
    if _cooldown_active():
        return max(15, _cooldown_remaining_seconds())
    return DEFAULT_PROVIDER_RECOVERY_INTERVAL_SECONDS + random.randint(0, DEFAULT_PROVIDER_RECOVERY_JITTER_SECONDS)


def _cooldown_active() -> bool:
    global _PROVIDER_COOLDOWN_UNTIL
    if _PROVIDER_COOLDOWN_UNTIL is None:
        return False
    if _utc_now() >= _PROVIDER_COOLDOWN_UNTIL:
        _PROVIDER_COOLDOWN_UNTIL = None
        if PROVIDER_STATE["provider_recovery_state"] == "cooldown":
            PROVIDER_STATE["provider_recovery_state"] = "probing"
        return False
    return True


def _cooldown_remaining_seconds() -> int:
    if not _cooldown_active() or _PROVIDER_COOLDOWN_UNTIL is None:
        return 0
    return max(0, int((_PROVIDER_COOLDOWN_UNTIL - _utc_now()).total_seconds()))


def _enter_provider_cooldown() -> None:
    global _PROVIDER_COOLDOWN_UNTIL
    _PROVIDER_COOLDOWN_UNTIL = _utc_now() + timedelta(seconds=PROVIDER_COOLDOWN_SECONDS)
    PROVIDER_STATE["provider_recovery_state"] = "cooldown"


def _record_provider_failure(category: str) -> None:
    if category == "quota_exceeded":
        PROVIDER_STATE["quota_failure_count"] += 1
        if PROVIDER_STATE["quota_failure_count"] >= PROVIDER_QUOTA_COOLDOWN_THRESHOLD:
            _enter_provider_cooldown()
        else:
            PROVIDER_STATE["provider_recovery_state"] = "degraded"
        return

    if category in {"provider_5xx", "provider_timeout", "no_validated_generation_model", "no_supported_generation_model"}:
        PROVIDER_STATE["provider_recovery_state"] = "degraded"


def _record_provider_success(model_name: str, provider_name: str, *, failover_reason: str | None = None) -> None:
    PROVIDER_STATE["ready"] = True
    PROVIDER_STATE["active_provider"] = provider_name
    PROVIDER_STATE["fallback_provider"] = "openrouter" if provider_name == "gemini" and _openrouter_configured() else "academic_fallback_engine"
    PROVIDER_STATE["provider_failover_reason"] = failover_reason
    PROVIDER_STATE["selected_model"] = model_name
    PROVIDER_STATE["model_name"] = model_name
    PROVIDER_STATE["provider_status"] = "ready"
    PROVIDER_STATE["provider_error_category"] = None
    PROVIDER_STATE["quota_failure_count"] = 0
    PROVIDER_STATE["last_successful_generation_timestamp"] = _utc_timestamp()
    PROVIDER_STATE["last_validated_timestamp"] = _utc_timestamp()
    PROVIDER_STATE["provider_recovery_state"] = "active"
    PROVIDER_STATE["gemini_provider_ready"] = provider_name == "gemini"
    PROVIDER_STATE["openrouter_provider_ready"] = provider_name == "openrouter"


def _was_degraded_before_success() -> bool:
    return bool(
        PROVIDER_STATE["provider_error_category"]
        or PROVIDER_STATE["provider_recovery_state"] in {"degraded", "cooldown", "recovering", "probing"}
        or not PROVIDER_STATE["ready"]
    )


def _mark_recovery_attempt_started() -> None:
    global _LAST_RECOVERY_ATTEMPT_AT
    _LAST_RECOVERY_ATTEMPT_AT = _utc_now()
    PROVIDER_STATE["provider_recovery_attempts"] += 1
    if PROVIDER_STATE["provider_recovery_state"] != "cooldown":
        PROVIDER_STATE["provider_recovery_state"] = "recovering"


def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ScholrGenerationError(
            "Scholr is not configured with a Gemini API key yet. Add a valid key in backend/.env and restart the backend.",
            retryable=False,
            category="invalid_api_key",
        )
    return api_key


def _openrouter_configured() -> bool:
    return bool(os.getenv("OPENROUTER_API_KEY", "").strip())


def _get_openrouter_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ScholrGenerationError(
            "Scholr is not configured with an OpenRouter API key yet.",
            retryable=False,
            category="invalid_api_key",
        )
    return api_key


def _build_openrouter_headers() -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {_get_openrouter_api_key()}",
        "Content-Type": "application/json",
        "X-OpenRouter-Experimental-Metadata": "enabled",
    }
    if OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    if OPENROUTER_APP_NAME:
        headers["X-Title"] = OPENROUTER_APP_NAME
    return headers


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
    for family in STRICT_MODEL_PRIORITY:
        if _matches_model_family(model_name, family):
            return family
    return None


def _matches_openrouter_family(model_name: str, family: str) -> bool:
    lowered_name = model_name.lower()
    lowered_family = family.lower()
    return (
        lowered_name == lowered_family
        or lowered_name.startswith(f"{lowered_family}-")
        or lowered_name.startswith(f"{lowered_family}:")
    )


def _get_openrouter_preferred_family(model_name: str) -> str | None:
    for family in OPENROUTER_MODEL_PRIORITY:
        if _matches_openrouter_family(model_name, family):
            return family
    return None


def _model_sort_key(model_name: str) -> tuple[int, str]:
    preferred_family = _get_preferred_family(model_name)
    if preferred_family is None:
        return (len(STRICT_MODEL_PRIORITY), model_name)

    exact_match_bonus = 0 if model_name.lower() == preferred_family.lower() else 1
    family_index = STRICT_MODEL_PRIORITY.index(preferred_family)
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


def _classify_openrouter_error(exc: Exception) -> ScholrGenerationError:
    if isinstance(exc, asyncio.TimeoutError):
        return ScholrGenerationError(
            "OpenRouter took too long to respond. Please try again in a moment.",
            retryable=True,
            category="provider_timeout",
        )

    if isinstance(exc, httpx.TimeoutException):
        return ScholrGenerationError(
            "OpenRouter took too long to respond. Please try again in a moment.",
            retryable=True,
            category="provider_timeout",
        )

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        response_text = exc.response.text.lower()

        if status_code in {401, 403}:
            return ScholrGenerationError(
                "The OpenRouter API key is missing, invalid, or blocked for this deployment.",
                retryable=False,
                category="invalid_api_key",
            )
        if status_code == 404 or "model" in response_text and "not found" in response_text:
            return ScholrGenerationError(
                "The selected OpenRouter model is unavailable for this project right now.",
                retryable=False,
                category="invalid_model",
            )
        if status_code in {402, 429} or "quota" in response_text or "rate limit" in response_text:
            return ScholrGenerationError(
                "OpenRouter is temporarily rate limited or out of credits for this project.",
                retryable=True,
                category="quota_exceeded",
            )
        if status_code >= 500:
            return ScholrGenerationError(
                "AI provider error. Please retry.",
                retryable=True,
                category="provider_5xx",
            )

    if isinstance(exc, httpx.RequestError):
        return ScholrGenerationError(
            "OpenRouter could not be reached right now. Please try again shortly.",
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
    global _DISCOVERED_MODELS_CACHE, _DISCOVERED_MODELS_CACHE_AT
    if _discovery_cache_is_fresh():
        return list(_DISCOVERED_MODELS_CACHE or [])

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

    models = [discovered[name] for name in sorted(discovered)]
    _DISCOVERED_MODELS_CACHE = models
    _DISCOVERED_MODELS_CACHE_AT = _utc_now()
    return list(models)


def _select_candidate_models(requested_model_name: str | None, discovered_models: list[dict[str, Any]]) -> dict[str, Any]:
    rejected_models: list[dict[str, Any]] = []
    models_by_family: dict[str, list[dict[str, Any]]] = {family: [] for family in STRICT_MODEL_PRIORITY}

    for descriptor in discovered_models:
        model_name = descriptor["name"]
        supported_actions = descriptor.get("supported_actions", [])
        rejected_reasons = _reject_model_reasons(model_name, supported_actions)
        matched_family = _get_preferred_family(model_name)

        if rejected_reasons:
            rejected_models.append(
                {
                    "name": model_name,
                    "reasons": rejected_reasons,
                }
            )
            continue

        if matched_family is None:
            rejected_models.append(
                {
                    "name": model_name,
                    "reasons": ["outside_strict_priority"],
                }
            )
            continue

        models_by_family[matched_family].append(descriptor)

    selected_descriptors: list[dict[str, Any]] = []
    for family in STRICT_MODEL_PRIORITY:
        family_models = sorted(models_by_family[family], key=lambda descriptor: _model_sort_key(descriptor["name"]))
        selected_descriptors.extend(family_models)

    strategy = "no_supported_generation_model"
    if selected_descriptors:
        strategy = "strict-priority-validated-fallback"

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


def _discover_openrouter_models() -> list[dict[str, Any]]:
    global _OPENROUTER_DISCOVERED_MODELS_CACHE, _OPENROUTER_DISCOVERED_MODELS_CACHE_AT
    if _openrouter_discovery_cache_is_fresh():
        return list(_OPENROUTER_DISCOVERED_MODELS_CACHE or [])

    with httpx.Client(timeout=DEFAULT_CONNECT_TIMEOUT_SECONDS, headers=_build_openrouter_headers()) as client:
        response = client.get(f"{OPENROUTER_API_BASE}/models")
        response.raise_for_status()
        payload = response.json()

    discovered: list[dict[str, Any]] = []
    for item in payload.get("data", []):
        model_id = str(item.get("id") or "").strip()
        if not model_id:
            continue

        architecture = item.get("architecture") or {}
        output_modalities = architecture.get("output_modalities") or []
        discovered.append(
            {
                "name": model_id,
                "modality": str(architecture.get("modality") or ""),
                "output_modalities": [str(entry).lower() for entry in output_modalities],
                "supported_parameters": [str(entry).lower() for entry in (item.get("supported_parameters") or [])],
            }
        )

    _OPENROUTER_DISCOVERED_MODELS_CACHE = discovered
    _OPENROUTER_DISCOVERED_MODELS_CACHE_AT = _utc_now()
    return list(discovered)


def _reject_openrouter_model_reasons(descriptor: dict[str, Any]) -> list[str]:
    model_name = descriptor["name"]
    lowered = model_name.lower()
    reasons: list[str] = []

    if not lowered.startswith("google/gemini"):
        reasons.append("non_gemini_openrouter_model")

    for token in OPENROUTER_MODEL_REJECTION_TOKENS:
        if token in lowered:
            reasons.append(f"excluded_token:{token}")
            break

    output_modalities = descriptor.get("output_modalities", [])
    modality = str(descriptor.get("modality") or "").lower()
    if "text" not in output_modalities and "text" not in modality:
        reasons.append("non_text_output")

    return reasons


def _select_openrouter_candidate_models(requested_model_name: str | None, discovered_models: list[dict[str, Any]]) -> dict[str, Any]:
    rejected_models: list[dict[str, Any]] = []
    models_by_family: dict[str, list[dict[str, Any]]] = {family: [] for family in OPENROUTER_MODEL_PRIORITY}

    for descriptor in discovered_models:
        model_name = descriptor["name"]
        rejected_reasons = _reject_openrouter_model_reasons(descriptor)
        matched_family = _get_openrouter_preferred_family(model_name)

        if rejected_reasons:
            rejected_models.append({"name": model_name, "reasons": rejected_reasons})
            continue

        if matched_family is None:
            rejected_models.append({"name": model_name, "reasons": ["outside_openrouter_priority"]})
            continue

        models_by_family[matched_family].append(descriptor)

    selected_descriptors: list[dict[str, Any]] = []
    for family in OPENROUTER_MODEL_PRIORITY:
        family_models = sorted(models_by_family[family], key=lambda descriptor: descriptor["name"])
        selected_descriptors.extend(family_models)

    strategy = "no_supported_generation_model"
    if selected_descriptors:
        strategy = "openrouter-priority-validated-fallback"

    candidates = tuple(descriptor["name"] for descriptor in selected_descriptors)
    log_event(
        logger,
        "openrouter_models_filtered",
        candidate_models=list(candidates),
        candidate_models_count=len(candidates),
        rejected_models=rejected_models[:20],
        rejected_models_count=len(rejected_models),
        requested_model_name=_normalize_model_name(requested_model_name) or None,
        configured_model_name=_normalize_model_name(CONFIGURED_OPENROUTER_MODEL_NAME) or None,
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


async def _openrouter_generate_text(
    *,
    model_name: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> str:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_output_tokens,
        "stream": False,
    }

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(DEFAULT_PROVIDER_RUNTIME_MAX_SECONDS, connect=DEFAULT_CONNECT_TIMEOUT_SECONDS),
        headers=_build_openrouter_headers(),
    ) as client:
        response = await client.post(f"{OPENROUTER_API_BASE}/chat/completions", json=payload)
        response.raise_for_status()
        body = response.json()

    choices = body.get("choices") or []
    if not choices:
        raise ScholrGenerationError(
            "OpenRouter returned an empty response for this prompt.",
            retryable=True,
            category="empty_response",
        )

    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        text = "".join(str(part.get("text") or "") for part in content if isinstance(part, dict))
    else:
        text = str(content or "")

    cleaned = text.strip()
    if not cleaned:
        raise ScholrGenerationError(
            "OpenRouter returned an empty response for this prompt.",
            retryable=True,
            category="empty_response",
        )
    return cleaned


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


async def _probe_openrouter_model_generation(model_name: str) -> None:
    await asyncio.wait_for(
        _openrouter_generate_text(
            model_name=model_name,
            prompt=PROVIDER_PROBE_PROMPT,
            temperature=0.0,
            max_output_tokens=PROVIDER_PROBE_MAX_OUTPUT_TOKENS,
        ),
        timeout=DEFAULT_PROVIDER_PROBE_TIMEOUT_SECONDS,
    )


def _build_failed_model_reason(model_name: str, category: str) -> dict[str, str]:
    return {
        "model": model_name,
        "reason": category,
    }


def _build_provider_degraded_text(module: str, topic: str, details: str, *, subject: str | None = None) -> str:
    if module == "research":
        return f"""## Provider Temporarily Unavailable
Scholr is temporarily in fallback academic mode for this research request, so here is a safe study plan while live AI generation recovers.

## Topic Received
{topic}

## Immediate Research Directions
1. Break the topic into three search angles: core concept, practical application, and latest improvement papers.
2. Search Google Scholar, Semantic Scholar, and IEEE Xplore using the exact topic plus one use-case keyword.
3. Compare at least two survey papers before reading individual implementation papers.

## Suggested Search Terms
- "{topic} survey"
- "{topic} review paper"
- "{topic} applications"
- "{topic} limitations"

## What To Do While Scholr Retries
{details}

## Retry Checklist
- retry in a minute
- simplify the topic wording
- try a narrower project-focused variation
"""

    if module == "notes":
        return f"""## Provider Temporarily Unavailable
Scholr is temporarily in fallback academic mode for this notes request, so here is a safe revision framework for this topic.

## Topic Received
{topic}

## Revision Outline
1. Write a two-line definition of the topic in your own words.
2. List five key concepts, subtypes, or steps related to it.
3. Add formulas, diagrams, or conditions that usually appear in exams.
4. End with three quick viva-style questions.

## What To Review First
- core definition
- important classifications
- exam-heavy formulas or conditions
- one real example or use case

## What To Do While Scholr Retries
{details}
"""

    subject_line = subject or "General"
    return f"""## Provider Temporarily Unavailable
Scholr is temporarily in fallback academic mode for this doubt request, so here is a safe explanation scaffold.

## Subject
{subject_line}

## Doubt Received
{topic}

## How To Approach It
1. Rewrite the doubt as one direct textbook question.
2. Identify the core definition behind it.
3. Write one example that proves the idea in practice.
4. Compare it with one related concept so the difference is clear.

## What To Check Next
- class notes or textbook definition
- one worked example
- one common mistake students make here

## What To Do While Scholr Retries
{details}
"""


def build_provider_degraded_text(module: str, topic: str, *, subject: str | None = None) -> str:
    return _build_provider_degraded_text(
        module,
        topic,
        "The provider orchestration layer is still healthy enough to keep your workflow moving, but live generation is temporarily unavailable.",
        subject=subject,
    )


def _update_provider_state(
    *,
    configured: bool,
    ready: bool,
    active_provider: str | None,
    fallback_provider: str | None,
    provider_failover_reason: str | None,
    selected_model: str | None,
    status: str,
    error_category: str | None,
    discovered_models: list[dict[str, Any]],
    candidate_models_count: int = 0,
    rejected_models_count: int = 0,
    validated_models_count: int = 0,
    failed_validation_models_count: int = 0,
    selected_model_validation_status: str = "not_validated",
    failed_model_reasons: list[dict[str, str]] | None = None,
    quota_failure_count: int | None = None,
    last_successful_generation_timestamp: str | None = None,
    provider_recovery_state: str | None = None,
    model_selection_strategy: str = "unknown",
    startup_validation_time_ms: int | None = None,
    last_validated_timestamp: str | None = None,
    gemini_provider_ready: bool | None = None,
    openrouter_provider_ready: bool | None = None,
) -> None:
    discovered_names = [descriptor["name"] for descriptor in discovered_models]
    PROVIDER_STATE.update(
        {
            "configured": configured,
            "ready": ready,
            "active_provider": active_provider,
            "fallback_provider": fallback_provider,
            "provider_failover_reason": provider_failover_reason,
            "selected_model": selected_model,
            "model_name": selected_model,
            "provider_status": status,
            "provider_error_category": error_category,
            "available_models_count": len(discovered_names),
            "available_models_sample": discovered_names[:8],
            "candidate_models_count": candidate_models_count,
            "rejected_models_count": rejected_models_count,
            "validated_models_count": validated_models_count,
            "failed_validation_models_count": failed_validation_models_count,
            "selected_model_validation_status": selected_model_validation_status,
            "failed_model_reasons": failed_model_reasons or [],
            "quota_failure_count": PROVIDER_STATE["quota_failure_count"] if quota_failure_count is None else quota_failure_count,
            "last_successful_generation_timestamp": (
                PROVIDER_STATE["last_successful_generation_timestamp"]
                if last_successful_generation_timestamp is None
                else last_successful_generation_timestamp
            ),
            "provider_recovery_state": (
                PROVIDER_STATE["provider_recovery_state"] if provider_recovery_state is None else provider_recovery_state
            ),
            "provider_recovery_attempts": PROVIDER_STATE["provider_recovery_attempts"],
            "provider_tier_strategy": PROVIDER_STATE["provider_tier_strategy"],
            "model_selection_strategy": model_selection_strategy,
            "startup_validation_time_ms": startup_validation_time_ms,
            "sdk_version": _sdk_version(),
            "openrouter_fallback_configured": bool(os.getenv("OPENROUTER_API_KEY", "").strip()),
            "gemini_provider_ready": (
                PROVIDER_STATE["gemini_provider_ready"] if gemini_provider_ready is None else gemini_provider_ready
            ),
            "openrouter_provider_ready": (
                PROVIDER_STATE["openrouter_provider_ready"] if openrouter_provider_ready is None else openrouter_provider_ready
            ),
            "last_validated_timestamp": (
                PROVIDER_STATE["last_validated_timestamp"]
                if last_validated_timestamp is None
                else last_validated_timestamp
            ),
        }
    )


def get_provider_status() -> dict[str, Any]:
    return {
        "provider_configured": PROVIDER_STATE["configured"],
        "provider_ready": PROVIDER_STATE["ready"],
        "active_provider": PROVIDER_STATE["active_provider"],
        "fallback_provider": PROVIDER_STATE["fallback_provider"],
        "provider_failover_reason": PROVIDER_STATE["provider_failover_reason"],
        "selected_model": PROVIDER_STATE["selected_model"],
        "model_name": PROVIDER_STATE["model_name"],
        "provider_status": PROVIDER_STATE["provider_status"],
        "provider_error_category": PROVIDER_STATE["provider_error_category"],
        "available_models_count": PROVIDER_STATE["available_models_count"],
        "available_models_sample": PROVIDER_STATE["available_models_sample"],
        "candidate_models_count": PROVIDER_STATE["candidate_models_count"],
        "rejected_models_count": PROVIDER_STATE["rejected_models_count"],
        "validated_models_count": PROVIDER_STATE["validated_models_count"],
        "failed_validation_models_count": PROVIDER_STATE["failed_validation_models_count"],
        "selected_model_validation_status": PROVIDER_STATE["selected_model_validation_status"],
        "failed_model_reasons": PROVIDER_STATE["failed_model_reasons"],
        "quota_failure_count": PROVIDER_STATE["quota_failure_count"],
        "quota_cooldown_remaining_seconds": _cooldown_remaining_seconds(),
        "last_successful_generation_timestamp": PROVIDER_STATE["last_successful_generation_timestamp"],
        "provider_recovery_state": PROVIDER_STATE["provider_recovery_state"],
        "provider_recovery_attempts": PROVIDER_STATE["provider_recovery_attempts"],
        "provider_tier_strategy": PROVIDER_STATE["provider_tier_strategy"],
        "model_selection_strategy": PROVIDER_STATE["model_selection_strategy"],
        "provider_sdk_version": PROVIDER_STATE["sdk_version"],
        "startup_validation_time_ms": PROVIDER_STATE["startup_validation_time_ms"],
        "openrouter_fallback_configured": PROVIDER_STATE["openrouter_fallback_configured"],
        "gemini_provider_ready": PROVIDER_STATE["gemini_provider_ready"],
        "openrouter_provider_ready": PROVIDER_STATE["openrouter_provider_ready"],
        "last_validated_timestamp": PROVIDER_STATE["last_validated_timestamp"],
    }


async def _provider_recovery_loop() -> None:
    while True:
        try:
            if not PROVIDER_STATE["ready"]:
                if _cooldown_active():
                    log_event(
                        logger,
                        "provider_recovery_waiting",
                        provider_recovery_state=PROVIDER_STATE["provider_recovery_state"],
                        quota_cooldown_remaining_seconds=_cooldown_remaining_seconds(),
                    )
                else:
                    await validate_provider_startup()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - defensive background task guard
            log_event(
                logger,
                "provider_recovery_loop_failed",
                provider_exception_type=type(exc).__name__,
                provider_exception_message=str(exc),
            )
        await asyncio.sleep(_provider_recovery_sleep_seconds())


def ensure_provider_recovery_task() -> None:
    global _RECOVERY_TASK

    if _RECOVERY_TASK is not None and not _RECOVERY_TASK.done():
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    _RECOVERY_TASK = loop.create_task(_provider_recovery_loop())


async def shutdown_provider_recovery_task() -> None:
    global _RECOVERY_TASK

    if _RECOVERY_TASK is None:
        return

    _RECOVERY_TASK.cancel()
    try:
        await _RECOVERY_TASK
    except asyncio.CancelledError:
        pass
    finally:
        _RECOVERY_TASK = None


def request_provider_recovery() -> bool:
    if PROVIDER_STATE["ready"] or _cooldown_active():
        return False

    ensure_provider_recovery_task()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return True

    if _LAST_RECOVERY_ATTEMPT_AT is None or (_utc_now() - _LAST_RECOVERY_ATTEMPT_AT).total_seconds() >= DEFAULT_PROVIDER_MIN_RETRY_SECONDS:
        loop.create_task(validate_provider_startup())
    return True


def _build_validation_result(
    *,
    configured: bool,
    ready: bool,
    active_provider: str | None,
    selected_model: str | None,
    status: str,
    error_category: str | None,
    discovered_models: list[dict[str, Any]],
    candidate_models_count: int,
    rejected_models_count: int,
    validated_models_count: int,
    failed_validation_models_count: int,
    selected_model_validation_status: str,
    failed_model_reasons: list[dict[str, str]],
    model_selection_strategy: str,
    provider_failover_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "configured": configured,
        "ready": ready,
        "active_provider": active_provider,
        "fallback_provider": "openrouter" if active_provider == "gemini" and _openrouter_configured() else "academic_fallback_engine",
        "provider_failover_reason": provider_failover_reason,
        "selected_model": selected_model,
        "status": status,
        "error_category": error_category,
        "discovered_models": discovered_models,
        "candidate_models_count": candidate_models_count,
        "rejected_models_count": rejected_models_count,
        "validated_models_count": validated_models_count,
        "failed_validation_models_count": failed_validation_models_count,
        "selected_model_validation_status": selected_model_validation_status,
        "failed_model_reasons": failed_model_reasons,
        "model_selection_strategy": model_selection_strategy,
        "gemini_provider_ready": active_provider == "gemini" and ready,
        "openrouter_provider_ready": active_provider == "openrouter" and ready,
    }


async def _validate_gemini_provider() -> dict[str, Any]:
    if _cooldown_active():
        return _build_validation_result(
            configured=bool(os.getenv("GEMINI_API_KEY", "").strip()),
            ready=False,
            active_provider=None,
            selected_model=None,
            status="cooldown",
            error_category="quota_exceeded",
            discovered_models=[],
            candidate_models_count=0,
            rejected_models_count=0,
            validated_models_count=0,
            failed_validation_models_count=0,
            selected_model_validation_status="not_validated",
            failed_model_reasons=[],
            model_selection_strategy="gemini_cooldown",
        )

    try:
        _get_api_key()
        _build_client()
    except ScholrGenerationError as exc:
        return _build_validation_result(
            configured=False,
            ready=False,
            active_provider=None,
            selected_model=None,
            status="not_configured",
            error_category=exc.category,
            discovered_models=[],
            candidate_models_count=0,
            rejected_models_count=0,
            validated_models_count=0,
            failed_validation_models_count=0,
            selected_model_validation_status="not_validated",
            failed_model_reasons=[],
            model_selection_strategy="gemini_not_configured",
        )

    try:
        discovered_models = _discover_models()
    except Exception as exc:
        classified = _classify_provider_error(exc)
        log_event(
            logger,
            "provider_model_discovery_failed",
            provider_name="gemini",
            auth_configured=True,
            provider_exception_type=type(exc).__name__,
            provider_exception_message=str(exc),
            error_category=classified.category,
        )
        return _build_validation_result(
            configured=True,
            ready=False,
            active_provider=None,
            selected_model=None,
            status="not_ready",
            error_category=classified.category,
            discovered_models=[],
            candidate_models_count=0,
            rejected_models_count=0,
            validated_models_count=0,
            failed_validation_models_count=0,
            selected_model_validation_status="not_validated",
            failed_model_reasons=[],
            model_selection_strategy="gemini_discovery_failed",
        )

    selection = _select_candidate_models(CONFIGURED_MODEL_NAME, discovered_models)
    candidates = selection["candidates"]
    if not candidates:
        return _build_validation_result(
            configured=True,
            ready=False,
            active_provider=None,
            selected_model=None,
            status="not_ready",
            error_category="no_supported_generation_model",
            discovered_models=discovered_models,
            candidate_models_count=0,
            rejected_models_count=len(selection["rejected_models"]),
            validated_models_count=0,
            failed_validation_models_count=0,
            selected_model_validation_status="not_validated",
            failed_model_reasons=[],
            model_selection_strategy=selection["strategy"],
        )

    failed_model_reasons: list[dict[str, str]] = []
    for candidate in candidates:
        try:
            log_event(logger, "model_probe_started", provider_name="gemini", model_name=candidate, stage="startup_probe")
            await _probe_model_generation(candidate)
            log_event(logger, "model_probe_success", provider_name="gemini", model_name=candidate, stage="startup_probe")
            return _build_validation_result(
                configured=True,
                ready=True,
                active_provider="gemini",
                selected_model=candidate,
                status="ready",
                error_category=None,
                discovered_models=discovered_models,
                candidate_models_count=len(candidates),
                rejected_models_count=len(selection["rejected_models"]),
                validated_models_count=1,
                failed_validation_models_count=len(failed_model_reasons),
                selected_model_validation_status="validated",
                failed_model_reasons=failed_model_reasons,
                model_selection_strategy=selection["strategy"],
            )
        except ScholrGenerationError as exc:
            failed_model_reasons.append(_build_failed_model_reason(candidate, exc.category))
            _record_provider_failure(exc.category)
            log_event(logger, "model_probe_failed", provider_name="gemini", model_name=candidate, error_category=exc.category, stage="startup_probe")
        except Exception as exc:
            classified = _classify_provider_error(exc)
            failed_model_reasons.append(_build_failed_model_reason(candidate, classified.category))
            _record_provider_failure(classified.category)
            log_event(
                logger,
                "model_probe_failed",
                provider_name="gemini",
                model_name=candidate,
                error_category=classified.category,
                provider_exception_type=type(exc).__name__,
                provider_exception_message=str(exc),
                stage="startup_probe",
            )

    return _build_validation_result(
        configured=True,
        ready=False,
        active_provider=None,
        selected_model=None,
        status="not_ready",
        error_category="no_validated_generation_model",
        discovered_models=discovered_models,
        candidate_models_count=len(candidates),
        rejected_models_count=len(selection["rejected_models"]),
        validated_models_count=0,
        failed_validation_models_count=len(failed_model_reasons),
        selected_model_validation_status="not_validated",
        failed_model_reasons=failed_model_reasons,
        model_selection_strategy=selection["strategy"],
    )


async def _validate_openrouter_provider() -> dict[str, Any]:
    if not _openrouter_configured():
        return _build_validation_result(
            configured=False,
            ready=False,
            active_provider=None,
            selected_model=None,
            status="not_configured",
            error_category="invalid_api_key",
            discovered_models=[],
            candidate_models_count=0,
            rejected_models_count=0,
            validated_models_count=0,
            failed_validation_models_count=0,
            selected_model_validation_status="not_validated",
            failed_model_reasons=[],
            model_selection_strategy="openrouter_not_configured",
        )

    try:
        _get_openrouter_api_key()
        discovered_models = _discover_openrouter_models()
    except ScholrGenerationError as exc:
        return _build_validation_result(
            configured=False,
            ready=False,
            active_provider=None,
            selected_model=None,
            status="not_configured",
            error_category=exc.category,
            discovered_models=[],
            candidate_models_count=0,
            rejected_models_count=0,
            validated_models_count=0,
            failed_validation_models_count=0,
            selected_model_validation_status="not_validated",
            failed_model_reasons=[],
            model_selection_strategy="openrouter_not_configured",
        )
    except Exception as exc:
        classified = _classify_openrouter_error(exc)
        log_event(
            logger,
            "provider_model_discovery_failed",
            provider_name="openrouter",
            auth_configured=True,
            provider_exception_type=type(exc).__name__,
            provider_exception_message=str(exc),
            error_category=classified.category,
        )
        return _build_validation_result(
            configured=True,
            ready=False,
            active_provider=None,
            selected_model=None,
            status="not_ready",
            error_category=classified.category,
            discovered_models=[],
            candidate_models_count=0,
            rejected_models_count=0,
            validated_models_count=0,
            failed_validation_models_count=0,
            selected_model_validation_status="not_validated",
            failed_model_reasons=[],
            model_selection_strategy="openrouter_discovery_failed",
        )

    selection = _select_openrouter_candidate_models(CONFIGURED_OPENROUTER_MODEL_NAME, discovered_models)
    candidates = selection["candidates"]
    if not candidates:
        return _build_validation_result(
            configured=True,
            ready=False,
            active_provider=None,
            selected_model=None,
            status="not_ready",
            error_category="no_supported_generation_model",
            discovered_models=discovered_models,
            candidate_models_count=0,
            rejected_models_count=len(selection["rejected_models"]),
            validated_models_count=0,
            failed_validation_models_count=0,
            selected_model_validation_status="not_validated",
            failed_model_reasons=[],
            model_selection_strategy=selection["strategy"],
        )

    failed_model_reasons: list[dict[str, str]] = []
    for candidate in candidates:
        try:
            log_event(logger, "model_probe_started", provider_name="openrouter", model_name=candidate, stage="startup_probe")
            await _probe_openrouter_model_generation(candidate)
            log_event(logger, "model_probe_success", provider_name="openrouter", model_name=candidate, stage="startup_probe")
            return _build_validation_result(
                configured=True,
                ready=True,
                active_provider="openrouter",
                selected_model=candidate,
                status="ready",
                error_category=None,
                discovered_models=discovered_models,
                candidate_models_count=len(candidates),
                rejected_models_count=len(selection["rejected_models"]),
                validated_models_count=1,
                failed_validation_models_count=len(failed_model_reasons),
                selected_model_validation_status="validated",
                failed_model_reasons=failed_model_reasons,
                model_selection_strategy=selection["strategy"],
                provider_failover_reason=PROVIDER_STATE.get("provider_error_category"),
            )
        except ScholrGenerationError as exc:
            failed_model_reasons.append(_build_failed_model_reason(candidate, exc.category))
            log_event(logger, "model_probe_failed", provider_name="openrouter", model_name=candidate, error_category=exc.category, stage="startup_probe")
        except Exception as exc:
            classified = _classify_openrouter_error(exc)
            failed_model_reasons.append(_build_failed_model_reason(candidate, classified.category))
            log_event(
                logger,
                "model_probe_failed",
                provider_name="openrouter",
                model_name=candidate,
                error_category=classified.category,
                provider_exception_type=type(exc).__name__,
                provider_exception_message=str(exc),
                stage="startup_probe",
            )

    return _build_validation_result(
        configured=True,
        ready=False,
        active_provider=None,
        selected_model=None,
        status="not_ready",
        error_category="no_validated_generation_model",
        discovered_models=discovered_models,
        candidate_models_count=len(candidates),
        rejected_models_count=len(selection["rejected_models"]),
        validated_models_count=0,
        failed_validation_models_count=len(failed_model_reasons),
        selected_model_validation_status="not_validated",
        failed_model_reasons=failed_model_reasons,
        model_selection_strategy=selection["strategy"],
    )


async def validate_provider_startup() -> dict[str, Any]:
    started_at = perf_counter()

    if _validated_state_is_fresh():
        PROVIDER_STATE["startup_validation_time_ms"] = round((perf_counter() - started_at) * 1000)
        return get_provider_status()

    if _LAST_RECOVERY_ATTEMPT_AT and not PROVIDER_STATE["ready"]:
        seconds_since_last_attempt = (_utc_now() - _LAST_RECOVERY_ATTEMPT_AT).total_seconds()
        if seconds_since_last_attempt < DEFAULT_PROVIDER_MIN_RETRY_SECONDS:
            return get_provider_status()

    _mark_recovery_attempt_started()
    gemini_result = await _validate_gemini_provider()
    recovered_from_degraded = _was_degraded_before_success()

    if gemini_result["ready"]:
        _update_provider_state(
            configured=True,
            ready=True,
            active_provider="gemini",
            fallback_provider="openrouter" if _openrouter_configured() else "academic_fallback_engine",
            provider_failover_reason=None,
            selected_model=gemini_result["selected_model"],
            status="ready",
            error_category=None,
            discovered_models=gemini_result["discovered_models"],
            candidate_models_count=gemini_result["candidate_models_count"],
            rejected_models_count=gemini_result["rejected_models_count"],
            validated_models_count=gemini_result["validated_models_count"],
            failed_validation_models_count=gemini_result["failed_validation_models_count"],
            selected_model_validation_status=gemini_result["selected_model_validation_status"],
            failed_model_reasons=gemini_result["failed_model_reasons"],
            quota_failure_count=0,
            last_successful_generation_timestamp=_utc_timestamp(),
            provider_recovery_state="active",
            model_selection_strategy=gemini_result["model_selection_strategy"],
            startup_validation_time_ms=round((perf_counter() - started_at) * 1000),
            last_validated_timestamp=_utc_timestamp(),
            gemini_provider_ready=True,
            openrouter_provider_ready=False,
        )
        log_event(
            logger,
            "final_validated_model_selected",
            provider_name="gemini",
            model_name=gemini_result["selected_model"],
            stage="startup_probe",
            available_models_count=len(gemini_result["discovered_models"]),
            candidate_models_count=gemini_result["candidate_models_count"],
            failed_validation_models_count=gemini_result["failed_validation_models_count"],
            model_selection_strategy=gemini_result["model_selection_strategy"],
        )
        if recovered_from_degraded:
            log_event(
                logger,
                "provider_recovery_success",
                provider_name="gemini",
                model_name=gemini_result["selected_model"],
                provider_recovery_attempts=PROVIDER_STATE["provider_recovery_attempts"],
                quota_failure_count=PROVIDER_STATE["quota_failure_count"],
                stage="startup_probe",
            )
        return get_provider_status()

    openrouter_result = await _validate_openrouter_provider()
    if openrouter_result["ready"]:
        _update_provider_state(
            configured=True,
            ready=True,
            active_provider="openrouter",
            fallback_provider="academic_fallback_engine",
            provider_failover_reason=gemini_result["error_category"],
            selected_model=openrouter_result["selected_model"],
            status="ready",
            error_category=None,
            discovered_models=openrouter_result["discovered_models"],
            candidate_models_count=openrouter_result["candidate_models_count"],
            rejected_models_count=openrouter_result["rejected_models_count"],
            validated_models_count=openrouter_result["validated_models_count"],
            failed_validation_models_count=openrouter_result["failed_validation_models_count"],
            selected_model_validation_status=openrouter_result["selected_model_validation_status"],
            failed_model_reasons=openrouter_result["failed_model_reasons"],
            quota_failure_count=PROVIDER_STATE["quota_failure_count"],
            last_successful_generation_timestamp=_utc_timestamp(),
            provider_recovery_state="active",
            model_selection_strategy=openrouter_result["model_selection_strategy"],
            startup_validation_time_ms=round((perf_counter() - started_at) * 1000),
            last_validated_timestamp=_utc_timestamp(),
            gemini_provider_ready=False,
            openrouter_provider_ready=True,
        )
        log_event(
            logger,
            "final_validated_model_selected",
            provider_name="openrouter",
            model_name=openrouter_result["selected_model"],
            stage="startup_probe",
            available_models_count=len(openrouter_result["discovered_models"]),
            candidate_models_count=openrouter_result["candidate_models_count"],
            failed_validation_models_count=openrouter_result["failed_validation_models_count"],
            model_selection_strategy=openrouter_result["model_selection_strategy"],
            provider_failover_reason=gemini_result["error_category"],
        )
        if recovered_from_degraded:
            log_event(
                logger,
                "provider_recovery_success",
                provider_name="openrouter",
                model_name=openrouter_result["selected_model"],
                provider_recovery_attempts=PROVIDER_STATE["provider_recovery_attempts"],
                quota_failure_count=PROVIDER_STATE["quota_failure_count"],
                stage="startup_probe",
            )
        return get_provider_status()

    final_error_category = gemini_result["error_category"] or openrouter_result["error_category"] or "no_validated_generation_model"
    final_status = "cooldown" if gemini_result["status"] == "cooldown" else "not_ready"
    final_strategy = (
        f"{gemini_result['model_selection_strategy']} -> {openrouter_result['model_selection_strategy']}"
    )
    _update_provider_state(
        configured=bool(os.getenv("GEMINI_API_KEY", "").strip()) or _openrouter_configured(),
        ready=False,
        active_provider=None,
        fallback_provider="academic_fallback_engine",
        provider_failover_reason=final_error_category,
        selected_model=None,
        status=final_status,
        error_category=final_error_category,
        discovered_models=gemini_result["discovered_models"] or openrouter_result["discovered_models"],
        candidate_models_count=max(gemini_result["candidate_models_count"], openrouter_result["candidate_models_count"]),
        rejected_models_count=gemini_result["rejected_models_count"] + openrouter_result["rejected_models_count"],
        validated_models_count=0,
        failed_validation_models_count=gemini_result["failed_validation_models_count"] + openrouter_result["failed_validation_models_count"],
        selected_model_validation_status="not_validated",
        failed_model_reasons=[*gemini_result["failed_model_reasons"], *openrouter_result["failed_model_reasons"]],
        provider_recovery_state="cooldown" if final_status == "cooldown" else "degraded",
        model_selection_strategy=final_strategy,
        startup_validation_time_ms=round((perf_counter() - started_at) * 1000),
        last_validated_timestamp=None,
        gemini_provider_ready=False,
        openrouter_provider_ready=False,
    )
    return get_provider_status()


def resolve_model_name(requested_model_name: str) -> str:
    preferred = PROVIDER_STATE["selected_model"]
    if PROVIDER_STATE["ready"] and preferred:
        return preferred
    requested = _normalize_model_name(requested_model_name)
    return requested or _normalize_model_name(CONFIGURED_MODEL_NAME) or STRICT_MODEL_PRIORITY[0]


async def _stream_gemini_model_response(
    *,
    model_name: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> AsyncIterator[str]:
    client = _build_client()
    stream = await asyncio.wait_for(
        client.aio.models.generate_content_stream(
            model=model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ),
        ),
        timeout=DEFAULT_CONNECT_TIMEOUT_SECONDS,
    )

    stream_deadline = perf_counter() + DEFAULT_PROVIDER_RUNTIME_MAX_SECONDS
    async for chunk in stream:
        if perf_counter() >= stream_deadline:
            raise ScholrGenerationError(
                "Gemini did not finish responding in time. Please try again.",
                retryable=True,
                category="provider_timeout",
            )

        text = _extract_chunk_text(chunk)
        if text:
            yield text


async def _stream_openrouter_model_response(
    *,
    model_name: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> AsyncIterator[str]:
    text = await _openrouter_generate_text(
        model_name=model_name,
        prompt=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    async for chunk in _yield_text_chunks(text):
        yield chunk


async def _get_openrouter_runtime_candidate() -> str | None:
    result = await _validate_openrouter_provider()
    if result["ready"]:
        return result["selected_model"]
    return None


async def stream_gemini_response(
    *,
    model_name: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> AsyncIterator[str]:
    if not PROVIDER_STATE["ready"]:
        await validate_provider_startup()
        if not PROVIDER_STATE["ready"]:
            raise ScholrGenerationError(
                "Scholr could not validate a live generation model right now.",
                retryable=True,
                category=PROVIDER_STATE["provider_error_category"] or "no_validated_generation_model",
            )
    active_provider = PROVIDER_STATE["active_provider"]
    selected_model = PROVIDER_STATE["selected_model"] if PROVIDER_STATE["ready"] else None
    attempts: list[tuple[str, str, str | None]] = []

    if active_provider and selected_model:
        attempts.append((active_provider, selected_model, None))
        if active_provider == "gemini" and _openrouter_configured():
            openrouter_candidate = await _get_openrouter_runtime_candidate()
            if openrouter_candidate:
                attempts.append(("openrouter", openrouter_candidate, "gemini_unavailable"))
    else:
        fallback_model = resolve_model_name(model_name)
        attempts.append(("gemini", fallback_model, None))

    last_error: ScholrGenerationError | None = None

    for index, (provider_name, candidate, failover_reason) in enumerate(attempts):
        chunks_received = 0
        try:
            log_event(
                logger,
                "provider_model_selected",
                active_provider=provider_name,
                fallback_provider="openrouter" if provider_name == "gemini" and index + 1 < len(attempts) else "academic_fallback_engine",
                model_name=candidate,
                provider_failover_reason=failover_reason,
                stage="generation_open",
            )
            generator = (
                _stream_gemini_model_response(
                    model_name=candidate,
                    prompt=prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
                if provider_name == "gemini"
                else _stream_openrouter_model_response(
                    model_name=candidate,
                    prompt=prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
            )

            async for chunk in generator:
                chunks_received += 1
                yield chunk
        except ScholrGenerationError as exc:
            last_error = exc
        except Exception as exc:
            last_error = _classify_provider_error(exc) if provider_name == "gemini" else _classify_openrouter_error(exc)

        if last_error:
            _record_provider_failure(last_error.category)
            log_event(
                logger,
                "provider_generation_failed",
                active_provider=provider_name,
                model_name=candidate,
                error_category=last_error.category,
                provider_failover_reason=failover_reason,
                streamed_chunks=chunks_received,
                stage="stream",
            )
            if _should_try_fallback(last_error) and index < len(attempts) - 1:
                next_provider, next_model, _ = attempts[index + 1]
                log_event(
                    logger,
                    "provider_model_fallback",
                    active_provider=provider_name,
                    attempted_model=candidate,
                    fallback_provider=next_provider,
                    fallback_model=next_model,
                    provider_failover_reason=last_error.category,
                )
                continue
            raise last_error

        if chunks_received == 0:
            last_error = ScholrGenerationError(
                "Scholr did not receive any usable text from the provider for this prompt. Please try rephrasing it.",
                retryable=True,
                category="empty_response",
            )
            log_event(
                logger,
                "provider_generation_failed",
                active_provider=provider_name,
                model_name=candidate,
                error_category=last_error.category,
                streamed_chunks=0,
                stage="stream",
            )
            if index < len(attempts) - 1:
                next_provider, next_model, _ = attempts[index + 1]
                log_event(
                    logger,
                    "provider_model_fallback",
                    active_provider=provider_name,
                    attempted_model=candidate,
                    fallback_provider=next_provider,
                    fallback_model=next_model,
                    provider_failover_reason=last_error.category,
                )
                continue
            raise last_error

        _record_provider_success(candidate, provider_name, failover_reason=failover_reason)
        PROVIDER_STATE.update(
            {
                "candidate_models_count": max(1, PROVIDER_STATE["candidate_models_count"]),
                "selected_model_validation_status": "validated",
            }
        )
        log_event(
            logger,
            "provider_generation_success",
            active_provider=provider_name,
            model_name=candidate,
            provider_failover_reason=failover_reason,
            streamed_chunks=chunks_received,
        )
        return

    raise last_error or ScholrGenerationError(
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
    started_at = perf_counter()
    provider_status = await validate_provider_startup()
    result: dict[str, Any] = {
        "provider_configured": provider_status["provider_configured"],
        "provider_ready": provider_status["provider_ready"],
        "active_provider": provider_status["active_provider"],
        "fallback_provider": provider_status["fallback_provider"],
        "provider_failover_reason": provider_status["provider_failover_reason"],
        "provider_status": provider_status["provider_status"],
        "selected_model": provider_status["selected_model"],
        "model_name": provider_status["model_name"],
        "provider_error_category": provider_status["provider_error_category"],
        "provider_sdk_version": provider_status["provider_sdk_version"],
        "available_models_count": provider_status["available_models_count"],
        "available_models_sample": provider_status["available_models_sample"],
        "candidate_models_count": provider_status["candidate_models_count"],
        "rejected_models_count": provider_status["rejected_models_count"],
        "validated_models_count": provider_status["validated_models_count"],
        "failed_validation_models_count": provider_status["failed_validation_models_count"],
        "selected_model_validation_status": provider_status["selected_model_validation_status"],
        "failed_model_reasons": provider_status["failed_model_reasons"],
        "quota_failure_count": provider_status["quota_failure_count"],
        "last_successful_generation_timestamp": provider_status["last_successful_generation_timestamp"],
        "provider_recovery_state": provider_status["provider_recovery_state"],
        "provider_recovery_attempts": provider_status["provider_recovery_attempts"],
        "quota_cooldown_remaining_seconds": provider_status["quota_cooldown_remaining_seconds"],
        "model_selection_strategy": provider_status["model_selection_strategy"],
        "startup_validation_time_ms": provider_status["startup_validation_time_ms"],
        "provider_tier_strategy": provider_status["provider_tier_strategy"],
        "gemini_provider_ready": provider_status["gemini_provider_ready"],
        "openrouter_provider_ready": provider_status["openrouter_provider_ready"],
        "prompt": prompt,
        "last_validated_timestamp": provider_status["last_validated_timestamp"],
    }

    if not provider_status["provider_ready"]:
        result["success"] = False
        result["latency_ms"] = round((perf_counter() - started_at) * 1000)
        return result

    try:
        collected: list[str] = []
        async for chunk in stream_gemini_response(
            model_name=provider_status["selected_model"] or STRICT_MODEL_PRIORITY[0],
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
                "latency_ms": round((perf_counter() - started_at) * 1000),
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
                "latency_ms": round((perf_counter() - started_at) * 1000),
            }
        )
        return result
