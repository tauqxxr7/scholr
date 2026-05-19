import asyncio
import logging
import os
from time import perf_counter
from collections.abc import AsyncIterator
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

from core.logging_utils import log_event

load_dotenv()

DEFAULT_CONNECT_TIMEOUT_SECONDS = 25
DEFAULT_STREAM_CHUNK_TIMEOUT_SECONDS = 45
DEFAULT_PROVIDER_PROBE_TIMEOUT_SECONDS = 18
DEFAULT_PROVIDER_RUNTIME_MAX_SECONDS = 40
MODEL_CANDIDATES = ("gemini-1.5-flash", "gemini-1.5-pro")
CONFIGURED_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "").strip()
PROVIDER_PROBE_PROMPT = "Reply with exactly OK."
PROVIDER_PROBE_MAX_OUTPUT_TOKENS = 8

PROVIDER_STATE: dict[str, Any] = {
    "configured": False,
    "ready": False,
    "model_name": None,
    "error_category": None,
    "sdk_version": getattr(genai, "__version__", "unknown"),
    "status": "unknown",
}
logger = logging.getLogger("scholr.provider")


class ScholrGenerationError(Exception):
    def __init__(self, user_message: str, *, retryable: bool = True, category: str = "provider"):
        super().__init__(user_message)
        self.user_message = user_message
        self.retryable = retryable
        self.category = category


def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ScholrGenerationError(
            "Scholr is not configured with a Gemini API key yet. Add a valid key in backend/.env and restart the backend.",
            retryable=False,
            category="invalid_api_key",
        )

    return api_key


def _preferred_models() -> tuple[str, ...]:
    if CONFIGURED_MODEL_NAME:
        return (CONFIGURED_MODEL_NAME, *[model for model in MODEL_CANDIDATES if model != CONFIGURED_MODEL_NAME])
    return MODEL_CANDIDATES


def _candidate_models(requested_model_name: str | None = None) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []

    for candidate in (requested_model_name, *_preferred_models()):
        normalized = (candidate or "").strip()
        if normalized and normalized not in seen:
            ordered.append(normalized)
            seen.add(normalized)

    return tuple(ordered)


def _build_model(model_name: str):
    genai.configure(api_key=_get_api_key())
    return genai.GenerativeModel(model_name)


