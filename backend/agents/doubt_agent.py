from agents._generation import (
    ScholrGenerationError,
    build_provider_degraded_text,
    sanitize_user_input,
    stream_gemini_response,
)
from routers._streaming import stream_text_chunks

FAST_DOUBT_PROMPT = """
You are a patient and clear BTech subject expert.

A student has this doubt: {question}
Subject area: {subject}

Default mode is FAST. No intro or outro.
Use maximum 4 sections and 5-7 bullets total.

## Direct Answer
Answer in 2-3 simple sentences.

## Steps
Give 3-4 numbered steps.

## Example
Give one short example.

## Common Mistake
Mention one misconception to avoid.

Keep the whole answer under 380 words.
"""

DEEP_DOUBT_PROMPT = """
You are a patient and clear BTech subject expert.

A student has this doubt: {question}
Subject area: {subject}

Use 5 sections max:
## Direct Answer
## Step-by-Step Explanation
## Example
## Common Mistake
## Related Concepts

No intro/outro. Keep under 750 words.
"""


def _is_deep_mode(response_mode: str) -> bool:
    return response_mode.strip().lower() == "deep"


async def generate_doubt_response(question: str, subject: str = "General", response_mode: str = "fast"):
    safe_question, warning = sanitize_user_input("doubt", question)
    if warning:
        yield f"> {warning}\n\n"

    prompt_template = DEEP_DOUBT_PROMPT if _is_deep_mode(response_mode) else FAST_DOUBT_PROMPT
    prompt = prompt_template.format(question=safe_question, subject=subject)

    try:
        async for chunk in stream_gemini_response(
            model_name="gemini-1.5-flash",
            prompt=prompt,
            temperature=0.3 if _is_deep_mode(response_mode) else 0.15,
            max_output_tokens=760 if _is_deep_mode(response_mode) else 460,
        ):
            yield chunk
    except ScholrGenerationError:
        degraded = build_provider_degraded_text("doubt", safe_question, subject=subject)
        async for chunk in stream_text_chunks(degraded):
            yield chunk
