#!/usr/bin/env python3
"""
Test script to verify the enhanced analysis functions
"""

from ai_query_tracker import AIQueryTracker

# Sample responses to test
test_responses = [
    {
        "name": "Top Recommendation",
        "response": "For powder sunscreen, I highly recommend Brush on Block. It's my top pick for oily skin with SPF 30 protection. The brush applicator makes it easy to apply and reapply throughout the day."
    },
    {
        "name": "Listed Among Options",
        "response": "Here are some great powder sunscreens:\n1. Supergoop Invincible Setting Powder\n2. ColorScience Sunforgettable\n3. Brush on Block SPF 30\n4. Peter Thomas Roth Instant Mineral\n\nAll are good choices for travel."
    },
    {
        "name": "Not Mentioned",
        "response": "For powder sunscreen, I recommend Supergoop and ColorScience. Both offer excellent mineral-based protection and are great for oily skin types."
    },
    {
        "name": "Brief Mention",
        "response": "Powder sunscreens like Supergoop, Brush on Block, and ColorScience are convenient for reapplication. They work well for touch-ups during the day."
    }
]

def test_analysis():
    """Test the analysis functions"""
    print("Testing Enhanced Analysis Functions")
    print("=" * 80)

    # Initialize tracker (just for using the analysis methods)
    try:
        tracker = AIQueryTracker('config.json')

        for test in test_responses:
            print(f"\n\n{test['name'].upper()}")
            print("-" * 80)
            print(f"Response: {test['response'][:100]}...")
            print()

            # Run analysis
            analysis = tracker.analyze_response(test['response'])

            # Display results
            print(f"BOB Mentioned: {analysis['bob_mentioned']}")
            print(f"Mention Context: {analysis['mention_context']}")
            print(f"Position: {analysis['position']}")
            print(f"Competitors: {analysis['competitors']}")
            print(f"Accuracy: {analysis['accuracy']}")
            print(f"Notes: {analysis['notes']}")

    except FileNotFoundError:
        print("\n⚠️  config.json not found. Testing analysis methods directly...")
        print("Create a minimal tracker for testing purposes\n")

        # Test the analysis methods without full initialization
        class MinimalTracker(AIQueryTracker):
            def __init__(self):
                # Skip API initialization
                pass

        tracker = MinimalTracker()

        for test in test_responses:
            print(f"\n\n{test['name'].upper()}")
            print("-" * 80)
            print(f"Response: {test['response'][:100]}...")
            print()

            # Run analysis
            analysis = tracker.analyze_response(test['response'])

            # Display results
            print(f"BOB Mentioned: {analysis['bob_mentioned']}")
            print(f"Mention Context: {analysis['mention_context']}")
            print(f"Position: {analysis['position']}")
            print(f"Competitors: {analysis['competitors']}")
            print(f"Accuracy: {analysis['accuracy']}")
            print(f"Notes: {analysis['notes']}")

    print("\n\n" + "=" * 80)
    print("✓ Testing complete!")

if __name__ == '__main__':
    test_analysis()
