import os
import sys
import time
from datetime import datetime

from google import genai

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
#API_KEY = ""
MODEL = "gemini-3.8-flash"
#PROMPT = "Hello world!"
#PROMPT = "Hello! Explain AI to me."
#PROMPT = "Explain how AI works in a few words"
PROMPT = "Write a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt. Then read the file and print its contents."
RETRY_INTERVAL = 60  # seconds


def main():

    if not API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable not found.")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)

    attempt = 0

    print("=" * 60)
    print("Google Gemini API - Continuous Connection Test")
    print(f"Model: {MODEL}")
    print(f"Retry interval: {RETRY_INTERVAL} seconds")
    print("=" * 60)

    while True:

        attempt += 1

        print(
            f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] "
            f"Attempt #{attempt}: Connecting to Google..."
        )

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=PROMPT,
            )

            # Validate response
            result = response.text

            if result and result.strip():

                print("\n" + "=" * 60)
                print("SUCCESS - VALID RESPONSE RECEIVED!")
                print("=" * 60)

                print(result)

                print("\nGOOD")

                sys.exit(0)

            else:

                print("Google returned an empty response.")

        except KeyboardInterrupt:

            print("\nStopped by user.")
            sys.exit(1)

        except Exception as exc:

            print(f"Connection failed: {type(exc).__name__}: {exc}")

        # Retry after one minute
        print(f"\nNext attempt in {RETRY_INTERVAL} seconds...")
        time.sleep(RETRY_INTERVAL)


if __name__ == "__main__":
    main()
