#!/usr/bin/env python3
"""
Helper script to get and manage competitors for an industry
"""

import sys
import json
from geo_audit.utils.competitors import get_competitors, COMPETITOR_DB

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 get_competitors.py <industry>", file=sys.stderr)
        sys.exit(1)

    industry = sys.argv[1].lower()

    # Get competitors for industry
    competitors = get_competitors("", industry=industry)

    if not competitors:
        # Try to find partial match
        for key in COMPETITOR_DB.keys():
            if industry in key or key in industry:
                competitors = COMPETITOR_DB[key]
                break

    # Output as comma-separated list
    if competitors:
        print(",".join(competitors))
    else:
        print("")  # Empty if no competitors found

if __name__ == '__main__':
    main()
