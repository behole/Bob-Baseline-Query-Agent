"""
GEO Audit V2 - Automated Competitor Discovery & Gap Analysis

New features:
- Automated competitor discovery from query results
- Intelligent gap analysis
- AI-powered recommendations
- Priority-based action plans
"""

from .discovery.competitor_discovery import CompetitorDiscovery
from .analysis.gap_analysis import GapAnalyzer
from .analysis.recommendations import RecommendationEngine

__all__ = [
    'CompetitorDiscovery',
    'GapAnalyzer',
    'RecommendationEngine'
]
