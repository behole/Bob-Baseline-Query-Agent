"""
Storage backends - Abstract storage layer
"""

from .base import StorageBackend
from .google_sheets import GoogleSheetsBackend

__all__ = ['StorageBackend', 'GoogleSheetsBackend']
