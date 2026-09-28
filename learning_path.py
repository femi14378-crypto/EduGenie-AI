import os
import time
import random
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def create_learning_path(goal):

    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing in the .env file."

    prompt = f"""
You are EduGenie AI, a helpful educational learning-path generator.

Create a simple learning path for this goal:

{goal}

Include:

1. Learning Goal
2. Topics to Learn
3. Weekly Plan
4. Daily Practice
5. Practice Activities
6. Small Projects
7. Revision Plan
8. Final Assessment

Make it simple and suitable for students.
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

                return "Gemini is temporarily unavailable. Please try again later."

            response.raise_for_status()

            result = response.json()

            return result["candidates"][0]["content"]["parts"][0]["text"]

        except requests.exceptions.RequestException as error:

            if attempt < 4:
                delay = (2 ** attempt) + random.uniform(0, 1)

                print(
                    f"Connection error. "
                    f"Retrying in {delay:.1f} seconds..."
                )

                time.sleep(delay)
                continue

            return f"Error while contacting Gemini: {error}"

        except (KeyError, IndexError, TypeError):

            return "Error: Unexpected response received from Gemini."

        except Exception as error:

            return f"Unexpected error: {error}"

    return "Unable to create the learning path."