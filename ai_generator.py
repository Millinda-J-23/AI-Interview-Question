import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ============================================
# Gemini API Key
# ============================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(api_key=API_KEY)


# ============================================
# Fallback Questions
# ============================================

def get_fallback_questions(role, skills, count):
    questions = [
        f"1. Tell me about yourself as a {role}.",
        f"2. Explain your experience with {skills}.",
        "3. What is the difference between a List and a Tuple in Python?",
        "4. Explain Object-Oriented Programming.",
        "5. What is REST API?",
        "6. What is the difference between GET and POST requests?",
        "7. Explain SQL JOINs.",
        "8. What is database normalization?",
        "9. How do you debug an application?",
        "10. Explain exception handling in Python.",
        "11. What are decorators in Python?",
        "12. Explain multithreading.",
        "13. Describe a challenging bug you fixed.",
        "14. Explain time complexity.",
        "15. How would you optimize a slow application?",
        "16. Explain Git branching.",
        "17. What are HTTP status codes?",
        "18. Explain authentication vs authorization.",
        "19. What are Flask Blueprints?",
        "20. What project are you most proud of?"
    ]

    return "\n".join(questions[:count])


# ============================================
# Generate Interview Questions
# ============================================

def generate_questions(company, role, experience, difficulty, skills, count):

    prompt = f"""
You are an expert technical interviewer.

Generate exactly {count} interview questions.

Company: {company}
Job Role: {role}
Experience: {experience}
Difficulty: {difficulty}
Technical Skills: {skills}

Rules:
1. Generate exactly {count} interview questions.
2. Questions should match the company's interview style.
3. Focus on the listed technical skills.
4. Mix theoretical, coding, debugging and scenario-based questions.
5. Do NOT provide answers.
6. Return ONLY a numbered list.
"""

    for attempt in range(3):
        try:

            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )

            return response.text

        except Exception as e:

            error = str(e)
            print("Gemini Error:", error)

            if "503" in error and attempt < 2:
                time.sleep(5)
                continue

            break

    # Fallback
    print("Using fallback interview questions.")
    return (
        "⚠ AI service is currently unavailable.\n"
        "Showing sample interview questions instead.\n\n"
        + get_fallback_questions(role, skills, count)
    )