from agents._generation import (
    ScholrGenerationError,
    build_provider_degraded_text,
    sanitize_user_input,
    stream_gemini_response,
)
from routers._streaming import stream_text_chunks

RESEARCH_PROMPT = """
You are an expert research assistant for Indian BTech engineering students.

A student needs help with this research topic: {topic}

Provide your response in this EXACT format with these headers:

## 5 Key Research Papers
For each paper provide: Title, Authors (if known), Year, and a 2-line summary.
Focus on papers relevant to Indian engineering curriculum.

## Must-Know Concepts Before You Start
List exactly 3 foundational concepts the student must understand first.
Keep each explanation to 2-3 sentences.

## Recommended Reading Order
Provide a beginner-to-advanced reading sequence.
Explain WHY you recommend this order.

## Research Gap to Explore
Identify ONE specific research gap in this area that a BTech student
could realistically investigate for a final year project.
Be specific about what is missing in current research.

Keep language clear and accessible for a BTech student.
Do not use overly academic jargon.
"""


async def generate_research_response(topic: str):
    safe_topic, warning = sanitize_user_input("research", topic)
    if warning:
        yield f"> {warning}\n\n"

    prompt = RESEARCH_PROMPT.format(topic=safe_topic)

    try:
        async for chunk in stream_gemini_response(
            model_name="gemini-1.5-flash",
            prompt=prompt,
            temperature=0.6,
            max_output_tokens=1600,
        ):
            yield chunk
    except ScholrGenerationError as exc:
        degraded = build_provider_degraded_text("research", safe_topic)
        async for chunk in stream_text_chunks(degraded):
            yield chunk
