import asyncio
import json
import logging
from collections.abc import AsyncIterator, Callable
from time import perf_counter
from typing import Any

from fastapi import Request
from fastapi.responses import StreamingResponse

from agents._generation import ScholrGenerationError, get_provider_status
from core.logging_utils import log_event

logger = logging.getLogger(__name__)
STREAM_OBSERVABILITY: dict[str, int] = {
    "stream_interruption_count": 0,
    "partial_stream_recovery_count": 0,
    "first_token_timeout_count": 0,
    "stream_hard_cutoff_count": 0,
}
FIRST_TOKEN_TIMEOUT_SECONDS = 5
STREAM_HARD_CUTOFF_SECONDS = 20
NEXT_CHUNK_TIMEOUT_SECONDS = 8

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _response_mode_payload(source: str) -> dict[str, str]:
    if source == "recovering":
        return {"mode": "recovering", "label": "Provider Recovering"}
    if source == "fallback":
        return {"mode": "fallback", "label": "Fallback Academic Mode"}
    if source == "warm_cache":
        return {"mode": "warm_cache", "label": "Cached Academic Response"}
    if source == "cache":
        return {"mode": "cache", "label": "Cached Academic Response"}
    return {"mode": "ai", "label": "AI Mode"}


def _safe_history_summary(text: str) -> str:
    cleaned = text.strip()
    return cleaned[:160] if cleaned else ""


