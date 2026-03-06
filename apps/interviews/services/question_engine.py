import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_question(interview, previous_answers, difficulty):

    history = ""

    for ans in previous_answers:
        history += f"""
Question: {ans.question.question_text}
Answer: {ans.answer_text}
"""

    prompt = f"""
You are an expert interviewer.

Interview Type: {interview.interview_type}
Difficulty Level: {difficulty}

Job Description:
{interview.jd.original_text}

Previous conversation:
{history}

Generate the NEXT interview question.

Rules:

1. Ask follow-up questions based on candidate answers.
2. Increase difficulty if answers are strong.
3. Decrease difficulty if answers are weak.
4. Ask ONLY one question.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content