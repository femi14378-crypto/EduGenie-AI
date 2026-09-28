import os
import time
import random
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

URL = (
    f"https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL}:generateContent"
)


def answer_question(question):

    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing in the .env file."

    prompt = f"""
You are EduGenie AI, an educational assistant.

Answer the following question in a simple and student-friendly way.

Question: {question}

Give a clear and easy-to-understand answer.
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
                headers={
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=60
            )

            # Rate limit / temporary server problem
            if response.status_code in (429, 503):

                if attempt < 4:

                    delay = (2 ** attempt) + random.uniform(0, 1)

                    print(
                        f"Gemini returned HTTP {response.status_code}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )

                    time.sleep(delay)
                    continue

                if response.status_code == 429:
                    return (
                        "Gemini API rate limit reached. "
                        "Please wait a little and try again."
                    )

                return (
                    "Gemini service is temporarily unavailable. "
                    "Please try again later."
                )

            response.raise_for_status()

            result = response.json()

            return (
                result["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

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

    return "Unable to answer the question."