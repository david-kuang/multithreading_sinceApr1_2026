How to Run Your AskGemini App
## Verify your GEMINI_API_KEY is exported in your environment:
Bash
export GEMINI_API_KEY="your-actual-gemini-api-key"

## Install Dependencies:
Bash
pip install -r requirements.txt

## Run Unit Tests:
Bash
pytest

## Start the Web Server:
Bash
uvicorn app.main:app --reload

## Open in Browser:
Navigate to http://localhost:8000 to interact with AskGemini.