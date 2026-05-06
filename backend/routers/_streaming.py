import json
import logging
from collections.abc import AsyncIterator, Callable
from time import perf_counter
from typing import Any

from fastapi import Request
from fastapi.responses import StreamingResponse

from agents._generation import ScholrGenerationError
from core.logging_utils import log_event

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


async def stream_text_chunks(text: str, chunk_size: int = 180) -> AsyncIterator[str]:
    for start in range(0, len(text), chunk_size):
        yield text[start : start + chunk_size]


def build_sse_response(
    *,
    generator: AsyncIterator[str],
    save_history: Callable[[str], Any] | None = None,
    empty_message: str = "Scholr did not generate any output for this prompt. Please try rephrasing it.",
    request: Request | None = None,
    module: str,
    source: str = "live",
) -> StreamingResponse:
    async def event_stream():
        full_response: list[str] = []
        request_id = getattr(getattr(request, "state", None), "request_id", None)
        started_at = perf_counter()

        log_event(
            logger,
            "generation_started",
            module=module,
            request_id=request_id,
            source=source,
        )

        try:
            async for chunk in generator:
                if not chunk:
                    continue

                full_response.append(chunk)
                yield _sse_event({"type": "chunk", "chunk": chunk})
        except ScholrGenerationError as exc:
            log_event(
                logger,
                "generation_failed",
                module=module,
                request_id=request_id,
                source=source,
                duration_ms=round((perf_counter() - started_at) * 1000),
                success=False,
                error_category=exc.category,
                retryable=exc.retryable,
            )
            yield _sse_event(
                {
                    "type": "error",
                    "message": exc.user_message,
                    "retryable": exc.retryable,
                    "category": exc.category,
                }
            )
        except Exception:
            log_event(
                logger,
                "generation_failed",
                module=module,
                request_id=request_id,
                source=source,
                duration_ms=round((perf_counter() - started_at) * 1000),
                success=False,
                error_category="unexpected",
            )
            logger.exception("Unexpected error while streaming module response")
            yield _sse_event(
                {
                    "type": "error",
                    "message": "Scholr hit an unexpected issue while generating this answer. Please try again.",
                    "retryable": True,
                    "category": "unexpected",
                }
            )
        else:
            if not full_response:
                log_event(
                    logger,
                    "generation_completed",
                    module=module,
                    request_id=request_id,
                    source=source,
                    duration_ms=round((perf_counter() - started_at) * 1000),
                    success=True,
                    response_length=0,
                )
                yield _sse_event(
                    {
                        "type": "empty",
                        "message": empty_message,
                    }
                )
            else:
                response_text = "".join(full_response)
                log_event(
                    logger,
                    "generation_completed",
                    module=module,
                    request_id=request_id,
                    source=source,
                    duration_ms=round((perf_counter() - started_at) * 1000),
                    success=True,
                    response_length=len(response_text),
                )
        finally:
            if full_response and save_history:
                response_text = "".join(full_response)
                try:
                    save_history(response_text)
                    log_event(
                        logger,
                        "history_saved",
                        module=module,
                        request_id=request_id,
                        source=source,
                        response_length=len(response_text),
                    )
                except Exception:
                    log_event(
                        logger,
                        "history_save_failed",
                        module=module,
                        request_id=request_id,
                        source=source,
                        response_length=len(response_text),
                    )
                    logger.exception(
                        "Search history could not be saved. First response preview: %s",
                        _safe_history_summary(response_text),
                    )

            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
