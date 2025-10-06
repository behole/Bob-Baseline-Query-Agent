#!/usr/bin/env python3
"""
Quick Query Runner - Test a single query across platforms
Usage: python quick_query.py "Your question here"
"""

import sys
from ai_query_tracker import AIQueryTracker

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_query.py \"Your question here\"")
        print("\nExample:")
        print('  python quick_query.py "What is the best powder sunscreen?"')
        sys.exit(1)
    
    query_text = sys.argv[1]
    
    # Optional: specify platforms as additional arguments
    if len(sys.argv) > 2:
        platforms = sys.argv[2:]
    else:
        platforms = ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']
    
    print(f"\n🚀 Running quick query across {len(platforms)} platforms...")
    print(f"Query: {query_text}\n")
    
    # Initialize tracker
    tracker = AIQueryTracker('config.json')
    
    # Run the query
    tracker.run_query(
        query_num=999,  # Use 999 for quick tests
        query_text=query_text,
        platforms=platforms
    )
    
    print("\n✅ Done! Check your Google Sheet and screenshots folder.")

if __name__ == '__main__':
    main()
