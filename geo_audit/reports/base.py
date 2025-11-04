"""
Base class for report generators - Plugin interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path


class ReportGenerator(ABC):
    """
    Abstract base class for report generators.

    Each report type (standard, advanced, PDF, dashboard) implements this interface.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize report generator

        Args:
            config: Report-specific configuration (styling, branding, etc.)
        """
        self.config = config
        self.report_type = self.get_report_type()

    @abstractmethod
    def get_report_type(self) -> str:
        """Return the report type name (e.g., 'standard', 'advanced')"""
        pass

    @abstractmethod
    def generate(
        self,
        data: List[Dict[str, Any]],
        brand_name: str,
        output_path: str,
        **kwargs
    ) -> Path:
        """
        Generate a report from tracking data

        Args:
            data: List of tracking results (from storage backend)
            brand_name: Brand being tracked
            output_path: Where to save the report
            **kwargs: Report-specific parameters

        Returns:
            Path to generated report file
        """
        pass

    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """
        Return list of required data columns for this report type

        Returns:
            List of column names
        """
        pass

    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate that data contains required columns

        Args:
            data: Data to validate

        Returns:
            True if valid
        """
        if not data:
            return False

        required = set(self.get_required_columns())
        available = set(data[0].keys())

        missing = required - available
        if missing:
            print(f"Missing required columns: {missing}")
            return False

        return True

    def get_supported_formats(self) -> List[str]:
        """
        Return list of supported output formats

        Returns:
            List of format extensions (e.g., ['html', 'pdf'])
        """
        return ['html']  # Default to HTML
