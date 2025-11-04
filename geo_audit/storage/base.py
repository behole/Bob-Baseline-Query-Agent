"""
Base class for storage backends - Abstract storage layer
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.

    Supports Google Sheets, databases, or any other storage mechanism.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize storage backend

        Args:
            config: Backend-specific configuration
        """
        self.config = config
        self._initialize()

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the storage backend (connections, auth, etc.)"""
        pass

    @abstractmethod
    def create_worksheet(self, worksheet_name: str, headers: List[str]) -> bool:
        """
        Create a new worksheet/table

        Args:
            worksheet_name: Name of the worksheet/table
            headers: Column headers

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def write_row(self, worksheet_name: str, row_data: Dict[str, Any]) -> bool:
        """
        Write a single row of data

        Args:
            worksheet_name: Target worksheet/table name
            row_data: Dictionary mapping column names to values

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def write_rows(self, worksheet_name: str, rows_data: List[Dict[str, Any]]) -> bool:
        """
        Write multiple rows of data (batch operation)

        Args:
            worksheet_name: Target worksheet/table name
            rows_data: List of dictionaries mapping column names to values

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def read_worksheet(self, worksheet_name: str) -> List[Dict[str, Any]]:
        """
        Read all data from a worksheet/table

        Args:
            worksheet_name: Source worksheet/table name

        Returns:
            List of dictionaries (one per row)
        """
        pass

    @abstractmethod
    def worksheet_exists(self, worksheet_name: str) -> bool:
        """
        Check if a worksheet/table exists

        Args:
            worksheet_name: Worksheet/table name to check

        Returns:
            True if exists
        """
        pass

    @abstractmethod
    def list_worksheets(self) -> List[str]:
        """
        List all available worksheets/tables

        Returns:
            List of worksheet/table names
        """
        pass

    def test_connection(self) -> bool:
        """
        Test if storage backend is accessible

        Returns:
            True if connection successful
        """
        try:
            self.list_worksheets()
            return True
        except Exception as e:
            print(f"Storage connection test failed: {e}")
            return False
