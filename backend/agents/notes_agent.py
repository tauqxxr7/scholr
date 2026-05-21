from agents._generation import (
    ScholrGenerationError,
    build_provider_degraded_text,
    sanitize_user_input,
    stream_gemini_response,
)
from routers._streaming import stream_text_chunks

NOTES_PROMPT = """
You are a study notes expert for Indian BTech engineering students.

Create comprehensive study notes for: {topic}

Format your response as follows:

## Overview
2-3 sentence introduction to the topic.

## Key Concepts
List and explain the 5-7 most important concepts. Use simple language.

## Important Definitions
Define all technical terms a student needs to know.

## Formulas & Equations (if applicable)
List all relevant formulas with brief explanations.

## Exam Tips
5 specific points that commonly appear in BTech university exams.

## Quick Revision Summary
Bullet points for last-minute revision before exam.
"""


async def generate_notes_response(topic: str):
    safe_topic, warning = sanitize_user_input("notes", topic)
    if warning:
        yield f"> {warning}\n\n"

    prompt = NOTES_PROMPT.format(topic=safe_topic)

    try:
        async for chunk in stream_gemini_response(
            model_name="gemini-1.5-flash",
            prompt=prompt,
            temperature=0.4,
            max_output_tokens=1400,
        ):
            yield chunk
    except ScholrGenerationError:
        degraded = build_provider_degraded_text("notes", safe_topic)
        async for chunk in stream_text_chunks(degraded):
            yield chunk
