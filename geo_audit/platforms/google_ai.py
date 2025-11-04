"""
Google AI (Gemini) Platform Client
"""

from google import genai
from typing import Dict, Any
from .base import PlatformClient, PlatformResponse


class GoogleAIClient(PlatformClient):
    """Google AI (Gemini) platform client implementation"""

    def get_platform_name(self) -> str:
        return "Google AI"

    def _initialize(self) -> None:
        """Initialize Google Gemini client"""
        api_key = self.config.get('api_key')
        if not api_key:
            raise ValueError("Google AI API key not provided in config")

        self.client = genai.Client(api_key=api_key)
        self.model = self.config.get('model', 'gemini-2.0-flash-exp')

    def query(self, query_text: str, **kwargs) -> PlatformResponse:
        """
        Query Google AI with the given text

        Args:
            query_text: The question to ask
            **kwargs: Optional overrides (model, etc.)

        Returns:
            PlatformResponse with standardized format
        """
        model = kwargs.get('model', self.model)

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=query_text
            )

            response_text = response.text

            return PlatformResponse(
                platform_name=self.name,
                query_text=query_text,
                response_text=response_text,
                raw_response={'text': response_text},  # Gemini response format varies
                model_used=model
            )

        except Exception as e:
            return PlatformResponse(
                platform_name=self.name,
                query_text=query_text,
                response_text="",
                raw_response={},
                error=str(e)
            )
