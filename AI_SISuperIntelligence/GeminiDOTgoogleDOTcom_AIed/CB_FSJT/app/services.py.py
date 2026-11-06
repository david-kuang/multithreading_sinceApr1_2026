"""
Service layer encapsulating LLM API invocation logic with fallback mechanisms.
"""

from typing import List, Dict
import openai
from app.config import settings


class LLMService:
    """
    Handles interactions with the OpenAI API or generates fallback responses if unconfigured/testing.
    """

    def __init__(self, api_key: str = settings.OPENAI_API_KEY):
        self.api_key = api_key

    def generate_chat_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Sends formatted message history to OpenAI ChatCompletion API and returns text response.
        Provides realistic mock fallback responses when invalid/mock API keys are present.
        """
        if not self.api_key or self.api_key == "mock-key-for-testing" or self.api_key.startswith("mock"):
            last_message = messages[-1]["content"] if messages else ""
            return f"[Simulated Response] I received your message: '{last_message}'. Set a valid OPENAI_API_KEY to enable live AI!"

        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback handling for API errors (e.g. rate limits, network failures)
            return f"Error communicating with AI service: {str(e)}"


llm_service = LLMService()