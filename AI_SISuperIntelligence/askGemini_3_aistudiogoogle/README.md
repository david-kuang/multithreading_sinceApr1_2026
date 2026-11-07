# Gemini Web Chat App

A lightweight web application powered by **FastAPI** and the official **Google Gen AI SDK (`google-genai`)**.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

## Set your API Key:
Make sure your GEMINI_API_KEY is exported in your environment:
Bash
export GEMINI_API_KEY="your_actual_api_key_here"
Run the Server:
Bash
uvicorn app.main:app --reload
Open in Browser:
Navigate to: http://127.0.0.1:8000
---

<ElicitationsGroup message="To take this further:">
  <Elicitation label="Add conversation memory/chat history to the backend session" query="How do I add session-based chat history and context memory to this FastAPI and Gemini backend?"/>
  <Elicitation label="Enable markdown and code syntax highlighting in the chat UI" query="How can I add marked.js and highlight.js to render Markdown and code snippets nicely in the chat UI?"/>
</ElicitationsGroup>