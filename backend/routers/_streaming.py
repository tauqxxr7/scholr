import json
import logging
from collections.abc import AsyncIterator, Callable
from typing import Any

from fastapi.responses import StreamingResponse

from agents._generation import ScholrGenerationError

logger = logging.getLogger(__name__)

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _safe_history_summary(text: str) -> str:
    cleaned = text.strip()
    return cleaned[:160] if cleaned else ""


def build_sse_response(
    *,
    generator: AsyncIterator[str],
    save_history: Callable[[str], Any] | None = None,
    empty_message: str = "Scholr did not generate any output for this prompt. Please try rephrasing it.",
) -> StreamingResponse:
    async def event_stream():
        full_response: list[str] = []

        try:
            async for chunk in generator:
                if not chunk:
                    continue

                full_response.append(chunk)
                yield _sse_event({"type": "chunk", "chunk": chunk})
        except ScholrGenerationError as exc:
            logger.warning("Generation error: %s", exc.user_message)
            yield _sse_event(
                {
                    "type": "error",
                    "message": exc.user_message,
                    "retryable": exc.retryable,
                }
            )
        except Exception:
            logger.exception("Unexpected error while streaming module response")
            yield _sse_event(
                {
                    "type": "error",
                    "message": "Scholr hit an unexpected issue while generating this answer. Please try again.",
                    "retryable": True,
                }
            )
        else:
            if not full_response:
                yield _sse_event(
                    {
                        "type": "empty",
                        "message": empty_message,
                    }
                )
        finally:
            if full_response and save_history:
                try:
                    save_history("".join(full_response))
                except Exception:
                    logger.exception(
                        "Search history could not be saved. First response preview: %s",
                        _safe_history_summary("".join(full_response)),
                    )

            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
