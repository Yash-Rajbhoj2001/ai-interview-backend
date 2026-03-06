import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_question(job_role, difficulty, previous_questions):

    prompt = f"""
You are an AI technical interviewer.

Generate ONE interview question.

Job Role: {job_role}
Difficulty: {difficulty}

Avoid repeating these questions:
{previous_questions}

Return only the question text.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content