def _classify_provider_error(exc: Exception) -> ScholrGenerationError:
    message = str(exc).lower()

    if isinstance(exc, asyncio.TimeoutError):
        return ScholrGenerationError(
            "Scholr took too long to get a response from Gemini. Please try again in a moment.",
            retryable=True,
            category="provider_timeout",
        )

    if "api key" in message or "permission" in message or "unauth" in message:
        return ScholrGenerationError(
            "The Gemini API key looks missing, invalid, or does not have access to this model. Update backend/.env and restart the backend.",
            retryable=False,
            category="invalid_api_key",
        )

    if "quota" in message or "rate limit" in message or "resource exhausted" in message:
        return ScholrGenerationError(
            "Gemini is temporarily rate limited or out of quota for this project. Please wait a bit and try again.",
            retryable=True,
            category="quota_exceeded",
        )

    if "model" in message and ("not found" in message or "supported" in message or "deprecated" in message):
        return ScholrGenerationError(
            "This Gemini model is unavailable for the current project. Switch to an active model and restart the backend.",
            retryable=False,
            category="invalid_model",
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

    if (
        "service unavailable" in message
        or "temporarily unavailable" in message
        or "internal" in message
        or "bad gateway" in message
        or "unavailable" in message
        or "connection reset" in message
        or "connection aborted" in message
        or "remote protocol" in message
        or "500" in message
        or "502" in message
        or "503" in message
        or "504" in message
    ):
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


async def _probe_model_generation(model_name: str) -> None:
    model = _build_model(model_name)
    response = await asyncio.wait_for(
        model.generate_content_async(
            PROVIDER_PROBE_PROMPT,
            generation_config=genai.GenerationConfig(
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


def get_provider_status() -> dict[str, Any]:
    return {
        "provider_configured": PROVIDER_STATE["configured"],
        "provider_ready": PROVIDER_STATE["ready"],
        "model_name": PROVIDER_STATE["model_name"],
        "provider_status": PROVIDER_STATE["status"],
        "provider_error_category": PROVIDER_STATE["error_category"],
        "provider_sdk_version": PROVIDER_STATE["sdk_version"],
    }


async def validate_provider_startup() -> dict[str, Any]:
    try:
        api_key = _get_api_key()
    except ScholrGenerationError as exc:
        PROVIDER_STATE.update(
            {
                "configured": False,
                "ready": False,
                "status": "not_configured",
                "error_category": exc.category,
            }
        )
        return get_provider_status()

    genai.configure(api_key=api_key)

    try:
        available = {
            model.name.replace("models/", ""): model
            for model in genai.list_models()
            if "generateContent" in getattr(model, "supported_generation_methods", [])
        }
    except Exception as exc:
        classified = _classify_provider_error(exc)
        PROVIDER_STATE.update(
            {
                "configured": True,
                "ready": False,
                "status": "not_ready",
                "error_category": classified.category,
            }
        )
        return get_provider_status()

    for candidate in _candidate_models():
        if candidate in available:
            try:
                await _probe_model_generation(candidate)
            except ScholrGenerationError as exc:
                PROVIDER_STATE.update(
                    {
                        "configured": True,
                        "ready": False,
                        "model_name": candidate,
                        "status": "not_ready",
                        "error_category": exc.category,
                    }
                )
                log_event(
                    logger,
                    "provider_probe_failed",
                    model_name=candidate,
                    error_category=exc.category,
                )
                continue
            except Exception as exc:
                classified = _classify_provider_error(exc)
                PROVIDER_STATE.update(
                    {
                        "configured": True,
                        "ready": False,
                        "model_name": candidate,
                        "status": "not_ready",
                        "error_category": classified.category,
                    }
                )
                log_event(
                    logger,
                    "provider_probe_failed",
                    model_name=candidate,
                    error_category=classified.category,
                )
                continue

            PROVIDER_STATE.update(
                {
                    "configured": True,
                    "ready": True,
                    "model_name": candidate,
                    "status": "ready",
                    "error_category": None,
                }
            )
            log_event(
                logger,
                "provider_model_selected",
                model_name=candidate,
                stage="startup_probe",
            )
            return get_provider_status()

    PROVIDER_STATE.update(
        {
            "configured": True,
            "ready": False,
            "status": "not_ready",
            "error_category": "invalid_model",
        }
    )
    return get_provider_status()


def resolve_model_name(requested_model_name: str) -> str:
    preferred = PROVIDER_STATE["model_name"]
    if PROVIDER_STATE["ready"] and preferred:
        return preferred
    return requested_model_name or _preferred_models()[0]


async def stream_gemini_response(
    *,
    model_name: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> AsyncIterator[str]:
    last_error: ScholrGenerationError | None = None
    candidates = _candidate_models(resolve_model_name(model_name))

    for candidate in candidates:
        last_error = None
        try:
            started_at = perf_counter()
            model = _build_model(candidate)
            log_event(
                logger,
                "provider_model_selected",
                model_name=candidate,
                stage="generation_open",
            )
            response = await asyncio.wait_for(
                model.generate_content_async(
                    prompt,
                    stream=True,
                    generation_config=genai.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_output_tokens,
                    ),
                ),
                timeout=DEFAULT_CONNECT_TIMEOUT_SECONDS,
            )
            log_event(
                logger,
                "provider_generation_opened",
                model_name=candidate,
                duration_ms=round((perf_counter() - started_at) * 1000),
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
            )
            if _should_try_fallback(last_error) and candidate != candidates[-1]:
                log_event(
                    logger,
                    "provider_model_fallback",
                    attempted_model=candidate,
                    fallback_model=candidates[candidates.index(candidate) + 1],
                    error_category=last_error.category,
                )
                continue
            raise last_error

        chunks_received = 0
        iterator = response.__aiter__()
        stream_deadline = perf_counter() + DEFAULT_PROVIDER_RUNTIME_MAX_SECONDS

        while True:
            remaining_seconds = stream_deadline - perf_counter()
            if remaining_seconds <= 0:
                last_error = ScholrGenerationError(
                    "Gemini did not finish responding in time. Please try again.",
                    retryable=True,
                    category="provider_timeout",
                )
                break

            try:
                chunk = await asyncio.wait_for(
                    anext(iterator),
                    timeout=min(DEFAULT_STREAM_CHUNK_TIMEOUT_SECONDS, remaining_seconds),
                )
            except StopAsyncIteration:
                break
            except ScholrGenerationError as exc:
                last_error = exc
                break
            except Exception as exc:
                last_error = _classify_provider_error(exc)
                break

            text = getattr(chunk, "text", None)
            if not text:
                continue

            chunks_received += 1
            yield text

        if last_error:
            log_event(
                logger,
                "provider_stream_failed",
                model_name=candidate,
                error_category=last_error.category,
                streamed_chunks=chunks_received,
            )
            if _should_try_fallback(last_error) and candidate != candidates[-1]:
                log_event(
                    logger,
                    "provider_model_fallback",
                    attempted_model=candidate,
                    fallback_model=candidates[candidates.index(candidate) + 1],
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
                "provider_stream_failed",
                model_name=candidate,
                error_category=last_error.category,
                streamed_chunks=0,
            )
            if _should_try_fallback(last_error) and candidate != candidates[-1]:
                log_event(
                    logger,
                    "provider_model_fallback",
                    attempted_model=candidate,
                    fallback_model=candidates[candidates.index(candidate) + 1],
                    error_category=last_error.category,
                    streamed_chunks=0,
                )
                continue
            raise last_error

        PROVIDER_STATE.update(
            {
                "configured": True,
                "ready": True,
                "model_name": candidate,
                "status": "ready",
                "error_category": None,
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


async def run_provider_smoke_test(prompt: str = PROVIDER_PROBE_PROMPT) -> dict[str, Any]:
    provider_status = await validate_provider_startup()
    result: dict[str, Any] = {
        "provider_configured": provider_status["provider_configured"],
        "provider_ready": provider_status["provider_ready"],
        "provider_status": provider_status["provider_status"],
        "model_name": provider_status["model_name"],
        "provider_error_category": provider_status["provider_error_category"],
        "provider_sdk_version": provider_status["provider_sdk_version"],
        "prompt": prompt,
    }

    if not provider_status["provider_ready"]:
        result["success"] = False
        return result

    try:
        collected: list[str] = []
        async for chunk in stream_gemini_response(
            model_name=provider_status["model_name"] or _preferred_models()[0],
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
