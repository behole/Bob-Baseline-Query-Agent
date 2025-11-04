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
import argparse

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
    
    def __init__(self, config_path: str = "config.json", brand_name: str = "Brush On Block"):
        """Initialize with API keys from config file"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Set brand name for analysis
        self.brand_name = brand_name
        self.brand_keywords = self._generate_brand_keywords(brand_name)
        
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
        self.spreadsheet = self.gc.open_by_key(self.config['spreadsheet_id'])
        self.sheet = None  # Will be set when creating a new worksheet for each run

    def _generate_brand_keywords(self, brand_name: str) -> List[str]:
        """Generate keywords for brand detection"""
        keywords = [brand_name.lower()]

        # Add common variations
        # Remove spaces and special characters
        no_spaces = brand_name.lower().replace(' ', '')
        if no_spaces != brand_name.lower():
            keywords.append(no_spaces)

        # Add acronym if multi-word
        words = brand_name.split()
        if len(words) > 1:
            acronym = ''.join([w[0] for w in words]).lower()
            keywords.append(acronym)

        return keywords

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
        Analyze response for brand mentions, competitors, and context
        Returns comprehensive analysis for automated sheet population
        """
        response_lower = response.lower()

        # Check for brand mentions
        brand_mentioned = any(keyword in response_lower for keyword in self.brand_keywords)

        # Get competitors based on industry (furniture brands for RH)
        competitors = self._get_competitors()

        mentioned_competitors = [comp for comp in competitors if comp.lower() in response_lower]

        # Analyze mention context (Column F)
        mention_context = self._analyze_mention_context(response, brand_mentioned)

        # Detect position (Column G)
        position = self._detect_brand_position(response, brand_mentioned)

        # Verify accuracy (Column J)
        accuracy = self._verify_brand_accuracy(response, brand_mentioned)

        # Generate automated notes (Column L)
        notes = self._generate_notes(response, brand_mentioned, mentioned_competitors)

        return {
            'bob_mentioned': 'Yes' if brand_mentioned else 'No',
            'competitors': ', '.join(mentioned_competitors) if mentioned_competitors else 'None',
            'mention_context': mention_context,
            'position': position,
            'accuracy': accuracy,
            'notes': notes
        }

    def _get_competitors(self) -> List[str]:
        """Get competitor list based on brand"""
        # Furniture brands (for Restoration Hardware)
        if any(term in self.brand_name.lower() for term in ['restoration hardware', 'rh']):
            return [
                'Pottery Barn', 'West Elm', 'Arhaus', 'Room & Board',
                'Crate and Barrel', 'CB2', 'Williams Sonoma Home',
                'Ethan Allen', 'Mitchell Gold', 'Four Hands'
            ]
        # Sunscreen brands (for Brush On Block)
        elif any(term in self.brand_name.lower() for term in ['brush on block', 'bob', 'sunscreen']):
            return [
                'Supergoop', 'ColorScience', 'Peter Thomas Roth', 'EltaMD',
                'La Roche-Posay', 'Neutrogena', 'CeraVe', 'Blue Lizard',
                'Coola', 'Sun Bum', 'Black Girl Sunscreen', 'Unseen Sunscreen'
            ]
        # Default: return empty list
        else:
            return []

    def _analyze_mention_context(self, response: str, brand_mentioned: bool) -> str:
        """Analyze how the brand is mentioned in the response (Column F)"""
        if not brand_mentioned:
            return 'Not mentioned'

        response_lower = response.lower()

        # Check for different mention contexts
        if any(phrase in response_lower for phrase in [
            'top recommendation', 'best option', 'highly recommend', 'favorite',
            'number one', '#1', 'first choice', 'top pick'
        ]):
            return 'Top recommendation'

        if any(phrase in response_lower for phrase in [
            'great option', 'good choice', 'another option', 'also consider',
            'alternatives include', 'other options'
        ]):
            return 'Listed among options'

        if any(phrase in response_lower for phrase in [
            'mentioned', 'includes', 'such as', 'like'
        ]):
            return 'Brief mention'

        if any(phrase in response_lower for phrase in [
            'compared to', 'versus', 'vs', 'unlike', 'whereas'
        ]):
            return 'In comparison'

        return 'General mention'

    def _detect_brand_position(self, response: str, brand_mentioned: bool) -> str:
        """Detect where brand appears in the response (Column G)"""
        if not brand_mentioned:
            return 'N/A'

        # Split response into sentences
        import re
        sentences = re.split(r'[.!?]+', response)

        # Find which sentence mentions the brand
        for idx, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in self.brand_keywords):
                total_sentences = len([s for s in sentences if s.strip()])

                # Determine position
                if idx < total_sentences * 0.2:
                    return f'Early (sentence {idx+1}/{total_sentences})'
                elif idx < total_sentences * 0.5:
                    return f'Middle (sentence {idx+1}/{total_sentences})'
                else:
                    return f'Late (sentence {idx+1}/{total_sentences})'

        # If not found in sentence analysis, check for list position
        lines = response.split('\n')
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in self.brand_keywords):
                # Check if it's in a numbered list
                if re.match(r'^\s*\d+\s*[.):-]', line):
                    list_num = re.match(r'^\s*(\d+)', line).group(1)
                    return f'Position #{list_num} in list'

        return 'Position unclear'

    def _verify_brand_accuracy(self, response: str, brand_mentioned: bool) -> str:
        """Verify if brand information is provided with details (Column J)"""
        if not brand_mentioned:
            return 'N/A'

        response_lower = response.lower()

        # Generic fact checking - count if specific details are mentioned
        details_mentioned = 0

        # Check for product/material mentions
        if any(term in response_lower for term in ['material', 'fabric', 'leather', 'wood', 'quality', 'product', 'powder', 'spf']):
            details_mentioned += 1

        # Check for price/value mentions
        if any(term in response_lower for term in ['price', 'cost', 'expensive', 'affordable', 'value', 'worth']):
            details_mentioned += 1

        # Check for features/attributes
        if any(term in response_lower for term in ['comfort', 'durable', 'style', 'design', 'application', 'apply']):
            details_mentioned += 1

        # Check for specific product names or collections
        if any(term in response_lower for term in ['collection', 'line', 'cloud', 'sofa', 'couch', 'furniture']):
            details_mentioned += 1

        # Determine detail level
        if details_mentioned == 0:
            return 'No details provided'
        elif details_mentioned >= 3:
            return 'Detailed'
        elif details_mentioned >= 2:
            return 'Some details'
        else:
            return 'Brief mention only'

    def _generate_notes(self, response: str, brand_mentioned: bool, competitors: List[str]) -> str:
        """Generate automated notes (Column L)"""
        notes = []

        if not brand_mentioned:
            notes.append(f'{self.brand_name} not mentioned')

            # Check if category was mentioned without the brand
            response_lower = response.lower()
            if any(term in response_lower for term in ['furniture', 'sofa', 'couch']):
                notes.append(f'Category discussed but {self.brand_name} not mentioned')
            elif 'powder' in response_lower and 'sunscreen' in response_lower:
                notes.append(f'Category discussed but {self.brand_name} not mentioned')
        else:
            # Analyze sentiment
            response_lower = response.lower()
            positive_words = ['excellent', 'great', 'best', 'recommend', 'love', 'favorite', 'top', 'quality']
            negative_words = ['however', 'but', 'unfortunately', 'limited', 'expensive', 'overpriced']

            if any(word in response_lower for word in positive_words):
                notes.append('Positive sentiment')
            if any(word in response_lower for word in negative_words):
                notes.append('Mixed/cautionary sentiment')

        # Note number of competitors
        if competitors:
            notes.append(f'{len(competitors)} competitors mentioned')

        # Check for specific features mentioned (generic)
        if any(term in response.lower() for term in ['warranty', 'guarantee', 'return']):
            notes.append('Policy/warranty mentioned')
        if any(term in response.lower() for term in ['delivery', 'shipping', 'lead time']):
            notes.append('Delivery/logistics mentioned')

        return '; '.join(notes) if notes else 'No special notes'
    
    def extract_citations(self, response: str, platform: str, citations: List = None) -> str:
        """Extract citation sources from response"""
        if platform == 'Perplexity' and citations:
            return ', '.join(citations)
        
        # For Google AI, try to extract domains from response
        # This is basic - may need refinement
        import re
        urls = re.findall(r'https?://(?:www\.)?([^\s/]+)', response)
        return ', '.join(set(urls)) if urls else 'None'
    
    def create_new_worksheet(self, run_name: str = None) -> None:
        """Create a new worksheet for this run"""
        if run_name is None:
            run_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        try:
            # Create new worksheet
            self.sheet = self.spreadsheet.add_worksheet(
                title=run_name,
                rows=1000,
                cols=12
            )

            # Add header row
            headers = [
                'Query #',
                'Query Text',
                'Platform',
                'Test Date',
                f'{self.brand_name} Mentioned?',
                'Mention Context',
                'Position',
                'Competitors Mentioned',
                'Sources Cited',
                'Accuracy',
                'Screenshot File',
                'Notes'
            ]
            self.sheet.append_row(headers)

            # Format header row (bold)
            self.sheet.format('A1:L1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })

            print(f"✓ Created new worksheet: '{run_name}'")

        except Exception as e:
            print(f"✗ Error creating worksheet: {e}")
            # Fallback to sheet1 if creation fails
            self.sheet = self.spreadsheet.sheet1

    def log_to_sheet(self, row_data: List):
        """Append a row to the Google Sheet"""
        try:
            self.sheet.append_row(row_data)
            print(f"✓ Logged to Google Sheets")
        except Exception as e:
            print(f"✗ Error logging to sheet: {e}")
    
    def run_query(self, query_num: int, query_text: str, platforms: List[str] = None,
                  create_worksheet: bool = False, run_name: str = None):
        """Run a single query across all platforms"""
        if platforms is None:
            platforms = ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']

        # Create worksheet if this is a standalone query run
        if create_worksheet:
            if run_name is None:
                run_name = f"Query_{query_num}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
            self.create_new_worksheet(run_name)

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
                analysis['mention_context'],        # F - Mention Context (auto-populated)
                analysis['position'],               # G - Position (auto-populated)
                analysis['competitors'],            # H - Competitors Mentioned
                citations,                          # I - Sources Cited
                analysis['accuracy'],               # J - Accuracy (auto-populated)
                screenshot_file,                    # K - Screenshot File
                analysis['notes']                   # L - Notes (auto-populated)
            ]
            
            # Log to Google Sheets
            self.log_to_sheet(row_data)
            
            # Small delay between API calls
            time.sleep(2)
        
        print(f"\n✓ Completed Query #{query_num}\n")
    
    def run_batch(self, queries: List[Dict], run_name: str = None):
        """Run multiple queries"""
        print(f"\n🚀 Starting batch processing of {len(queries)} queries\n")

        # Create a new worksheet for this run
        if run_name is None:
            run_name = f"Run_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"

        self.create_new_worksheet(run_name)

        for query in queries:
            self.run_query(query['num'], query['text'], query.get('platforms'))

        print(f"\n✅ Batch complete! Check worksheet '{run_name}' and screenshots folder.\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Query Tracker - Track brand mentions across AI platforms')
    parser.add_argument('--queries', '-q',
                        default='queries.json',
                        help='Path to queries JSON file (default: queries.json)')
    parser.add_argument('--config', '-c',
                        default='config.json',
                        help='Path to config JSON file (default: config.json)')
    parser.add_argument('--run-name', '-r',
                        help='Custom name for this run (default: auto-generated timestamp)')
    parser.add_argument('--brand', '-b',
                        default='Brush On Block',
                        help='Brand name to track (default: Brush On Block)')

    args = parser.parse_args()

    # Initialize tracker
    tracker = AIQueryTracker(args.config, brand_name=args.brand)

    # Load queries from file
    with open(args.queries, 'r') as f:
        queries = json.load(f)

    # Run batch
    tracker.run_batch(queries, run_name=args.run_name)


if __name__ == '__main__':
    main()
