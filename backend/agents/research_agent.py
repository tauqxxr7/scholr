from agents._generation import stream_gemini_response

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
    prompt = RESEARCH_PROMPT.format(topic=topic)

    async for chunk in stream_gemini_response(
        model_name="gemini-2.5-flash",
        prompt=prompt,
        temperature=0.7,
        max_output_tokens=2048,
    ):
        yield chunk
