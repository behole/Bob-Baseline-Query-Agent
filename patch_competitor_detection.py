#!/usr/bin/env python3
"""
Patch existing Google Sheets data to add competitor detection
Re-analyzes responses that are already saved but have missing competitor data
"""

import gspread
import json
import sys
from google.oauth2.service_account import Credentials
from geo_audit.utils.competitors import get_competitors, detect_industry

def patch_sheet(worksheet_name: str, brand_name: str):
    """Re-analyze existing responses and update competitor mentions"""

    # Load config
    with open('config.json') as f:
        config = json.load(f)

    # Connect to Google Sheets
    creds = Credentials.from_service_account_file(
        config['google_credentials_path'],
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(config['spreadsheet_id']).worksheet(worksheet_name)

    print(f"🔧 PATCHING COMPETITOR DETECTION")
    print("=" * 80)
    print(f"Worksheet: {worksheet_name}")
    print(f"Brand: {brand_name}")
    print()

    # Get competitors for this brand
    industry = detect_industry(brand_name)
    competitors = get_competitors(brand_name, industry=industry)

    print(f"Industry: {industry}")
    print(f"Competitors: {len(competitors)} brands")
    print(f"  {', '.join(competitors[:10])}...")
    print()

    # Get all data
    data = sheet.get_all_records()
    print(f"Total rows: {len(data)}")
    print()

    # Find the column index for "Competitors Mentioned"
    headers = sheet.row_values(1)
    try:
        competitor_col_idx = headers.index('Competitors Mentioned') + 1  # 1-indexed
    except ValueError:
        print("❌ Error: 'Competitors Mentioned' column not found")
        return

    # Re-analyze each row and collect updates
    batch_updates = []
    competitors_found = 0

    print("Analyzing responses...")
    for i, row in enumerate(data, start=2):  # Start at row 2 (1 is header)
        response = row.get('Response', '')
        current_competitors = row.get('Competitors Mentioned', '')

        if not response:
            continue

        # Detect competitors in response
        response_lower = response.lower()
        mentioned_competitors = [comp for comp in competitors if comp.lower() in response_lower]

        # Update if different from current value
        new_value = ', '.join(mentioned_competitors) if mentioned_competitors else 'None'

        if new_value != current_competitors:
            # Add to batch updates
            batch_updates.append({
                'range': f'{chr(64 + competitor_col_idx)}{i}',  # e.g., 'H2'
                'values': [[new_value]]
            })

            if mentioned_competitors:
                competitors_found += 1
                print(f"  ✅ Row {i}: Found {len(mentioned_competitors)} competitors - {', '.join(mentioned_competitors)}")

        # Progress indicator
        if i % 20 == 0:
            print(f"  ... analyzed {i-1} rows")

    # Perform batch update
    print()
    print(f"Updating {len(batch_updates)} cells in Google Sheets...")
    if batch_updates:
        sheet.batch_update(batch_updates)
    updates_made = len(batch_updates)

    print()
    print("=" * 80)
    print(f"✅ PATCH COMPLETE!")
    print(f"  Rows updated: {updates_made}")
    print(f"  Rows with competitors: {competitors_found}")
    print()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 patch_competitor_detection.py <worksheet_name> <brand_name>")
        print()
        print("Example:")
        print("  python3 patch_competitor_detection.py marriott_audit_FIXED Marriott")
        sys.exit(1)

    worksheet_name = sys.argv[1]
    brand_name = sys.argv[2]

    patch_sheet(worksheet_name, brand_name)