def get_stream_observability() -> dict[str, int]:
    return dict(STREAM_OBSERVABILITY)


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
    mode: str = "fast",
    source: str = "live",
    cache_hit: bool = False,
    recovery_text: str | None = None,
) -> StreamingResponse:
    async def event_stream():
        full_response: list[str] = []
        request_id = getattr(getattr(request, "state", None), "request_id", None)
        started_at = perf_counter()
        first_token_logged = False
        first_token_ms: int | None = None
        partial_completion = False
        provider_status = get_provider_status()
        provider = str(provider_status.get("active_provider") or provider_status.get("provider_status") or "unknown")
        error_category: str | None = None

        log_event(
            logger,
            "stream_started",
            module=module,
            mode=mode,
            request_id=request_id,
            source=source,
            provider=provider,
            cache_hit=cache_hit,
        )
        log_event(
            logger,
            "generation_started",
            module=module,
            mode=mode,
            request_id=request_id,
            source=source,
        )
        if source in {"fallback", "recovering"}:
            log_event(
                logger,
                "fallback_activated",
                module=module,
                request_id=request_id,
                source=source,
            )
        yield _sse_event({"type": "meta", **_response_mode_payload(source)})

        try:
            iterator = generator.__aiter__()
            while True:
                elapsed = perf_counter() - started_at
                remaining_total = STREAM_HARD_CUTOFF_SECONDS - elapsed
                if remaining_total <= 0:
                    STREAM_OBSERVABILITY["stream_hard_cutoff_count"] += 1
                    if full_response:
                        partial_completion = True
                        yield _sse_event(
                            {
                                "type": "partial",
                                "message": "Answer completed partially. Tap retry for deeper version.",
                                "category": "stream_hard_cutoff",
                            }
                        )
                        break
                    raise ScholrGenerationError(
                        "Scholr took too long to start this answer. Please retry.",
                        retryable=True,
                        category="provider_timeout",
                    )

                next_timeout = min(remaining_total, FIRST_TOKEN_TIMEOUT_SECONDS if not full_response else NEXT_CHUNK_TIMEOUT_SECONDS)
                try:
                    chunk = await asyncio.wait_for(iterator.__anext__(), timeout=next_timeout)
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError as exc:
                    if full_response:
                        partial_completion = True
                        STREAM_OBSERVABILITY["partial_stream_recovery_count"] += 1
                        yield _sse_event(
                            {
                                "type": "partial",
                                "message": "Answer completed partially. Tap retry for deeper version.",
                                "category": "stream_chunk_timeout",
                            }
                        )
                        break
                    STREAM_OBSERVABILITY["first_token_timeout_count"] += 1
                    raise ScholrGenerationError(
                        "Scholr took too long to start this answer. Please retry.",
                        retryable=True,
                        category="first_token_timeout",
                    ) from exc

                if not chunk:
                    continue

                if not first_token_logged:
                    first_token_logged = True
                    first_token_ms = round((perf_counter() - started_at) * 1000)
                    log_event(
                        logger,
                        "first_token_emitted",
                        module=module,
                        mode=mode,
                        request_id=request_id,
                        source=source,
                        first_token_latency_ms=first_token_ms,
                    )
                full_response.append(chunk)
                yield _sse_event({"type": "chunk", "chunk": chunk})
        except ScholrGenerationError as exc:
            error_category = exc.category
            STREAM_OBSERVABILITY["stream_interruption_count"] += 1
            if full_response:
                partial_completion = True
                STREAM_OBSERVABILITY["partial_stream_recovery_count"] += 1
                log_event(
                    logger,
                    "generation_partial_completed",
                    module=module,
                    request_id=request_id,
                    source=source,
                    duration_ms=round((perf_counter() - started_at) * 1000),
                    response_length=len("".join(full_response)),
                    error_category=exc.category,
                )
                yield _sse_event(
                    {
                        "type": "partial",
                        "message": "Answer completed partially. Tap retry for deeper version.",
                        "category": exc.category,
                    }
                )
            elif recovery_text:
                full_response.clear()
                yield _sse_event({"type": "meta", **_response_mode_payload("fallback")})
                async for fallback_chunk in stream_text_chunks(recovery_text):
                    full_response.append(fallback_chunk)
                    yield _sse_event({"type": "chunk", "chunk": fallback_chunk})
                log_event(
                    logger,
                    "generation_completed",
                    module=module,
                    request_id=request_id,
                    source="fallback",
                    duration_ms=round((perf_counter() - started_at) * 1000),
                    success=True,
                    response_length=len("".join(full_response)),
                    error_category=exc.category,
                )
                return
            else:
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
            error_category = "unexpected"
            STREAM_OBSERVABILITY["stream_interruption_count"] += 1
            if full_response:
                partial_completion = True
                STREAM_OBSERVABILITY["partial_stream_recovery_count"] += 1
                log_event(
                    logger,
                    "generation_partial_completed",
                    module=module,
                    request_id=request_id,
                    source=source,
                    duration_ms=round((perf_counter() - started_at) * 1000),
                    response_length=len("".join(full_response)),
                    error_category="unexpected",
                )
                yield _sse_event(
                    {
                        "type": "partial",
                        "message": "Answer completed partially. Tap retry for deeper version.",
                        "category": "unexpected",
                    }
                )
            elif recovery_text:
                full_response.clear()
                yield _sse_event({"type": "meta", **_response_mode_payload("fallback")})
                async for fallback_chunk in stream_text_chunks(recovery_text):
                    full_response.append(fallback_chunk)
                    yield _sse_event({"type": "chunk", "chunk": fallback_chunk})
                log_event(
                    logger,
                    "generation_completed",
                    module=module,
                    request_id=request_id,
                    source="fallback",
                    duration_ms=round((perf_counter() - started_at) * 1000),
                    success=True,
                    response_length=len("".join(full_response)),
                    error_category="unexpected",
                )
                return
            else:
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
                    partial=partial_completion,
                )
        finally:
            response_text_for_metrics = "".join(full_response)
            log_event(
                logger,
                "stream_completed",
                module=module,
                mode=mode,
                first_token_ms=first_token_ms,
                completion_ms=round((perf_counter() - started_at) * 1000),
                output_length=len(response_text_for_metrics),
                provider=provider,
                cache_hit=cache_hit,
                source=source,
                partial=partial_completion,
                error_category=error_category,
            )
            if full_response and save_history:
                response_text = response_text_for_metrics
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
