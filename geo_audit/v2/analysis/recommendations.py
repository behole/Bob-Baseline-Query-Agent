"""
Recommendation Engine

Generates actionable, high-level recommendations based on gap analysis
with estimated impact metrics.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from .gap_analysis import GapCluster


@dataclass
class Recommendation:
    """Actionable recommendation with impact estimate"""
    gap_theme: str
    competitor: str
    affected_queries: List[str]
    actions: List[str]
    impact_level: str  # HIGH, MEDIUM, LOW
    affected_query_count: int
    potential_improvement: str
    difficulty: str  # HIGH, MEDIUM, LOW
    priority_rank: int = 0


class RecommendationEngine:
    """
    Generates strategic recommendations from gap analysis
    """

    def __init__(self):
        """Initialize recommendation engine"""
        # Action templates by gap type
        self.action_templates = {
            'soccer': {
                'authority': [
                    'Enhance soccer content authority and expertise',
                    'Highlight professional soccer partnerships and endorsements',
                    'Strengthen soccer heritage messaging',
                    'Create comprehensive soccer-specific buying guides'
                ],
                'content': [
                    'Improve soccer product detail visibility',
                    'Add technical specifications for soccer footwear',
                    'Include professional athlete testimonials',
                    'Reference major tournament presence and partnerships'
                ]
            },
            'sustainability': {
                'messaging': [
                    'Strengthen sustainability messaging and visibility',
                    'Highlight specific environmental initiatives and programs',
                    'Improve transparency on eco-friendly efforts',
                    'Reference recycled material percentages and carbon metrics'
                ],
                'content': [
                    'Create dedicated sustainability-focused content',
                    'Develop eco-friendly product comparison guides',
                    'Showcase environmental partnership programs',
                    'Emphasize "Move to Zero" or similar initiatives'
                ]
            },
            'trail': {
                'authority': [
                    'Build trail running category authority',
                    'Create comprehensive trail running content and guides',
                    'Emphasize technical trail product features',
                    'Highlight trail-specific innovations'
                ]
            },
            'running': {
                'content': [
                    'Enhance running category content depth',
                    'Create detailed running shoe comparison guides',
                    'Highlight running-specific technologies',
                    'Feature runner testimonials and use cases'
                ]
            },
            'price': {
                'messaging': [
                    'Clarify value proposition and pricing strategy',
                    'Emphasize quality-to-price ratio',
                    'Create budget-friendly product guides',
                    'Highlight financing or promotional options'
                ]
            },
            'quality': {
                'authority': [
                    'Strengthen quality and durability messaging',
                    'Highlight product testing and quality standards',
                    'Feature long-term customer testimonials',
                    'Emphasize warranty and guarantee programs'
                ]
            },
            'performance': {
                'content': [
                    'Enhance performance-focused content',
                    'Highlight technical specifications and innovations',
                    'Feature professional athlete endorsements',
                    'Create performance comparison guides'
                ]
            },
            'general': {
                'content': [
                    'Improve content depth and detail',
                    'Enhance product information visibility',
                    'Create comprehensive category guides',
                    'Strengthen overall brand positioning'
                ],
                'authority': [
                    'Build category authority and expertise',
                    'Highlight relevant partnerships and credentials',
                    'Improve thought leadership visibility'
                ]
            }
        }

    def generate_recommendations(
        self,
        gap_clusters: List[GapCluster],
        target_brand: str
    ) -> List[Recommendation]:
        """
        Generate prioritized recommendations from gap clusters

        Args:
            gap_clusters: List of GapCluster objects
            target_brand: Brand being audited

        Returns:
            List of Recommendation objects, ranked by priority
        """
        recommendations = []

        for idx, cluster in enumerate(gap_clusters, 1):
            # Generate actions for this gap theme
            actions = self._generate_actions(cluster)

            # Estimate impact
            impact = self._estimate_impact(cluster)

            rec = Recommendation(
                gap_theme=cluster.theme,
                competitor=cluster.competitor,
                affected_queries=cluster.affected_queries,
                actions=actions,
                impact_level=impact['level'],
                affected_query_count=len(cluster.affected_queries),
                potential_improvement=impact['potential_improvement'],
                difficulty=impact['difficulty'],
                priority_rank=idx
            )

            recommendations.append(rec)

        return recommendations

    def _generate_actions(self, cluster: GapCluster) -> List[str]:
        """Generate specific actions for a gap cluster"""
        theme = cluster.theme
        actions = []

        # Get templates for this theme
        theme_templates = self.action_templates.get(theme, self.action_templates['general'])

        # Select mix of authority and content actions
        for action_type, action_list in theme_templates.items():
            actions.extend(action_list[:2])  # Take top 2 from each type

        # Limit to 4 actions max
        return actions[:4]

    def _estimate_impact(self, cluster: GapCluster) -> Dict[str, str]:
        """
        Estimate impact of addressing this gap

        Returns:
            Dict with level, potential_improvement, and difficulty
        """
        query_count = len(cluster.affected_queries)
        avg_gap_size = cluster.avg_gap_size

        # Determine impact level
        if query_count >= 3 and avg_gap_size >= 2:
            level = 'HIGH'
            potential_improvement = '15-25%'
            difficulty = 'MEDIUM'
        elif query_count >= 2 or avg_gap_size >= 1.5:
            level = 'MEDIUM'
            potential_improvement = '8-15%'
            difficulty = 'LOW' if query_count == 2 else 'MEDIUM'
        else:
            level = 'LOW'
            potential_improvement = '3-8%'
            difficulty = 'LOW'

        # Adjust difficulty based on theme
        if cluster.theme in ['sustainability', 'price']:
            difficulty = 'LOW'  # Messaging changes are easier
        elif cluster.theme in ['soccer', 'trail', 'performance']:
            difficulty = 'MEDIUM'  # Requires content + authority building

        return {
            'level': level,
            'potential_improvement': potential_improvement,
            'difficulty': difficulty
        }

    def format_action_plan(
        self,
        recommendations: List[Recommendation],
        format_type: str = 'text'
    ) -> str:
        """
        Format recommendations as actionable plan

        Args:
            recommendations: List of recommendations
            format_type: 'text' or 'html'

        Returns:
            Formatted action plan string
        """
        if format_type == 'html':
            return self._format_html_action_plan(recommendations)
        else:
            return self._format_text_action_plan(recommendations)

    def _format_text_action_plan(self, recommendations: List[Recommendation]) -> str:
        """Format as plain text"""
        output = []
        output.append("=" * 60)
        output.append("PRIORITIZED ACTION PLAN")
        output.append("=" * 60)

        for rec in recommendations:
            output.append(f"\nPRIORITY {rec.priority_rank}: {rec.gap_theme.upper()} (vs {rec.competitor})")
            output.append(f"Impact: {rec.impact_level} | Difficulty: {rec.difficulty} | Queries: {rec.affected_query_count}")
            output.append("\nRecommended Actions:")
            for i, action in enumerate(rec.actions, 1):
                output.append(f"  {i}. {action}")
            output.append(f"\nEstimated Impact: {rec.potential_improvement} improvement in {rec.gap_theme} category")
            output.append("-" * 60)

        return "\n".join(output)

    def _format_html_action_plan(self, recommendations: List[Recommendation]) -> str:
        """Format as HTML section"""
        html_parts = []

        html_parts.append('<div class="action-plan">')
        html_parts.append('<h2>Prioritized Action Plan</h2>')

        for rec in recommendations:
            impact_class = f"impact-{rec.impact_level.lower()}"

            html_parts.append(f'<div class="recommendation {impact_class}">')
            html_parts.append(f'<h3>Priority {rec.priority_rank}: {rec.gap_theme.title()} Gap (vs {rec.competitor})</h3>')

            html_parts.append('<div class="rec-metrics">')
            html_parts.append(f'<span class="badge impact-badge">{rec.impact_level} Impact</span>')
            html_parts.append(f'<span class="badge difficulty-badge">{rec.difficulty} Difficulty</span>')
            html_parts.append(f'<span class="badge queries-badge">{rec.affected_query_count} Queries</span>')
            html_parts.append('</div>')

            html_parts.append('<div class="rec-actions">')
            html_parts.append('<h4>Recommended Actions:</h4>')
            html_parts.append('<ul>')
            for action in rec.actions:
                html_parts.append(f'<li>{action}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')

            html_parts.append('<div class="rec-impact">')
            html_parts.append(f'<strong>Expected Impact:</strong> {rec.potential_improvement} improvement in {rec.gap_theme} category')
            html_parts.append('</div>')

            html_parts.append('</div>')

        html_parts.append('</div>')

        return '\n'.join(html_parts)
