"""
Screenshot generation utilities
"""

import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path
from typing import Tuple


class ScreenshotGenerator:
    """Generates screenshot images of AI responses"""

    def __init__(self, output_dir: str = "screenshots"):
        """
        Initialize screenshot generator

        Args:
            output_dir: Directory to save screenshots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Image settings
        self.width = 1200
        self.padding = 40
        self.line_spacing = 10
        self.font_size_title = 24
        self.font_size_body = 18
        self.font_size_meta = 14

        # Load fonts
        self._load_fonts()

    def _load_fonts(self) -> None:
        """Load fonts with fallback to default"""
        try:
            font_path = "/System/Library/Fonts/Helvetica.ttc"
            self.font_title = ImageFont.truetype(font_path, self.font_size_title)
            self.font_body = ImageFont.truetype(font_path, self.font_size_body)
            self.font_meta = ImageFont.truetype(font_path, self.font_size_meta)
        except Exception:
            # Fallback to default font
            self.font_title = ImageFont.load_default()
            self.font_body = ImageFont.load_default()
            self.font_meta = ImageFont.load_default()

    def generate(
        self,
        query: str,
        response: str,
        platform: str,
        query_num: int,
        date_str: str
    ) -> str:
        """
        Generate a screenshot image

        Args:
            query: The query text
            response: The AI response
            platform: Platform name (Claude, ChatGPT, etc.)
            query_num: Query number
            date_str: Date string for filename

        Returns:
            Path to saved screenshot file
        """
        # Wrap text
        wrapper = textwrap.TextWrapper(width=80)
        query_lines = wrapper.wrap(text=f"Query: {query}")
        response_lines = wrapper.wrap(text=response)

        # Calculate height needed
        line_height = self.font_size_body + self.line_spacing
        total_lines = len(query_lines) + len(response_lines) + 8
        height = total_lines * line_height + self.padding * 2

        # Create image
        img = Image.new('RGB', (self.width, height), color='white')
        draw = ImageDraw.Draw(img)

        y = self.padding

        # Draw header
        header = f"{platform} - {date_str}"
        draw.text((self.padding, y), header, fill='black', font=self.font_meta)
        y += line_height * 2

        # Draw query
        draw.text((self.padding, y), "QUERY:", fill='#1a73e8', font=self.font_title)
        y += line_height
        for line in query_lines:
            draw.text((self.padding, y), line, fill='black', font=self.font_body)
            y += line_height

        y += self.line_spacing * 2

        # Draw response
        draw.text((self.padding, y), "RESPONSE:", fill='#1a73e8', font=self.font_title)
        y += line_height
        for line in response_lines:
            draw.text((self.padding, y), line, fill='#333333', font=self.font_body)
            y += line_height

        # Save image
        filename = f"Q{query_num:03d}_{platform}_{date_str}.png"
        filepath = self.output_dir / filename
        img.save(filepath)

        return str(filepath)

    def generate_batch(
        self,
        responses: list,
        base_filename: str = "response"
    ) -> list:
        """
        Generate multiple screenshots at once

        Args:
            responses: List of dicts with query, response, platform, etc.
            base_filename: Base name for files

        Returns:
            List of generated file paths
        """
        filepaths = []
        for i, resp in enumerate(responses):
            filepath = self.generate(
                query=resp['query'],
                response=resp['response'],
                platform=resp['platform'],
                query_num=resp.get('query_num', i + 1),
                date_str=resp.get('date_str', 'unknown')
            )
            filepaths.append(filepath)

        return filepaths
