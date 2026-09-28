import os
import time
import random
import requests
from dotenv import load_dotenv

load_dotenv()

# Get API key from .env
API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini model
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Gemini API URL
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def explain_topic(topic):

    # Check API key
    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing in the .env file."

    # Prompt
    prompt = f"""
You are EduGenie AI, an educational assistant.

Explain the following topic in a simple and student-friendly way.

Topic: {topic}

Give the answer in this format:

1. Definition
2. Simple Explanation
3. Important Points
4. Real-World Example
5. Short Summary

Use easy language suitable for students.
"""

    # Request data
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

    # Try up to 5 times
    for attempt in range(5):

        try:

            response = requests.post(
                URL,
                params={
                    "key": API_KEY
                },
                headers={
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=60
            )

            # Gemini temporarily unavailable
            if response.status_code == 503:

                if attempt < 4:

                    delay = (2 ** attempt) + random.uniform(0, 1)

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {delay:.1f} seconds..."
                    )

                    time.sleep(delay)

                    continue

                return (
                    "Gemini is temporarily unavailable right now. "
                    "Please try again after a few seconds."
                )

            # Other HTTP errors
            response.raise_for_status()

            # Convert response to JSON
            result = response.json()

            # Get generated answer
            answer = (
                result["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

            return answer

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

    return "Unable to generate an explanation."