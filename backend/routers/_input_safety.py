import json
import re

from fastapi.responses import StreamingResponse


def sanitize_input(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def is_likely_spam(text: str) -> bool:
    spam_signals = ["http://", "https://", "buy now", "click here", "free money", "casino", "viagra"]
    low = text.lower()
    return any(signal in low for signal in spam_signals) or len(text) < 3


def invalid_academic_topic_stream() -> StreamingResponse:
    async def stream():
        yield f"data: {json.dumps({'type': 'chunk', 'chunk': 'Please enter a valid academic topic.'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
