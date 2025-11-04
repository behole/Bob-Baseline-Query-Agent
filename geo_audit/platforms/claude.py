"""
Claude AI Platform Client
"""

import anthropic
from typing import Dict, Any
from .base import PlatformClient, PlatformResponse


class ClaudeClient(PlatformClient):
    """Claude AI platform client implementation"""

    def get_platform_name(self) -> str:
        return "Claude"

    def _initialize(self) -> None:
        """Initialize Anthropic client"""
        api_key = self.config.get('api_key')
        if not api_key:
            raise ValueError("Claude API key not provided in config")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = self.config.get('model', 'claude-sonnet-4-20250514')
        self.max_tokens = self.config.get('max_tokens', 2000)

    def query(self, query_text: str, **kwargs) -> PlatformResponse:
        """
        Query Claude with the given text

        Args:
            query_text: The question to ask
            **kwargs: Optional overrides (model, max_tokens, etc.)

        Returns:
            PlatformResponse with standardized format
        """
        model = kwargs.get('model', self.model)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)

        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": query_text}
                ]
            )

            response_text = message.content[0].text

            return PlatformResponse(
                platform_name=self.name,
                query_text=query_text,
                response_text=response_text,
                raw_response=message.model_dump(),
                model_used=model,
                tokens_used=message.usage.output_tokens if hasattr(message, 'usage') else None
            )

        except Exception as e:
            return PlatformResponse(
                platform_name=self.name,
                query_text=query_text,
                response_text="",
                raw_response={},
                error=str(e)
            )
