import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

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
    prompt = DOUBT_PROMPT.format(question=question, subject=subject)
    response = await model.generate_content_async(
        prompt,
        stream=True,
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=1500
        )
    )

    async for chunk in response:
        if getattr(chunk, "text", None):
            yield chunk.text
