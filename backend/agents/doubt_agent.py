from agents._generation import (
    ScholrGenerationError,
    build_provider_degraded_text,
    sanitize_user_input,
    stream_gemini_response,
)
from routers._streaming import stream_text_chunks

FAST_DOUBT_PROMPT = """
You are a patient engineering tutor. You MUST always structure your response with ## headings: Simple Answer, Step-by-Step Explanation, Example, Common Mistake, Related Topics. Never merge sections. Never skip Example or Common Mistake. Keep Simple Answer to 2-3 sentences maximum.

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
You are a patient engineering tutor. You MUST always structure your response with ## headings: Simple Answer, Step-by-Step Explanation, Example, Common Mistake, Related Topics. Never merge sections. Never skip Example or Common Mistake. Keep Simple Answer to 2-3 sentences maximum.

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


def build_doubt_prompt(question: str, subject: str = "General", response_mode: str = "fast") -> str:
    prompt_template = DEEP_DOUBT_PROMPT if _is_deep_mode(response_mode) else FAST_DOUBT_PROMPT
    return prompt_template.format(question=question, subject=subject)


def get_doubt_generation_config(response_mode: str = "fast") -> dict[str, int | float]:
    is_deep = _is_deep_mode(response_mode)
    return {
        "temperature": 0.3 if is_deep else 0.15,
        "max_output_tokens": 760 if is_deep else 460,
    }


async def generate_doubt_response(question: str, subject: str = "General", response_mode: str = "fast"):
    safe_question, warning = sanitize_user_input("doubt", question)
    if warning:
        yield f"> {warning}\n\n"

    prompt = build_doubt_prompt(safe_question, subject, response_mode)
    generation_config = get_doubt_generation_config(response_mode)

    try:
        async for chunk in stream_gemini_response(
            model_name="gemini-1.5-flash",
            prompt=prompt,
            temperature=float(generation_config["temperature"]),
            max_output_tokens=int(generation_config["max_output_tokens"]),
        ):
            yield chunk
    except ScholrGenerationError:
        degraded = build_provider_degraded_text("doubt", safe_question, subject=subject)
        async for chunk in stream_text_chunks(degraded):
            yield chunk
