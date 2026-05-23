from agents._generation import (
    ScholrGenerationError,
    build_provider_degraded_text,
    sanitize_user_input,
    stream_gemini_response,
)
from routers._streaming import stream_text_chunks

FAST_NOTES_PROMPT = """
You are a study notes expert for Indian BTech engineering students.

Create compact revision notes for: {topic}

Default mode is FAST. No intro or outro.
Use maximum 4 sections and 5-7 bullets total.

## Meaning
- 2-line explanation.

## Core Points
- 4-5 exam-focused bullets.

## Example / Formula
- 1 useful example, formula, or condition if relevant.

## Quick Revision
- 2 memory hooks or viva cues.

Keep the whole answer under 420 words.
"""

DEEP_NOTES_PROMPT = """
You are a study notes expert for Indian BTech engineering students.

Create study notes for: {topic}

Use 5 sections max:
## Overview
## Key Concepts
## Important Definitions
## Formula / Example
## Exam Tips

No intro/outro. Keep under 850 words.
"""


def _is_deep_mode(response_mode: str) -> bool:
    return response_mode.strip().lower() == "deep"


async def generate_notes_response(topic: str, response_mode: str = "fast"):
    safe_topic, warning = sanitize_user_input("notes", topic)
    if warning:
        yield f"> {warning}\n\n"

    prompt_template = DEEP_NOTES_PROMPT if _is_deep_mode(response_mode) else FAST_NOTES_PROMPT
    prompt = prompt_template.format(topic=safe_topic)

    try:
        async for chunk in stream_gemini_response(
            model_name="gemini-1.5-flash",
            prompt=prompt,
            temperature=0.35 if _is_deep_mode(response_mode) else 0.2,
            max_output_tokens=850 if _is_deep_mode(response_mode) else 500,
        ):
            yield chunk
    except ScholrGenerationError:
        degraded = build_provider_degraded_text("notes", safe_topic)
        async for chunk in stream_text_chunks(degraded):
            yield chunk
