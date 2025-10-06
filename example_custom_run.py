#!/usr/bin/env python3
"""
Example script showing how to use custom worksheet names for different tracking scenarios
"""

from ai_query_tracker import AIQueryTracker

def main():
    # Initialize tracker
    tracker = AIQueryTracker('config.json')

    # Example 1: Weekly tracking with custom name
    queries_week1 = [
        {"num": 1, "text": "What is the best powder sunscreen?"},
        {"num": 2, "text": "Best sunscreen for oily skin?"}
    ]

    print("Running weekly tracking...")
    tracker.run_batch(queries_week1, run_name="Week_1_Baseline")

    # Example 2: A/B testing different query phrasings
    # You could run this later to test query variations
    # queries_variation = [
    #     {"num": 1, "text": "Top powder sunscreen recommendations?"},
    #     {"num": 2, "text": "Sunscreen for oily sensitive skin?"}
    # ]
    # tracker.run_batch(queries_variation, run_name="Query_Variation_Test")

    # Example 3: Single query test with custom name
    # tracker.run_query(
    #     query_num=99,
    #     query_text="Best travel-size powder sunscreen?",
    #     create_worksheet=True,
    #     run_name="Travel_Product_Test"
    # )

if __name__ == '__main__':
    main()
