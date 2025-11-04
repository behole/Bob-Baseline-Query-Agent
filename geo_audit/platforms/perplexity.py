"""
Perplexity AI Platform Client
"""

import requests
from typing import Dict, Any, List
from .base import PlatformClient, PlatformResponse


class PerplexityClient(PlatformClient):
    """Perplexity AI platform client implementation"""

    def get_platform_name(self) -> str:
        return "Perplexity"

    def _initialize(self) -> None:
        """Initialize Perplexity API configuration"""
        api_key = self.config.get('api_key')
        if not api_key:
            raise ValueError("Perplexity API key not provided in config")

        self.api_key = api_key
        self.model = self.config.get('model', 'sonar-pro')
        self.api_url = "https://api.perplexity.ai/chat/completions"

    def query(self, query_text: str, **kwargs) -> PlatformResponse:
        """
        Query Perplexity with the given text

        Args:
            query_text: The question to ask
            **kwargs: Optional overrides (model, etc.)

        Returns:
            PlatformResponse with standardized format
        """
        model = kwargs.get('model', self.model)

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": query_text}
                ]
            }

            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            response_text = data['choices'][0]['message']['content']
            citations = data.get('citations', [])

            # Store citations in raw_response for later use
            return PlatformResponse(
                platform_name=self.name,
                query_text=query_text,
                response_text=response_text,
                raw_response={
                    'data': data,
                    'citations': citations
                },
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

    def get_citations(self, response: PlatformResponse) -> List[str]:
        """
        Extract citations from a Perplexity response

        Args:
            response: PlatformResponse from Perplexity

        Returns:
            List of citation URLs
        """
        if response.platform_name != self.name:
            return []

        return response.raw_response.get('citations', [])
