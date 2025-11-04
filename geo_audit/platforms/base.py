"""
Base class for AI Platform clients - Plugin interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PlatformResponse:
    """Standardized response from any AI platform"""
    platform_name: str
    query_text: str
    response_text: str
    raw_response: Dict[str, Any]
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if query was successful"""
        return self.error is None and len(self.response_text) > 0


class PlatformClient(ABC):
    """
    Abstract base class for AI platform clients.

    Each platform (Claude, ChatGPT, Google AI, Perplexity, etc.)
    implements this interface as a plugin.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize platform client with configuration

        Args:
            config: Platform-specific configuration (API keys, models, etc.)
        """
        self.config = config
        self.name = self.get_platform_name()
        self._initialize()

    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name (e.g., 'Claude', 'ChatGPT')"""
        pass

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the platform client (API clients, auth, etc.)"""
        pass

    @abstractmethod
    def query(self, query_text: str, **kwargs) -> PlatformResponse:
        """
        Execute a query on this platform

        Args:
            query_text: The question/query to ask the AI
            **kwargs: Platform-specific parameters

        Returns:
            PlatformResponse with standardized format
        """
        pass

    def test_connection(self) -> bool:
        """
        Test if the platform is accessible and configured correctly

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.query("Test connection")
            return response.success
        except Exception as e:
            print(f"Connection test failed for {self.name}: {e}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return platform capabilities (models available, rate limits, etc.)

        Returns:
            Dictionary of platform capabilities
        """
        return {
            "name": self.name,
            "models": self.config.get("models", []),
            "rate_limit": self.config.get("rate_limit"),
            "supports_images": self.config.get("supports_images", False),
        }
