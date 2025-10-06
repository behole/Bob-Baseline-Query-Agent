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
        self.spreadsheet = self.gc.open_by_key(self.config['spreadsheet_id'])
        self.sheet = None  # Will be set when creating a new worksheet for each run
        
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
        Analyze response for BOB mentions, competitors, and context
        Returns comprehensive analysis for automated sheet population
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

        # Analyze mention context (Column F)
        mention_context = self._analyze_mention_context(response, bob_mentioned)

        # Detect position (Column G)
        position = self._detect_bob_position(response, bob_mentioned)

        # Verify accuracy (Column J)
        accuracy = self._verify_bob_accuracy(response, bob_mentioned)

        # Generate automated notes (Column L)
        notes = self._generate_notes(response, bob_mentioned, mentioned_competitors)

        return {
            'bob_mentioned': 'Yes' if bob_mentioned else 'No',
            'competitors': ', '.join(mentioned_competitors) if mentioned_competitors else 'None',
            'mention_context': mention_context,
            'position': position,
            'accuracy': accuracy,
            'notes': notes
        }

    def _analyze_mention_context(self, response: str, bob_mentioned: bool) -> str:
        """Analyze how BOB is mentioned in the response (Column F)"""
        if not bob_mentioned:
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

    def _detect_bob_position(self, response: str, bob_mentioned: bool) -> str:
        """Detect where BOB appears in the response (Column G)"""
        if not bob_mentioned:
            return 'N/A'

        # Split response into sentences
        import re
        sentences = re.split(r'[.!?]+', response)

        # Find which sentence mentions BOB
        bob_keywords = ['brush on block', 'brushonblock', 'bob']
        for idx, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in bob_keywords):
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
            if any(keyword in line_lower for keyword in bob_keywords):
                # Check if it's in a numbered list
                if re.match(r'^\s*\d+\s*[.):-]', line):
                    list_num = re.match(r'^\s*(\d+)', line).group(1)
                    return f'Position #{list_num} in list'

        return 'Position unclear'

    def _verify_bob_accuracy(self, response: str, bob_mentioned: bool) -> str:
        """Verify if BOB information is accurate (Column J)"""
        if not bob_mentioned:
            return 'N/A'

        response_lower = response.lower()

        # Key BOB facts to check
        accurate_facts = 0
        total_facts_mentioned = 0

        # Check for product type mentions
        if 'powder' in response_lower or 'mineral' in response_lower:
            total_facts_mentioned += 1
            if 'powder' in response_lower:
                accurate_facts += 1

        # Check for SPF mentions
        if 'spf' in response_lower:
            total_facts_mentioned += 1
            # BOB products typically have SPF 30 or higher
            if any(spf in response_lower for spf in ['spf 30', 'spf 50', 'spf 90']):
                accurate_facts += 1

        # Check for application method
        if 'brush' in response_lower or 'apply' in response_lower:
            total_facts_mentioned += 1
            accurate_facts += 1

        # Check for skin type mentions
        if any(skin_type in response_lower for skin_type in ['oily', 'sensitive', 'all skin']):
            total_facts_mentioned += 1
            accurate_facts += 1

        # Determine accuracy level
        if total_facts_mentioned == 0:
            return 'No details provided'

        accuracy_ratio = accurate_facts / total_facts_mentioned

        if accuracy_ratio >= 0.8:
            return 'Accurate'
        elif accuracy_ratio >= 0.5:
            return 'Partially accurate'
        else:
            return 'Review needed'

    def _generate_notes(self, response: str, bob_mentioned: bool, competitors: List[str]) -> str:
        """Generate automated notes (Column L)"""
        notes = []

        if not bob_mentioned:
            notes.append('BOB not mentioned')

            # Check if powder sunscreen was mentioned without BOB
            if 'powder' in response.lower() and 'sunscreen' in response.lower():
                notes.append('Powder sunscreen discussed but BOB not mentioned')
        else:
            # Analyze sentiment
            response_lower = response.lower()
            positive_words = ['excellent', 'great', 'best', 'recommend', 'love', 'favorite', 'top']
            negative_words = ['however', 'but', 'unfortunately', 'limited', 'expensive']

            if any(word in response_lower for word in positive_words):
                notes.append('Positive sentiment')
            if any(word in response_lower for word in negative_words):
                notes.append('Mixed/negative sentiment')

        # Note number of competitors
        if competitors:
            notes.append(f'{len(competitors)} competitors mentioned')

        # Check for specific features mentioned
        if 'reapplication' in response.lower():
            notes.append('Reapplication mentioned')
        if 'travel' in response.lower() or 'portable' in response.lower():
            notes.append('Portability mentioned')

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
                'BOB Mentioned?',
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

    args = parser.parse_args()

    # Initialize tracker
    tracker = AIQueryTracker(args.config)

    # Load queries from file
    with open(args.queries, 'r') as f:
        queries = json.load(f)

    # Run batch
    tracker.run_batch(queries, run_name=args.run_name)


if __name__ == '__main__':
    main()
