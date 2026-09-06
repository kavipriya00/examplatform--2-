"""
All Gemini API calls live here, isolated from views.py, so the AI logic
is easy to find, test, and swap out (e.g. for OpenAI) without touching
the rest of the app.
"""
import json
import re
from django.conf import settings
from google import genai


def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _clean_json(raw_text):
    return re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()


def generate_questions(syllabus_text, unit_number, difficulty, count=5):
    """
    Sends the syllabus text to Gemini and asks for `count` MCQs of a given
    difficulty, scoped to one unit. Returns a list of dicts ready to be
    saved as Question objects.
    """
    prompt = f"""
You are generating exam questions for a university course.

Syllabus content (Unit {unit_number}):
\"\"\"{syllabus_text}\"\"\"

Generate exactly {count} multiple-choice questions at {difficulty} difficulty
based ONLY on the content above.

Respond with ONLY a JSON array (no markdown, no explanation text outside the
JSON), where each item has this exact shape:
{{
  "topic_name": "short topic name",
  "question": "the question text",
  "option_a": "...",
  "option_b": "...",
  "option_c": "...",
  "option_d": "...",
  "correct_option": "A",
  "explanation": "one sentence why this is correct"
}}
"""
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    try:
        return json.loads(_clean_json(response.text))
    except json.JSONDecodeError:
        return []


def extract_units_from_syllabus(syllabus_text):
    """
    Asks Gemini to split raw syllabus text into a unit-number -> text map,
    matching Module 3's requirement to identify Units/Topics/Subtopics.
    """
    prompt = f"""
Here is a course syllabus:
\"\"\"{syllabus_text}\"\"\"

Split it into units. Respond with ONLY a JSON array, no other text, like:
[
  {{"unit_number": 1, "unit_title": "Introduction", "content": "..."}},
  {{"unit_number": 2, "unit_title": "Regression", "content": "..."}}
]
"""
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    try:
        return json.loads(_clean_json(response.text))
    except json.JSONDecodeError:
        return []
