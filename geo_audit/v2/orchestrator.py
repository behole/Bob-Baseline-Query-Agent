"""
V2 Orchestrator

Coordinates the entire V2 automated audit workflow:
1. Query generation
2. Query execution
3. Competitor discovery
4. Gap analysis
5. Recommendation generation
6. Report creation
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.query_generator import QueryGenerator
from ..utils.competitors import get_competitors
from .discovery.competitor_discovery import CompetitorDiscovery
from .analysis.gap_analysis import GapAnalyzer
from .analysis.recommendations import RecommendationEngine
from .reporting.report_generator import V2ReportGenerator


class V2AuditOrchestrator:
    """
    Orchestrates the complete V2 automated audit workflow
    """

    def __init__(
        self,
        brand_name: str,
        industry: str,
        anthropic_api_key: str,
        output_dir: str = "reports"
    ):
        """
        Initialize V2 orchestrator

        Args:
            brand_name: Target brand name
            industry: Industry category (e.g., 'athletic_wear', 'automotive')
            anthropic_api_key: API key for Claude (query generation)
            output_dir: Directory for output files
        """
        self.brand_name = brand_name
        self.industry = industry
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize modules
        self.query_generator = QueryGenerator(api_key=anthropic_api_key)
        self.competitor_discovery = CompetitorDiscovery(
            target_brand=brand_name,
            industry=industry
        )
        self.gap_analyzer = GapAnalyzer(target_brand=brand_name)
        self.rec_engine = RecommendationEngine()
        self.report_generator = V2ReportGenerator(
            brand_name=brand_name,
            industry=industry
        )

    def run_full_audit(
        self,
        product_categories: List[str],
        total_queries: int = 60,
        max_competitors: int = 7,
        max_gaps_per_competitor: int = 3,
        query_results_path: Optional[str] = None,
        skip_query_generation: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete V2 audit workflow

        Args:
            product_categories: List of product categories for query generation
            total_queries: Total number of queries to generate
            max_competitors: Maximum competitors to analyze
            max_gaps_per_competitor: Max priority gaps per competitor
            query_results_path: Optional path to pre-executed query results JSON
            skip_query_generation: Skip query generation (use existing file)

        Returns:
            Dictionary with audit results
        """
        print("\n" + "="*60)
        print(f"🚀 Starting V2 Automated Audit: {self.brand_name}")
        print("="*60)

        # Step 1: Generate or load queries
        if skip_query_generation and query_results_path:
            print("\n📋 Loading existing queries...")
            queries = self._load_queries(query_results_path)
        else:
            print("\n📋 Step 1: Generating Queries")
            queries = self._generate_queries(product_categories, total_queries)

        # Step 2: Execute queries (placeholder - needs integration with existing tracker)
        print("\n🔍 Step 2: Executing Queries")
        if query_results_path and Path(query_results_path).exists():
            print(f"   Loading results from: {query_results_path}")
            query_results = self._load_query_results(query_results_path)
        else:
            print("   ⚠️  Query execution requires integration with existing tracker")
            print("   For now, please run queries using existing system and provide results file")
            return {
                'status': 'pending_execution',
                'queries_generated': len(queries),
                'next_step': 'Execute queries and provide results JSON file'
            }

        # Step 3: Discover competitors
        print("\n🎯 Step 3: Discovering Competitors")
        competitors = self.competitor_discovery.discover_from_results(
            query_results=query_results,
            max_competitors=max_competitors
        )
        print(f"   Discovered {len(competitors)} competitors:")
        for i, comp in enumerate(competitors, 1):
            print(f"   #{i} {comp.brand_name}: {comp.mention_rate:.1f}% share, avg rank #{comp.avg_ranking:.1f}")

        # Step 4: Analyze gaps
        print("\n📊 Step 4: Analyzing Competitive Gaps")
        all_gap_clusters = []
        for comp in competitors:
            print(f"   Analyzing vs {comp.brand_name}...")
            gaps = self.gap_analyzer.identify_gaps(
                query_results=query_results,
                competitor_name=comp.brand_name,
                max_priority_gaps=max_gaps_per_competitor
            )
            all_gap_clusters.extend(gaps)
            print(f"      Found {len(gaps)} priority gaps")

        # Step 5: Generate recommendations
        print("\n💡 Step 5: Generating Recommendations")
        recommendations = self.rec_engine.generate_recommendations(
            gap_clusters=all_gap_clusters,
            target_brand=self.brand_name
        )
        print(f"   Generated {len(recommendations)} prioritized recommendations")

        # Step 6: Calculate query stats
        query_stats = self._calculate_query_stats(queries, query_results)

        # Step 7: Generate report
        print("\n📄 Step 6: Generating Report")
        report_path = self.output_dir / f"{self.brand_name.lower().replace(' ', '_')}_v2_geo_report.html"
        self.report_generator.generate_report(
            competitors=competitors,
            all_gap_clusters=all_gap_clusters,
            recommendations=recommendations,
            query_stats=query_stats,
            output_path=str(report_path)
        )

        print("\n" + "="*60)
        print("✅ V2 Audit Complete!")
        print(f"📊 Report saved to: {report_path}")
        print("="*60 + "\n")

        return {
            'status': 'complete',
            'brand': self.brand_name,
            'industry': self.industry,
            'total_queries': len(queries),
            'competitors_discovered': len(competitors),
            'gaps_identified': len(all_gap_clusters),
            'recommendations': len(recommendations),
            'report_path': str(report_path),
            'top_competitor': competitors[0].brand_name if competitors else None,
            'market_share': query_stats.get('generic_mention_rate', 0)
        }

    def _generate_queries(
        self,
        product_categories: List[str],
        total_queries: int
    ) -> List[Dict[str, Any]]:
        """Generate queries using QueryGenerator"""

        # For V2, we only generate branded and generic (no manual competitor queries)
        queries = self.query_generator.generate_queries(
            brand_name=self.brand_name,
            industry=self.industry,
            product_categories=product_categories,
            competitors=[],  # Empty - we'll discover competitors
            total_queries=total_queries,
            include_types=['generic', 'branded']  # Only these two types
        )

        # Add category field
        for query in queries:
            query_text = query['text'].lower()
            if self.brand_name.lower() in query_text:
                query['category'] = 'branded'
            else:
                query['category'] = 'generic'

        # Save queries
        queries_path = self.output_dir / f"{self.brand_name.lower().replace(' ', '_')}_queries_v2.json"
        with open(queries_path, 'w') as f:
            json.dump(queries, f, indent=2)

        print(f"   ✅ Generated {len(queries)} queries")
        print(f"   💾 Saved to: {queries_path}")

        return queries

    def _load_queries(self, path: str) -> List[Dict[str, Any]]:
        """Load queries from JSON file"""
        with open(path, 'r') as f:
            return json.load(f)

    def _load_query_results(self, path: str) -> List[Dict[str, Any]]:
        """
        Load query results from JSON file

        Expected format:
        [
            {
                "query": "best running shoes",
                "category": "generic",
                "responses": {
                    "Claude": "Nike is...",
                    "ChatGPT": "Adidas offers...",
                    ...
                }
            },
            ...
        ]
        """
        with open(path, 'r') as f:
            return json.load(f)

    def _calculate_query_stats(
        self,
        queries: List[Dict[str, Any]],
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate query statistics"""

        branded_queries = [q for q in queries if q.get('category') == 'branded']
        generic_queries = [q for q in queries if q.get('category') == 'generic']

        # Count brand mentions
        branded_mentions = 0
        branded_total = 0
        generic_mentions = 0
        generic_total = 0

        for result in results:
            category = result.get('category', '')
            brand_lower = self.brand_name.lower()

            for platform, response in result.get('responses', {}).items():
                if not response:
                    continue

                response_lower = response.lower()

                if category == 'branded':
                    branded_total += 1
                    if brand_lower in response_lower:
                        branded_mentions += 1
                elif category == 'generic':
                    generic_total += 1
                    if brand_lower in response_lower:
                        generic_mentions += 1

        return {
            'total_queries': len(queries),
            'branded_count': len(branded_queries),
            'generic_count': len(generic_queries),
            'branded_mention_rate': (branded_mentions / branded_total * 100) if branded_total > 0 else 0,
            'generic_mention_rate': (generic_mentions / generic_total * 100) if generic_total > 0 else 0
        }


def run_v2_audit(
    brand_name: str,
    industry: str,
    product_categories: List[str],
    anthropic_api_key: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to run V2 audit

    Args:
        brand_name: Target brand
        industry: Industry category
        product_categories: Product categories for query generation
        anthropic_api_key: Claude API key
        **kwargs: Additional arguments for run_full_audit()

    Returns:
        Audit results dictionary
    """
    orchestrator = V2AuditOrchestrator(
        brand_name=brand_name,
        industry=industry,
        anthropic_api_key=anthropic_api_key
    )

    return orchestrator.run_full_audit(
        product_categories=product_categories,
        **kwargs
    )
