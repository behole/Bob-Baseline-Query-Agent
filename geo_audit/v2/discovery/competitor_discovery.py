"""
Automated Competitor Discovery Engine

Analyzes generic query results to automatically discover and rank competitors
based on mention frequency, ranking position, and response quality.
"""

import re
from typing import List, Dict, Any, Set, Optional
from collections import defaultdict
from dataclasses import dataclass, field

from geo_audit.utils.competitors import COMPETITOR_DB


@dataclass
class CompetitorMetrics:
    """Metrics for a discovered competitor"""
    brand_name: str
    mention_count: int = 0
    total_queries: int = 0
    mention_rate: float = 0.0
    ranking_positions: List[int] = field(default_factory=list)
    avg_ranking: float = 0.0
    response_details: List[str] = field(default_factory=list)
    avg_detail_score: float = 0.0
    sentiment_scores: List[float] = field(default_factory=list)
    avg_sentiment: float = 0.0
    competitiveness_score: float = 0.0
    queries_appeared_in: List[str] = field(default_factory=list)


class CompetitorDiscovery:
    """
    Automated competitor discovery from query results

    Uses hybrid approach:
    1. Industry seed list for validation
    2. Pattern-based brand extraction from responses
    3. Competitive ranking algorithm
    """

    def __init__(self, target_brand: str, industry: str):
        """
        Initialize competitor discovery

        Args:
            target_brand: The brand being audited
            industry: Industry category (e.g., 'athletic_wear', 'automotive')
        """
        self.target_brand = target_brand
        self.industry = industry

        # Get industry seed list for validation
        self.industry_brands = set(COMPETITOR_DB.get(industry, []))

        # Add common brand patterns for detection
        self.brand_patterns = self._build_brand_patterns()

    def _build_brand_patterns(self) -> List[re.Pattern]:
        """Build regex patterns for brand detection"""
        patterns = []

        # Pattern for brands from seed list
        for brand in self.industry_brands:
            # Create pattern that matches brand name with word boundaries
            pattern = re.compile(
                r'\b' + re.escape(brand) + r'\b',
                re.IGNORECASE
            )
            patterns.append((brand, pattern))

        return patterns

    def discover_from_results(
        self,
        query_results: List[Dict[str, Any]],
        max_competitors: int = 7
    ) -> List[CompetitorMetrics]:
        """
        Discover competitors from generic query results

        Args:
            query_results: List of query result dictionaries containing:
                - query: str
                - category: str (should be 'generic' for discovery)
                - responses: Dict[platform, response_text]
                - rankings: Dict[platform, List[brands_mentioned]]
            max_competitors: Maximum number of competitors to return

        Returns:
            List of CompetitorMetrics, ranked by competitiveness
        """
        # Filter to only generic queries for discovery
        generic_results = [
            r for r in query_results
            if r.get('category') == 'generic'
        ]

        if not generic_results:
            return []

        # Extract brand mentions from all generic queries
        brand_tracker = defaultdict(lambda: CompetitorMetrics(brand_name=''))

        for result in generic_results:
            query_text = result.get('query', '')

            # Analyze each platform's response
            for platform, response in result.get('responses', {}).items():
                if not response:
                    continue

                # Extract brand mentions from response
                brands_found = self._extract_brands_from_text(response)

                for brand, position, detail_score in brands_found:
                    # Skip target brand
                    if brand.lower() == self.target_brand.lower():
                        continue

                    # Track metrics
                    metrics = brand_tracker[brand]
                    if not metrics.brand_name:
                        metrics.brand_name = brand

                    metrics.mention_count += 1
                    metrics.ranking_positions.append(position)
                    metrics.avg_detail_score = (
                        (metrics.avg_detail_score * (metrics.mention_count - 1) + detail_score)
                        / metrics.mention_count
                    )

                    if query_text not in metrics.queries_appeared_in:
                        metrics.queries_appeared_in.append(query_text)

        # Calculate aggregate metrics
        total_generic_queries = len(generic_results)

        for brand, metrics in brand_tracker.items():
            metrics.total_queries = total_generic_queries
            metrics.mention_rate = (metrics.mention_count / total_generic_queries) * 100

            if metrics.ranking_positions:
                metrics.avg_ranking = sum(metrics.ranking_positions) / len(metrics.ranking_positions)

            # Calculate competitiveness score
            metrics.competitiveness_score = self._calculate_competitiveness(metrics)

        # Sort by competitiveness and return top N
        ranked_competitors = sorted(
            brand_tracker.values(),
            key=lambda m: m.competitiveness_score,
            reverse=True
        )

        return ranked_competitors[:max_competitors]

    def _extract_brands_from_text(self, text: str) -> List[tuple]:
        """
        Extract brand mentions from text with position and detail score

        Returns:
            List of (brand_name, position, detail_score) tuples
        """
        brands_found = []
        text_lower = text.lower()

        for brand, pattern in self.brand_patterns:
            matches = pattern.finditer(text)

            for match in matches:
                # Estimate position (earlier = better)
                char_position = match.start()
                estimated_position = 1 + int((char_position / len(text)) * 10)

                # Calculate detail score (how much text surrounds this brand)
                context_start = max(0, char_position - 100)
                context_end = min(len(text), char_position + 100)
                context = text[context_start:context_end]
                detail_score = min(10, len(context.split()) / 20)

                brands_found.append((brand, estimated_position, detail_score))
                break  # Only count first mention per brand

        return brands_found

    def _calculate_competitiveness(self, metrics: CompetitorMetrics) -> float:
        """
        Calculate overall competitiveness score

        Weighted formula:
        - Mention rate (40%): How often does this brand appear?
        - Avg ranking position (30%): How prominently is it featured?
        - Detail score (20%): How much detail/attention does it get?
        - Sentiment (10%): Is the sentiment positive?
        """
        # Mention rate component (0-40 points)
        mention_component = (metrics.mention_rate / 100) * 40

        # Ranking component (0-30 points, inverse - lower rank = better)
        if metrics.avg_ranking > 0:
            ranking_component = (1 / metrics.avg_ranking) * 30
        else:
            ranking_component = 0

        # Detail score component (0-20 points)
        detail_component = (metrics.avg_detail_score / 10) * 20

        # Sentiment component (0-10 points) - placeholder for now
        sentiment_component = 5  # Neutral default

        total_score = (
            mention_component +
            ranking_component +
            detail_component +
            sentiment_component
        )

        return total_score

    def enrich_with_seed_data(
        self,
        discovered: List[CompetitorMetrics]
    ) -> List[CompetitorMetrics]:
        """
        Enrich discovered competitors with seed list data

        Adds any major competitors from seed list that weren't discovered
        but should be tracked (with zero metrics)
        """
        discovered_brands = {m.brand_name.lower() for m in discovered}

        # Add top seed list brands if not discovered
        for seed_brand in list(self.industry_brands)[:10]:
            if seed_brand.lower() not in discovered_brands:
                # Add with zero metrics (for awareness)
                discovered.append(CompetitorMetrics(
                    brand_name=seed_brand,
                    mention_rate=0.0,
                    avg_ranking=0.0,
                    competitiveness_score=0.0
                ))

        return discovered
