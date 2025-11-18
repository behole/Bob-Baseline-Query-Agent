"""
Gap Analysis Engine

Identifies specific queries where competitors outperform the target brand,
clusters gaps by theme, and prioritizes for action.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import re


@dataclass
class Gap:
    """Represents a single competitive gap"""
    query: str
    category: str
    target_brand: str
    competitor: str
    target_rank: int
    competitor_rank: int
    gap_size: int
    competitor_detail: str
    target_detail: str
    theme: str = ''


@dataclass
class GapCluster:
    """Cluster of related gaps by theme"""
    theme: str
    competitor: str
    gaps: List[Gap] = field(default_factory=list)
    affected_queries: List[str] = field(default_factory=list)
    avg_gap_size: float = 0.0
    priority_score: float = 0.0
    strategic_importance: float = 5.0  # 1-10 scale


class GapAnalyzer:
    """
    Analyzes query results to identify competitive gaps
    """

    def __init__(self, target_brand: str):
        """
        Initialize gap analyzer

        Args:
            target_brand: The brand being audited
        """
        self.target_brand = target_brand

        # Theme keywords for categorization
        self.theme_patterns = {
            'soccer': ['soccer', 'football', 'cleats', 'boots'],
            'running': ['running', 'runner', 'marathon', 'jogging'],
            'trail': ['trail', 'hiking', 'outdoor running'],
            'basketball': ['basketball', 'court', 'hoops'],
            'training': ['training', 'gym', 'workout', 'cross-training'],
            'sustainability': ['sustainable', 'eco-friendly', 'environment', 'recycled', 'green'],
            'price': ['affordable', 'budget', 'cheap', 'expensive', 'price', 'cost'],
            'quality': ['quality', 'durability', 'lasting', 'premium'],
            'comfort': ['comfortable', 'comfort', 'cushioning', 'support'],
            'style': ['style', 'fashion', 'trendy', 'design', 'look'],
            'performance': ['performance', 'speed', 'lightweight', 'technical'],
            'casual': ['casual', 'everyday', 'lifestyle'],
            'professional': ['professional', 'athlete', 'pro', 'elite'],
        }

    def identify_gaps(
        self,
        query_results: List[Dict[str, Any]],
        competitor_name: str,
        max_priority_gaps: int = 3
    ) -> List[GapCluster]:
        """
        Identify priority gaps against a specific competitor

        Args:
            query_results: List of query result dictionaries
            competitor_name: Competitor to compare against
            max_priority_gaps: Maximum number of priority gap clusters to return

        Returns:
            List of GapCluster objects, sorted by priority
        """
        # Find all individual gaps
        all_gaps = []

        for result in query_results:
            query_text = result.get('query', '')
            category = result.get('category', '')

            # Analyze each platform's response
            for platform, response in result.get('responses', {}).items():
                if not response:
                    continue

                # Extract rankings
                target_rank = self._find_brand_rank(response, self.target_brand)
                competitor_rank = self._find_brand_rank(response, competitor_name)

                # Check if competitor outperforms
                if competitor_rank > 0 and (target_rank == 0 or competitor_rank < target_rank):
                    gap_size = (target_rank if target_rank > 0 else 10) - competitor_rank

                    # Extract context details
                    competitor_detail = self._extract_brand_context(response, competitor_name)
                    target_detail = self._extract_brand_context(response, self.target_brand) if target_rank > 0 else "Not mentioned"

                    # Categorize theme
                    theme = self._categorize_theme(query_text)

                    gap = Gap(
                        query=query_text,
                        category=category,
                        target_brand=self.target_brand,
                        competitor=competitor_name,
                        target_rank=target_rank if target_rank > 0 else 999,
                        competitor_rank=competitor_rank,
                        gap_size=gap_size,
                        competitor_detail=competitor_detail,
                        target_detail=target_detail,
                        theme=theme
                    )

                    all_gaps.append(gap)

        # Cluster gaps by theme
        gap_clusters = self._cluster_by_theme(all_gaps, competitor_name)

        # Prioritize clusters
        prioritized = self._prioritize_clusters(gap_clusters)

        return prioritized[:max_priority_gaps]

    def _find_brand_rank(self, text: str, brand_name: str) -> int:
        """
        Find approximate ranking position of brand in text

        Returns:
            Position (1-10) or 0 if not found
        """
        text_lower = text.lower()
        brand_lower = brand_name.lower()

        # Check if brand is mentioned
        pattern = re.compile(r'\b' + re.escape(brand_lower) + r'\b')
        match = pattern.search(text_lower)

        if not match:
            return 0

        # Estimate position based on character position
        char_position = match.start()
        text_length = len(text)

        # Map character position to rank 1-10
        position_ratio = char_position / text_length
        estimated_rank = 1 + int(position_ratio * 9)

        return estimated_rank

    def _extract_brand_context(self, text: str, brand_name: str, context_chars: int = 200) -> str:
        """Extract text context around brand mention"""
        text_lower = text.lower()
        brand_lower = brand_name.lower()

        pattern = re.compile(r'\b' + re.escape(brand_lower) + r'\b')
        match = pattern.search(text_lower)

        if not match:
            return ""

        start = max(0, match.start() - context_chars)
        end = min(len(text), match.end() + context_chars)

        return text[start:end].strip()

    def _categorize_theme(self, query: str) -> str:
        """Categorize query into a theme"""
        query_lower = query.lower()

        # Check each theme pattern
        theme_scores = {}
        for theme, keywords in self.theme_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                theme_scores[theme] = score

        if theme_scores:
            # Return theme with highest score
            return max(theme_scores, key=theme_scores.get)

        return 'general'

    def _cluster_by_theme(self, gaps: List[Gap], competitor: str) -> List[GapCluster]:
        """Group gaps by theme"""
        theme_clusters = defaultdict(lambda: GapCluster(theme='', competitor=competitor))

        for gap in gaps:
            cluster = theme_clusters[gap.theme]
            cluster.theme = gap.theme
            cluster.gaps.append(gap)
            if gap.query not in cluster.affected_queries:
                cluster.affected_queries.append(gap.query)

        # Calculate aggregate metrics for each cluster
        for cluster in theme_clusters.values():
            if cluster.gaps:
                cluster.avg_gap_size = sum(g.gap_size for g in cluster.gaps) / len(cluster.gaps)

        return list(theme_clusters.values())

    def _prioritize_clusters(self, clusters: List[GapCluster]) -> List[GapCluster]:
        """
        Prioritize gap clusters by impact

        Priority formula:
        - Number of affected queries (40%)
        - Average gap size (30%)
        - Strategic importance (30%)
        """
        for cluster in clusters:
            # Impact component (0-40 points)
            query_count = len(cluster.affected_queries)
            impact_score = min(40, query_count * 10)

            # Gap size component (0-30 points)
            gap_score = min(30, cluster.avg_gap_size * 5)

            # Strategic importance (0-30 points)
            strategic_score = (cluster.strategic_importance / 10) * 30

            cluster.priority_score = impact_score + gap_score + strategic_score

        # Sort by priority score
        return sorted(clusters, key=lambda c: c.priority_score, reverse=True)
