#!/usr/bin/env python3
"""
V2 GEO Audit CLI

Automated competitor discovery and gap analysis for any brand.

Usage:
    python v2_audit.py --brand "Nike" --industry athletic_wear \\
        --categories "running shoes,athletic wear,sneakers"

Full automation:
    python v2_audit.py --brand "Nike" --industry athletic_wear \\
        --categories "running shoes,athletic wear" \\
        --auto  # Generates queries, executes (when integrated), analyzes, reports
"""

import argparse
import os
import sys
from pathlib import Path

from geo_audit.v2.orchestrator import V2AuditOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description='V2 GEO Audit - Automated Competitor Discovery & Gap Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate queries only
  python v2_audit.py --brand "Nike" --industry athletic_wear \\
      --categories "running shoes,sneakers,athletic wear"

  # Full audit with existing results
  python v2_audit.py --brand "Nike" --industry athletic_wear \\
      --categories "running shoes,sneakers" \\
      --results path/to/query_results.json

  # Customize output
  python v2_audit.py --brand "Rivian" --industry automotive \\
      --categories "electric vehicles,SUVs,trucks" \\
      --queries 80 --competitors 10 --output reports/rivian

Industries:
  athletic_wear, automotive, furniture, sunscreen, skincare,
  fashion, electronics, travel, real_estate, financial_services
        """
    )

    # Required arguments
    parser.add_argument(
        '--brand',
        required=True,
        help='Brand name (e.g., "Nike", "Rivian", "Restoration Hardware")'
    )

    parser.add_argument(
        '--industry',
        required=True,
        help='Industry category (e.g., athletic_wear, automotive, furniture)'
    )

    parser.add_argument(
        '--categories',
        required=True,
        help='Comma-separated product categories (e.g., "running shoes,sneakers,athletic wear")'
    )

    # Optional arguments
    parser.add_argument(
        '--queries',
        type=int,
        default=60,
        help='Total number of queries to generate (default: 60)'
    )

    parser.add_argument(
        '--competitors',
        type=int,
        default=7,
        help='Maximum competitors to analyze (default: 7)'
    )

    parser.add_argument(
        '--gaps',
        type=int,
        default=3,
        help='Maximum priority gaps per competitor (default: 3)'
    )

    parser.add_argument(
        '--results',
        help='Path to query results JSON file (if already executed)'
    )

    parser.add_argument(
        '--output',
        default='reports',
        help='Output directory for reports (default: reports/)'
    )

    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )

    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip query generation (use with --results for analysis only)'
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
    if not api_key and not args.skip_generation:
        print("❌ Error: Anthropic API key required for query generation")
        print("   Set ANTHROPIC_API_KEY environment variable or use --api-key")
        sys.exit(1)

    # Parse product categories
    product_categories = [c.strip() for c in args.categories.split(',')]

    # Print configuration
    print("\n" + "="*60)
    print("V2 GEO AUDIT CONFIGURATION")
    print("="*60)
    print(f"Brand:       {args.brand}")
    print(f"Industry:    {args.industry}")
    print(f"Categories:  {', '.join(product_categories)}")
    print(f"Queries:     {args.queries}")
    print(f"Max Competitors: {args.competitors}")
    print(f"Max Gaps/Competitor: {args.gaps}")
    if args.results:
        print(f"Results File: {args.results}")
    print(f"Output Dir:  {args.output}")
    print("="*60 + "\n")

    # Initialize orchestrator
    orchestrator = V2AuditOrchestrator(
        brand_name=args.brand,
        industry=args.industry,
        anthropic_api_key=api_key or "",  # Empty if skipping generation
        output_dir=args.output
    )

    try:
        # Run audit
        results = orchestrator.run_full_audit(
            product_categories=product_categories,
            total_queries=args.queries,
            max_competitors=args.competitors,
            max_gaps_per_competitor=args.gaps,
            query_results_path=args.results,
            skip_query_generation=args.skip_generation
        )

        # Print summary
        if results['status'] == 'complete':
            print("\n" + "="*60)
            print("🎉 AUDIT SUMMARY")
            print("="*60)
            print(f"Total Queries:        {results['total_queries']}")
            print(f"Competitors Found:    {results['competitors_discovered']}")
            print(f"Top Competitor:       {results['top_competitor']}")
            print(f"Market Share:         {results['market_share']:.1f}%")
            print(f"Gaps Identified:      {results['gaps_identified']}")
            print(f"Recommendations:      {results['recommendations']}")
            print(f"\n📊 Report: {results['report_path']}")
            print("="*60 + "\n")
        elif results['status'] == 'pending_execution':
            print("\n⏸️  Audit paused - query execution needed")
            print(f"   {results['queries_generated']} queries generated")
            print(f"   Next: {results['next_step']}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
