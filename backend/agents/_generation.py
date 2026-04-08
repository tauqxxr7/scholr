import asyncio
import os
from collections.abc import AsyncIterator

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CONNECT_TIMEOUT_SECONDS = 25
DEFAULT_STREAM_CHUNK_TIMEOUT_SECONDS = 45


class ScholrGenerationError(Exception):
    def __init__(self, user_message: str, *, retryable: bool = True):
        super().__init__(user_message)
        self.user_message = user_message
        self.retryable = retryable


def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ScholrGenerationError(
            "Scholr is not configured with a Gemini API key yet. Add a valid key in backend/.env and restart the backend.",
            retryable=False,
        )

    return api_key


def _build_model(model_name: str):
    genai.configure(api_key=_get_api_key())
    return genai.GenerativeModel(model_name)


def _classify_provider_error(exc: Exception) -> ScholrGenerationError:
    message = str(exc).lower()

    if isinstance(exc, asyncio.TimeoutError):
        return ScholrGenerationError(
            "Scholr took too long to get a response from Gemini. Please try again in a moment.",
            retryable=True,
        )

    if "api key" in message or "permission" in message or "unauth" in message or "invalid argument" in message:
        return ScholrGenerationError(
            "The Gemini API key looks missing, invalid, or does not have access to this model. Update backend/.env and restart the backend.",
            retryable=False,
        )

    if "quota" in message or "rate limit" in message or "resource exhausted" in message:
        return ScholrGenerationError(
            "Gemini is temporarily rate limited or out of quota for this project. Please wait a bit and try again.",
            retryable=True,
        )

    if "model" in message and ("not found" in message or "supported" in message or "deprecated" in message):
        return ScholrGenerationError(
            "This Gemini model is unavailable for the current project. Switch to an active model and restart the backend.",
            retryable=False,
        )

    if "deadline" in message or "timed out" in message or "timeout" in message:
        return ScholrGenerationError(
            "Gemini did not respond in time. Please retry once the connection is stable.",
            retryable=True,
        )

    return ScholrGenerationError(
        "Scholr could not generate a response right now. Please try again.",
        retryable=True,
    )


async def stream_gemini_response(
    *,
    model_name: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> AsyncIterator[str]:
    try:
        model = _build_model(model_name)
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
        )
