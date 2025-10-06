#!/usr/bin/env env python3
"""
AI Query Tracker - Multi-platform AI Response Tracking
Tracks brand mentions across ChatGPT, Claude, Perplexity, and Google AI
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import time

# API Clients
import anthropic
import openai
from google import genai
import requests

# Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# Screenshot generation
from PIL import Image, ImageDraw, ImageFont
import textwrap


class AIQueryTracker:
    """Main class for tracking AI responses across platforms"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize with API keys from config file"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize API clients
        self.anthropic_client = anthropic.Anthropic(
            api_key=self.config['anthropic_api_key']
        )
        self.openai_client = openai.OpenAI(
            api_key=self.config['openai_api_key']
        )
        self.gemini_client = genai.Client(
            api_key=self.config['google_api_key']
        )
        self.perplexity_api_key = self.config['perplexity_api_key']
        
        # Initialize Google Sheets
        self.setup_google_sheets()
        
        # Create screenshots directory
        os.makedirs('screenshots', exist_ok=True)
        
    def setup_google_sheets(self):
        """Setup Google Sheets API connection"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            self.config['google_credentials_path'],
            scopes=scopes
        )
        
        self.gc = gspread.authorize(creds)
        self.sheet = self.gc.open_by_key(self.config['spreadsheet_id']).sheet1
        
    def query_claude(self, query: str) -> Dict:
        """Query Claude API"""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": query}
                ]
            )
            response_text = message.content[0].text
            return {
                'success': True,
                'response': response_text,
                'platform': 'Claude'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'Claude'
            }
    
    def query_chatgpt(self, query: str) -> Dict:
        """Query ChatGPT API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # or gpt-4-turbo, gpt-3.5-turbo
                messages=[
                    {"role": "user", "content": query}
                ],
                max_tokens=2000
            )
            response_text = response.choices[0].message.content
            return {
                'success': True,
                'response': response_text,
                'platform': 'ChatGPT'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'ChatGPT'
            }
    
    def query_gemini(self, query: str) -> Dict:
        """Query Google Gemini API"""
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=query
            )
            response_text = response.text
            return {
                'success': True,
                'response': response_text,
                'platform': 'Google AI'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'Google AI'
            }
    
    def query_perplexity(self, query: str) -> Dict:
        """Query Perplexity API"""
        try:
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {"role": "user", "content": query}
                ]
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            response_text = data['choices'][0]['message']['content']
            citations = data.get('citations', [])
            
            return {
                'success': True,
                'response': response_text,
                'citations': citations,
                'platform': 'Perplexity'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'Perplexity'
            }
    
    def create_screenshot(self, query: str, response: str, platform: str, 
                         query_num: int, date_str: str) -> str:
        """Create a screenshot image of the response"""
        # Image settings
        width = 1200
        padding = 40
        line_spacing = 10
        font_size_title = 24
        font_size_body = 18
        
        # Try to load fonts, fallback to default
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size_title)
            font_body = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size_body)
            font_meta = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()
            font_meta = ImageFont.load_default()
        
        # Wrap text
        wrapper = textwrap.TextWrapper(width=80)
        query_lines = wrapper.wrap(text=f"Query: {query}")
        response_lines = wrapper.wrap(text=response)
        
        # Calculate height needed
        line_height = font_size_body + line_spacing
        total_lines = len(query_lines) + len(response_lines) + 8
        height = total_lines * line_height + padding * 2
        
        # Create image
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        y = padding
        
        # Draw header
        header = f"{platform} - {date_str}"
        draw.text((padding, y), header, fill='black', font=font_meta)
        y += line_height * 2
        
        # Draw query
        draw.text((padding, y), "QUERY:", fill='#1a73e8', font=font_title)
        y += line_height
        for line in query_lines:
            draw.text((padding, y), line, fill='black', font=font_body)
            y += line_height
        
        y += line_spacing * 2
        
        # Draw response
        draw.text((padding, y), "RESPONSE:", fill='#1a73e8', font=font_title)
        y += line_height
        for line in response_lines:
            draw.text((padding, y), line, fill='#333333', font=font_body)
            y += line_height
        
        # Save screenshot
        filename = f"screenshots/Q{query_num}_{platform.replace(' ', '_')}_{date_str.replace('/', '-')}.png"
        img.save(filename)
        
        return filename
    
    def analyze_response(self, response: str) -> Dict:
        """
        Analyze response for BOB mentions and competitors
        Note: This is a basic analysis - manual review recommended
        """
        response_lower = response.lower()
        
        # Check for BOB mentions
        bob_keywords = ['brush on block', 'brushonblock', 'bob']
        bob_mentioned = any(keyword in response_lower for keyword in bob_keywords)
        
        # Common sunscreen brands to look for
        competitors = [
            'Supergoop', 'ColorScience', 'Peter Thomas Roth', 'EltaMD',
            'La Roche-Posay', 'Neutrogena', 'CeraVe', 'Blue Lizard',
            'Coola', 'Sun Bum', 'Black Girl Sunscreen', 'Unseen Sunscreen'
        ]
        
        mentioned_competitors = [comp for comp in competitors if comp.lower() in response_lower]
        
        return {
            'bob_mentioned': 'Yes' if bob_mentioned else 'No',
            'competitors': ', '.join(mentioned_competitors) if mentioned_competitors else 'None'
        }
    
    def extract_citations(self, response: str, platform: str, citations: List = None) -> str:
        """Extract citation sources from response"""
        if platform == 'Perplexity' and citations:
            return ', '.join(citations)
        
        # For Google AI, try to extract domains from response
        # This is basic - may need refinement
        import re
        urls = re.findall(r'https?://(?:www\.)?([^\s/]+)', response)
        return ', '.join(set(urls)) if urls else 'None'
    
    def log_to_sheet(self, row_data: List):
        """Append a row to the Google Sheet"""
        try:
            self.sheet.append_row(row_data)
            print(f"✓ Logged to Google Sheets")
        except Exception as e:
            print(f"✗ Error logging to sheet: {e}")
    
    def run_query(self, query_num: int, query_text: str, platforms: List[str] = None):
        """Run a single query across all platforms"""
        if platforms is None:
            platforms = ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']
        
        date_str = datetime.now().strftime('%m/%d/%Y')
        
        print(f"\n{'='*80}")
        print(f"Query #{query_num}: {query_text}")
        print(f"{'='*80}\n")
        
        for platform in platforms:
            print(f"Querying {platform}...", end=' ')
            
            # Query the platform
            if platform == 'Claude':
                result = self.query_claude(query_text)
            elif platform == 'ChatGPT':
                result = self.query_chatgpt(query_text)
            elif platform == 'Google AI':
                result = self.query_gemini(query_text)
            elif platform == 'Perplexity':
                result = self.query_perplexity(query_text)
            else:
                print(f"Unknown platform: {platform}")
                continue
            
            if not result['success']:
                print(f"✗ Error: {result['error']}")
                continue
            
            print(f"✓")
            
            response = result['response']
            
            # Create screenshot
            screenshot_file = self.create_screenshot(
                query_text, response, platform, query_num, date_str
            )
            
            # Analyze response
            analysis = self.analyze_response(response)
            
            # Extract citations if applicable
            citations = self.extract_citations(
                response, 
                platform, 
                result.get('citations', [])
            )
            
            # Prepare row data
            row_data = [
                query_num,                          # A - Query #
                query_text,                         # B - Query Text
                platform,                           # C - Platform
                date_str,                           # D - Test Date
                analysis['bob_mentioned'],          # E - BOB Mentioned?
                '',                                 # F - Mention Context (manual review)
                '',                                 # G - Position (manual review)
                analysis['competitors'],            # H - Competitors Mentioned
                citations,                          # I - Sources Cited
                '',                                 # J - Accuracy (manual review)
                screenshot_file,                    # K - Screenshot File
                ''                                  # L - Notes (manual review)
            ]
            
            # Log to Google Sheets
            self.log_to_sheet(row_data)
            
            # Small delay between API calls
            time.sleep(2)
        
        print(f"\n✓ Completed Query #{query_num}\n")
    
    def run_batch(self, queries: List[Dict]):
        """Run multiple queries"""
        print(f"\n🚀 Starting batch processing of {len(queries)} queries\n")
        
        for query in queries:
            self.run_query(query['num'], query['text'], query.get('platforms'))
        
        print(f"\n✅ Batch complete! Check your Google Sheet and screenshots folder.\n")


def main():
    """Main entry point"""
    # Initialize tracker
    tracker = AIQueryTracker('config.json')
    
    # Load queries from file
    with open('queries.json', 'r') as f:
        queries = json.load(f)
    
    # Run batch
    tracker.run_batch(queries)


if __name__ == '__main__':
    main()
