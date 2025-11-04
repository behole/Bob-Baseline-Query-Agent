"""
Google Sheets Storage Backend
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional
from .base import StorageBackend


class GoogleSheetsBackend(StorageBackend):
    """Google Sheets implementation of StorageBackend"""

    def _initialize(self) -> None:
        """Initialize Google Sheets API connection"""
        credentials_path = self.config.get('credentials_path')
        spreadsheet_id = self.config.get('spreadsheet_id')

        if not credentials_path:
            raise ValueError("Google credentials path not provided in config")
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID not provided in config")

        # Setup scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        # Authorize with service account
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=scopes
        )

        self.gc = gspread.authorize(creds)
        self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
        self._worksheets_cache = {}

    def create_worksheet(self, worksheet_name: str, headers: List[str]) -> bool:
        """
        Create a new worksheet with headers

        Args:
            worksheet_name: Name of the worksheet to create
            headers: Column headers

        Returns:
            True if successful
        """
        try:
            # Check if worksheet already exists
            if self.worksheet_exists(worksheet_name):
                print(f"Worksheet '{worksheet_name}' already exists")
                return True

            # Create new worksheet (default 1000 rows, cols based on headers)
            worksheet = self.spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=len(headers)
            )

            # Write headers
            worksheet.append_row(headers)

            # Cache the worksheet
            self._worksheets_cache[worksheet_name] = worksheet

            return True

        except Exception as e:
            print(f"Error creating worksheet '{worksheet_name}': {e}")
            return False

    def write_row(self, worksheet_name: str, row_data: Dict[str, Any]) -> bool:
        """
        Write a single row of data

        Args:
            worksheet_name: Target worksheet name
            row_data: Dictionary mapping column names to values

        Returns:
            True if successful
        """
        try:
            worksheet = self._get_worksheet(worksheet_name)
            if not worksheet:
                return False

            # Get headers to determine column order
            headers = worksheet.row_values(1)

            # Build row in correct order
            row = [str(row_data.get(header, '')) for header in headers]

            # Append row
            worksheet.append_row(row)

            return True

        except Exception as e:
            print(f"Error writing row to '{worksheet_name}': {e}")
            return False

    def write_rows(self, worksheet_name: str, rows_data: List[Dict[str, Any]]) -> bool:
        """
        Write multiple rows of data (batch operation)

        Args:
            worksheet_name: Target worksheet name
            rows_data: List of dictionaries mapping column names to values

        Returns:
            True if successful
        """
        try:
            worksheet = self._get_worksheet(worksheet_name)
            if not worksheet:
                return False

            # Get headers to determine column order
            headers = worksheet.row_values(1)

            # Build rows in correct order
            rows = []
            for row_data in rows_data:
                row = [str(row_data.get(header, '')) for header in headers]
                rows.append(row)

            # Batch append
            worksheet.append_rows(rows)

            return True

        except Exception as e:
            print(f"Error writing rows to '{worksheet_name}': {e}")
            return False

    def read_worksheet(self, worksheet_name: str) -> List[Dict[str, Any]]:
        """
        Read all data from a worksheet

        Args:
            worksheet_name: Source worksheet name

        Returns:
            List of dictionaries (one per row)
        """
        try:
            worksheet = self._get_worksheet(worksheet_name)
            if not worksheet:
                return []

            # Get all records (returns list of dicts)
            records = worksheet.get_all_records()

            return records

        except Exception as e:
            print(f"Error reading worksheet '{worksheet_name}': {e}")
            return []

    def worksheet_exists(self, worksheet_name: str) -> bool:
        """
        Check if a worksheet exists

        Args:
            worksheet_name: Worksheet name to check

        Returns:
            True if exists
        """
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            self._worksheets_cache[worksheet_name] = worksheet
            return True
        except gspread.exceptions.WorksheetNotFound:
            return False
        except Exception as e:
            print(f"Error checking worksheet '{worksheet_name}': {e}")
            return False

    def list_worksheets(self) -> List[str]:
        """
        List all available worksheets

        Returns:
            List of worksheet names
        """
        try:
            worksheets = self.spreadsheet.worksheets()
            return [ws.title for ws in worksheets]
        except Exception as e:
            print(f"Error listing worksheets: {e}")
            return []

    def _get_worksheet(self, worksheet_name: str) -> Optional[Any]:
        """
        Get worksheet object (uses cache)

        Args:
            worksheet_name: Worksheet name

        Returns:
            Worksheet object or None
        """
        # Check cache first
        if worksheet_name in self._worksheets_cache:
            return self._worksheets_cache[worksheet_name]

        # Try to get worksheet
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            self._worksheets_cache[worksheet_name] = worksheet
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            print(f"Worksheet '{worksheet_name}' not found")
            return None
        except Exception as e:
            print(f"Error getting worksheet '{worksheet_name}': {e}")
            return None

    def clear_worksheet(self, worksheet_name: str, keep_headers: bool = True) -> bool:
        """
        Clear all data from a worksheet

        Args:
            worksheet_name: Worksheet to clear
            keep_headers: If True, keep the first row (headers)

        Returns:
            True if successful
        """
        try:
            worksheet = self._get_worksheet(worksheet_name)
            if not worksheet:
                return False

            if keep_headers:
                # Clear all except first row
                worksheet.delete_rows(2, worksheet.row_count)
            else:
                # Clear everything
                worksheet.clear()

            return True

        except Exception as e:
            print(f"Error clearing worksheet '{worksheet_name}': {e}")
            return False
