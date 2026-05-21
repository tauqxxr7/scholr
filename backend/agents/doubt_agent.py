from agents._generation import (
    ScholrGenerationError,
    build_provider_degraded_text,
    sanitize_user_input,
    stream_gemini_response,
)
from routers._streaming import stream_text_chunks

DOUBT_PROMPT = """
You are a patient and clear BTech subject expert.

A student has this doubt: {question}
Subject area: {subject}

Answer in this format:

## Simple Answer
Answer in 2-3 sentences using the simplest possible language.

## Step-by-Step Explanation
Break down the concept step by step. Number each step.

## Example
Give one concrete, relatable example a BTech student will understand.

## Common Mistake to Avoid
Mention one common misconception students have about this topic.

## Related Concepts
List 3 related topics the student should also understand.
"""


async def generate_doubt_response(question: str, subject: str = "General"):
    safe_question, warning = sanitize_user_input("doubt", question)
    if warning:
        yield f"> {warning}\n\n"

    prompt = DOUBT_PROMPT.format(question=safe_question, subject=subject)

    try:
        async for chunk in stream_gemini_response(
            model_name="gemini-1.5-flash",
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=1100,
        ):
            yield chunk
    except ScholrGenerationError:
        degraded = build_provider_degraded_text("doubt", safe_question, subject=subject)
        async for chunk in stream_text_chunks(degraded):
            yield chunk
