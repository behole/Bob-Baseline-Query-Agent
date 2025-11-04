"""
AI Platform clients - Plugin system
"""

from .base import PlatformClient, PlatformResponse
from .claude import ClaudeClient
from .chatgpt import ChatGPTClient
from .google_ai import GoogleAIClient
from .perplexity import PerplexityClient

__all__ = [
    'PlatformClient',
    'PlatformResponse',
    'ClaudeClient',
    'ChatGPTClient',
    'GoogleAIClient',
    'PerplexityClient'
]
