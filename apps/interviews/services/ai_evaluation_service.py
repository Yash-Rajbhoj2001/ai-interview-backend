import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_answer(question, answer):

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

Question:
{question}

Candidate Answer:
{answer}

Score the answer from 1 to 10.

Return JSON format:

score:
feedback:
strengths:
improvements:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    import json

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "score": 5,
            "feedback": content,
            "strengths": "",
            "improvements": ""
        }