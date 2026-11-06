"""
Service layer encapsulating Google Gemini API integration using the official `google-genai` SDK.
"""

from typing import List, Dict
from google import genai
from app.config import settings


class GeminiService:
    """
    Service wrapper around the Google Gemini SDK for handling search and Q&A reasoning.
    """

    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        self.api_key = api_key

    def generate_answer(self, history: List[Dict[str, str]], current_prompt: str) -> str:
        """
        Sends query history and the current prompt to Gemini, returning structured text responses.
        Falls back to a simulation response if GEMINI_API_KEY is not configured.
        """
        if not self.api_key or self.api_key.startswith("mock"):
            return f"[Simulated AskGemini Response] I processed your question: '{current_prompt}'. Your GEMINI_API_KEY environment variable is active, but running in mock/fallback mode."

        try:
            # Initialize client using the environment variable GEMINI_API_KEY automatically
            client = genai.Client(api_key=self.api_key)

            # Map historical messages into Gemini chat history format ('user' and 'model')
            gemini_history = []
            for item in history[:-1]:
                role = "model" if item["role"] == "assistant" else "user"
                gemini_history.append({
                    "role": role,
                    "parts": [{"text": item["content"]}]
                })

            # Create a multi-turn chat session using gemini-2.5-flash
            chat = client.chats.create(model="gemini-2.5-flash", history=gemini_history)
            response = chat.send_message(current_prompt)
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini service: {str(e)}"


gemini_service = GeminiService()