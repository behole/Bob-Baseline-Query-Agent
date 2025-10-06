#!/usr/bin/env python3
"""
Setup Verification Script
Tests all API connections and Google Sheets access
"""

import json
import sys
from datetime import datetime

def test_config():
    """Test if config file exists and is valid"""
    print("1. Testing config.json...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = [
            'anthropic_api_key',
            'openai_api_key', 
            'google_api_key',
            'perplexity_api_key',
            'google_credentials_path',
            'spreadsheet_id'
        ]
        
        missing = [key for key in required_keys if not config.get(key) or config[key].startswith('YOUR_')]
        
        if missing:
            print(f"   ✗ Missing or placeholder values: {', '.join(missing)}")
            return False
        else:
            print("   ✓ config.json is valid")
            return True
            
    except FileNotFoundError:
        print("   ✗ config.json not found")
        return False
    except json.JSONDecodeError:
        print("   ✗ config.json is not valid JSON")
        return False

def test_anthropic(api_key):
    """Test Anthropic API connection"""
    print("\n2. Testing Anthropic (Claude) API...")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": "Say 'test successful' and nothing else"}]
        )
        response = message.content[0].text
        print(f"   ✓ Claude API working - Response: {response[:50]}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_openai(api_key):
    """Test OpenAI API connection"""
    print("\n3. Testing OpenAI (ChatGPT) API...")
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[{"role": "user", "content": "Say 'test successful' and nothing else"}],
            max_tokens=100
        )
        text = response.choices[0].message.content
        print(f"   ✓ ChatGPT API working - Response: {text[:50]}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_gemini(api_key):
    """Test Google Gemini API connection"""
    print("\n4. Testing Google AI (Gemini) API...")
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="Say 'test successful' and nothing else"
        )
        text = response.text
        print(f"   ✓ Gemini API working - Response: {text[:50]}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_perplexity(api_key):
    """Test Perplexity API connection"""
    print("\n5. Testing Perplexity API...")
    try:
        import requests
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar",  # Use the working model
            "messages": [{"role": "user", "content": "Say 'test successful' and nothing else"}],
            "max_tokens": 50
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        text = data['choices'][0]['message']['content']
        print(f"   ✓ Perplexity API working - Response: {text[:50]}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Request Error: {str(e)}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_google_sheets(credentials_path, spreadsheet_id):
    """Test Google Sheets access"""
    print("\n6. Testing Google Sheets access...")
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(spreadsheet_id).sheet1
        
        # Try to read the first row
        headers = sheet.row_values(1)
        print(f"   ✓ Google Sheets accessible - Found {len(headers)} columns")
        
        # Verify headers match expected format
        expected_headers = [
            'Query #', 'Query Text', 'Platform', 'Test Date', 
            'BOB Mentioned?', 'Mention Context', 'Position', 
            'Competitors Mentioned', 'Sources Cited', 'Accuracy', 
            'Screenshot File', 'Notes'
        ]
        
        if headers == expected_headers:
            print(f"   ✓ Column headers are correct")
        else:
            print(f"   ⚠ Warning: Column headers don't match expected format")
            print(f"      Expected: {expected_headers}")
            print(f"      Found: {headers}")
        
        return True
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        print(f"\n   Make sure to:")
        print(f"   1. Share your Google Sheet with the service account email")
        print(f"   2. Give it 'Editor' permissions")
        return False

def test_screenshot_creation():
    """Test screenshot functionality"""
    print("\n7. Testing screenshot creation...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        import os
        
        os.makedirs('screenshots', exist_ok=True)
        
        # Create a simple test image
        img = Image.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "Test Screenshot", fill='black')
        
        test_file = 'screenshots/test_screenshot.png'
        img.save(test_file)
        
        if os.path.exists(test_file):
            print(f"   ✓ Screenshot creation working - Saved to {test_file}")
            os.remove(test_file)  # Clean up
            return True
        else:
            print(f"   ✗ Failed to create screenshot")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI Query Tracker - Setup Verification")
    print("="*60 + "\n")
    
    results = []
    
    # Test 1: Config file
    if not test_config():
        print("\n❌ Setup incomplete. Please configure config.json first.")
        sys.exit(1)
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Test 2-5: API connections
    results.append(("Anthropic API", test_anthropic(config['anthropic_api_key'])))
    results.append(("OpenAI API", test_openai(config['openai_api_key'])))
    results.append(("Google AI API", test_gemini(config['google_api_key'])))
    results.append(("Perplexity API", test_perplexity(config['perplexity_api_key'])))
    
    # Test 6: Google Sheets
    results.append(("Google Sheets", test_google_sheets(
        config['google_credentials_path'], 
        config['spreadsheet_id']
    )))
    
    # Test 7: Screenshots
    results.append(("Screenshot Creation", test_screenshot_creation()))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the tracker.")
        print("   Run: python ai_query_tracker.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before running the tracker.")
        sys.exit(1)

if __name__ == '__main__':
    main()
