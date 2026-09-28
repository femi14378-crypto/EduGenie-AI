import os
import json
import time
import random
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def generate_quiz(topic, num_questions=5):

    if not API_KEY:
        return {"error": "GEMINI_API_KEY is missing in the .env file."}

    prompt = f"""
You are EduGenie AI, an educational quiz generator.

Create {num_questions} multiple-choice questions about:

Topic: {topic}

Return ONLY valid JSON.

Use exactly this format:

[
  {{
    "question": "Question here",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Option A",
    "explanation": "Short explanation"
  }}
]

Do not add Markdown or ```json.
"""

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    for attempt in range(5):

        try:

            response = requests.post(
                URL,
                params={"key": API_KEY},
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=60
            )

            if response.status_code == 503:

                if attempt < 4:
                    delay = (2 ** attempt) + random.uniform(0, 1)

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {delay:.1f} seconds..."
                    )

                    time.sleep(delay)
                    continue

                return {
                    "error": "Gemini is temporarily unavailable. Please try again later."
                }

            response.raise_for_status()

            result = response.json()

            text = result["candidates"][0]["content"]["parts"][0]["text"]

            # Remove Markdown code fences if Gemini adds them
            text = text.strip()

            if text.startswith("```json"):
                text = text[7:]

            elif text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            quiz = json.loads(text)

            return quiz

        except requests.exceptions.RequestException as error:

            if attempt < 4:
                delay = (2 ** attempt) + random.uniform(0, 1)

                print(
                    f"Connection error. "
                    f"Retrying in {delay:.1f} seconds..."
                )

                time.sleep(delay)
                continue

            return {
                "error": f"Error while contacting Gemini: {error}"
            }

        except json.JSONDecodeError:

            return {
                "error": "Gemini returned an invalid quiz format."
            }

        except (KeyError, IndexError, TypeError):

            return {
                "error": "Error: Unexpected response received from Gemini."
            }

        except Exception as error:

            return {
                "error": f"Unexpected error: {error}"
            }

    return {
        "error": "Unable to generate quiz."
    }