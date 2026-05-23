from agents._generation import (
    ScholrGenerationError,
    build_provider_degraded_text,
    sanitize_user_input,
    stream_gemini_response,
)
from routers._streaming import stream_text_chunks

FAST_RESEARCH_PROMPT = """
You are an expert research assistant for Indian BTech engineering students.

A student needs fast research direction for: {topic}

Default mode is FAST. Be concise. No intro or outro.
Use maximum 4 sections and 5-7 bullets total.

## Key Concepts
- 3-4 must-know concepts, each with a 1-line meaning.

## Papers / Search Queries
- 3 paper search queries or paper types, each with a 2-line summary.

## Reading Order
- 3 short steps from beginner to project-ready.

## BTech Project Gap
- 1 realistic gap a student can explore.

Keep the whole answer under 450 words.
"""

DEEP_RESEARCH_PROMPT = """
You are an expert research assistant for Indian BTech engineering students.

A student needs research direction for: {topic}

Provide 5 sections max:
## Key Papers
List 5 relevant paper directions with 2-line summaries.
## Must-Know Concepts
List 5 concepts.
## Reading Order
Give a beginner-to-advanced order.
## Research Gap
Give one realistic BTech project gap.
## Next Search Queries
List 4 useful queries.

No intro/outro. Keep under 900 words.
"""


def _is_deep_mode(response_mode: str) -> bool:
    return response_mode.strip().lower() == "deep"


def build_research_prompt(topic: str, response_mode: str = "fast") -> str:
    prompt_template = DEEP_RESEARCH_PROMPT if _is_deep_mode(response_mode) else FAST_RESEARCH_PROMPT
    return prompt_template.format(topic=topic)


def get_research_generation_config(response_mode: str = "fast") -> dict[str, int | float]:
    is_deep = _is_deep_mode(response_mode)
    return {
        "temperature": 0.4 if is_deep else 0.25,
        "max_output_tokens": 1600 if is_deep else 800,
    }


async def generate_research_response(topic: str, response_mode: str = "fast"):
    safe_topic, warning = sanitize_user_input("research", topic)
    if warning:
        yield f"> {warning}\n\n"

    prompt = build_research_prompt(safe_topic, response_mode)
    generation_config = get_research_generation_config(response_mode)

    try:
        async for chunk in stream_gemini_response(
            model_name="gemini-1.5-flash",
            prompt=prompt,
            temperature=float(generation_config["temperature"]),
            max_output_tokens=int(generation_config["max_output_tokens"]),
        ):
            yield chunk
    except ScholrGenerationError as exc:
        degraded = build_provider_degraded_text("research", safe_topic)
        async for chunk in stream_text_chunks(degraded):
            yield chunk
