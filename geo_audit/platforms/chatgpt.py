"""
ChatGPT (OpenAI) Platform Client
"""

import openai
from typing import Dict, Any
from .base import PlatformClient, PlatformResponse


class ChatGPTClient(PlatformClient):
    """ChatGPT platform client implementation"""

    def get_platform_name(self) -> str:
        return "ChatGPT"

    def _initialize(self) -> None:
        """Initialize OpenAI client"""
        api_key = self.config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API key not provided in config")

        self.client = openai.OpenAI(api_key=api_key)
        self.model = self.config.get('model', 'gpt-4o')
        self.max_tokens = self.config.get('max_tokens', 2000)

    def query(self, query_text: str, **kwargs) -> PlatformResponse:
        """
        Query ChatGPT with the given text

        Args:
            query_text: The question to ask
            **kwargs: Optional overrides (model, max_tokens, temperature, etc.)

        Returns:
            PlatformResponse with standardized format
        """
        model = kwargs.get('model', self.model)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        temperature = kwargs.get('temperature', 0.7)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": query_text}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None

            return PlatformResponse(
                platform_name=self.name,
                query_text=query_text,
                response_text=response_text,
                raw_response=response.model_dump(),
                model_used=model,
                tokens_used=tokens_used
            )

        except Exception as e:
            return PlatformResponse(
                platform_name=self.name,
                query_text=query_text,
                response_text="",
                raw_response={},
                error=str(e)
            )
