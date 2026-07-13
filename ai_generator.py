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
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )

            return response.text

        except Exception as e:
            error = str(e)
            print("Gemini Error:", error)  # This will appear in Render logs

            if "503" in error and attempt < 2:
                time.sleep(5)
                continue

            raise Exception(error)

    return "Gemini is busy. Please try again after a few minutes."