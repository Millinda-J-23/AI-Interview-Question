import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_questions(company, role, experience, difficulty, skills, count):

    prompt = f"""
You are an expert technical interviewer.

Generate exactly {count} interview questions.

Company:
{company}

Job Role:
{role}

Experience:
{experience}

Difficulty:
{difficulty}

Technical Skills:
{skills}

Rules:

1. Generate exactly {count} questions.
2. Questions should match the company's interview style.
3. Focus on the listed technical skills.
4. Mix theoretical and practical questions.
5. Return only a numbered list.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        },
        timeout=300
    )

    response.raise_for_status()

    return response.json()["response"]