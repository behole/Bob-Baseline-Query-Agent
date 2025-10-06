#!/usr/bin/env python3
"""
Test Perplexity API connection specifically
"""

import json
import requests

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

print("Testing Perplexity API...\n")
print(f"API Key (first 10 chars): {config['perplexity_api_key'][:10]}...\n")

url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Authorization": f"Bearer {config['perplexity_api_key']}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.1-sonar-small-128k-online",
    "messages": [
        {"role": "user", "content": "What is the best powder sunscreen?"}
    ]
}

print("Sending request to Perplexity...\n")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code != 200:
        print(f"Error Response: {response.text}\n")
    else:
        data = response.json()
        print("✓ Success!")
        print(f"\nResponse: {data['choices'][0]['message']['content'][:200]}...")
        print(f"\nCitations: {data.get('citations', [])}")
        
except Exception as e:
    print(f"✗ Exception occurred: {str(e)}")
