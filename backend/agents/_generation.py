import asyncio
import os
from collections.abc import AsyncIterator
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CONNECT_TIMEOUT_SECONDS = 25
DEFAULT_STREAM_CHUNK_TIMEOUT_SECONDS = 45
MODEL_CANDIDATES = ("gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro")
CONFIGURED_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "").strip()

PROVIDER_STATE: dict[str, Any] = {
    "configured": False,
    "ready": False,
    "model_name": CONFIGURED_MODEL_NAME or MODEL_CANDIDATES[0],
    "error_category": None,
}


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
            category="configuration",
        )

    return api_key


def _preferred_models() -> tuple[str, ...]:
    if CONFIGURED_MODEL_NAME:
        return (CONFIGURED_MODEL_NAME, *[model for model in MODEL_CANDIDATES if model != CONFIGURED_MODEL_NAME])
    return MODEL_CANDIDATES


def _build_model(model_name: str):
    genai.configure(api_key=_get_api_key())
    return genai.GenerativeModel(model_name)


def _classify_provider_error(exc: Exception) -> ScholrGenerationError:
    message = str(exc).lower()

    if isinstance(exc, asyncio.TimeoutError):
        return ScholrGenerationError(
            "Scholr took too long to get a response from Gemini. Please try again in a moment.",
            retryable=True,
            category="timeout",
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


def get_provider_status() -> dict[str, Any]:
    return {
        "provider_configured": PROVIDER_STATE["configured"],
        "provider_ready": PROVIDER_STATE["ready"],
        "model_name": PROVIDER_STATE["model_name"],
        "provider_error_category": PROVIDER_STATE["error_category"],
    }


def validate_provider_startup() -> dict[str, Any]:
    try:
        api_key = _get_api_key()
    except ScholrGenerationError as exc:
        PROVIDER_STATE.update(
            {
                "configured": False,
                "ready": False,
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
                "error_category": classified.category,
            }
        )
        return get_provider_status()

    for candidate in _preferred_models():
        if candidate in available:
            PROVIDER_STATE.update(
                {
                    "configured": True,
                    "ready": True,
                    "model_name": candidate,
                    "error_category": None,
                }
            )
            return get_provider_status()

    PROVIDER_STATE.update(
        {
            "configured": True,
            "ready": False,
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
    try:
        model = _build_model(resolve_model_name(model_name))
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
    except ScholrGenerationError:
        raise
    except Exception as exc:
        raise _classify_provider_error(exc) from exc

    chunks_received = 0
    iterator = response.__aiter__()

    while True:
        try:
            chunk = await asyncio.wait_for(
                anext(iterator),
                timeout=DEFAULT_STREAM_CHUNK_TIMEOUT_SECONDS,
            )
        except StopAsyncIteration:
            break
        except ScholrGenerationError:
            raise
        except Exception as exc:
            raise _classify_provider_error(exc) from exc

        text = getattr(chunk, "text", None)
        if not text:
            continue

        chunks_received += 1
        yield text

    if chunks_received == 0:
        raise ScholrGenerationError(
            "Scholr did not receive any usable text from Gemini for this prompt. Please try rephrasing it.",
            retryable=True,
            category="empty_response",
        )
