import json
from collections.abc import AsyncIterator


async def sse_json_stream(chunks: AsyncIterator[str]):
    try:
        async for chunk in chunks:
            payload = json.dumps({"chunk": chunk})
            yield f"data: {payload}\n\n"
    finally:
        yield "data: [DONE]\n\n"
