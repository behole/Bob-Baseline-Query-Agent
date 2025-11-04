#!/usr/bin/env python3
"""
Quick Query Runner - Test a single query across platforms
Usage: python quick_query.py "Your question here" --brand "Brand Name"
"""

import sys
import argparse
from ai_query_tracker import AIQueryTracker

def main():
    parser = argparse.ArgumentParser(description='Quick query test across AI platforms')
    parser.add_argument('query', help='Question to ask')
    parser.add_argument('--brand', '-b', default='Brush On Block',
                        help='Brand name to track (default: Brush On Block)')
    parser.add_argument('--config', '-c', default='config.json',
                        help='Path to config file (default: config.json)')

    args = parser.parse_args()

    platforms = ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']

    print(f"\n🚀 Running quick query across {len(platforms)} platforms...")
    print(f"Query: {args.query}")
    print(f"Tracking brand: {args.brand}\n")

    # Initialize tracker with brand name
    tracker = AIQueryTracker(args.config, brand_name=args.brand)
    
    # Run the query
    tracker.run_query(
        query_num=999,  # Use 999 for quick tests
        query_text=args.query,
        platforms=platforms
    )
    
    print("\n✅ Done! Check your Google Sheet and screenshots folder.")

if __name__ == '__main__':
    main()
