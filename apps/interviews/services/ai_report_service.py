import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_interview_report(transcript):

    prompt = f"""
You are an expert AI interview evaluator.

Analyze the following interview transcript.

{transcript}

Return JSON format:

overall_score:
technical_score:
communication_score:
strengths:
weaknesses:
suggestions:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    # return response.choices[0].message["content"]
    import json

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "overall_score": 0,
            "technical_score": 0,
            "communication_score": 0,
            "strengths": content,
            "weaknesses": "",
            "suggestions": ""
        }