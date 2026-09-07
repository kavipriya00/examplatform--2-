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


def generate_questions(syllabus_text, unit_number, difficulty, mcq_count=5, long_count=0, long_marks=15):
    """
    Sends the syllabus text to Gemini and asks for a mix of MCQ (1 mark each)
    and long-answer questions (worth `long_marks` each). Returns a list of
    dicts ready to be saved as Question objects.
    """
    prompt = f"""
You are generating exam questions for a university course.

Syllabus content (Unit {unit_number}):
\"\"\"{syllabus_text}\"\"\"

Generate exactly {mcq_count} multiple-choice questions (1 mark each) and
{long_count} long-answer/essay questions ({long_marks} marks each), all at
{difficulty} difficulty, based ONLY on the content above.

Respond with ONLY a JSON array (no markdown, no explanation text outside the
JSON). Each item must have this shape:

For MCQs:
{{
  "question_type": "MCQ",
  "topic_name": "short topic name",
  "question": "the question text",
  "marks": 1,
  "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...",
  "correct_option": "A",
  "explanation": "one sentence why this is correct"
}}

For long-answer questions:
{{
  "question_type": "LONG",
  "topic_name": "short topic name",
  "question": "the essay-style question text",
  "marks": {long_marks}
}}
"""
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-3.6-flash",
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
        model="gemini-3.6-flash",
        contents=prompt,
    )

    try:
        return json.loads(_clean_json(response.text))
    except json.JSONDecodeError:
        return []