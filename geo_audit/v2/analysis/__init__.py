"""Analysis module for gap analysis and recommendations"""

from .gap_analysis import GapAnalyzer, GapCluster
from .recommendations import RecommendationEngine

__all__ = ['GapAnalyzer', 'GapCluster', 'RecommendationEngine']
