"""
V2 GEO Audit Report Generator

Generates comprehensive reports with:
- Executive Summary
- Market Discovery (auto-discovered competitors)
- Gap Analysis per competitor
- Prioritized Action Plan
"""

from typing import List, Dict, Any
from datetime import datetime
from ..discovery.competitor_discovery import CompetitorMetrics
from ..analysis.gap_analysis import GapCluster
from ..analysis.recommendations import Recommendation


class V2ReportGenerator:
    """Generate V2 GEO audit reports with automated insights"""

    def __init__(self, brand_name: str, industry: str):
        """
        Initialize report generator

        Args:
            brand_name: Target brand name
            industry: Industry category
        """
        self.brand_name = brand_name
        self.industry = industry
        self.brand_short = self._get_brand_short_name(brand_name)

    def _get_brand_short_name(self, brand_name: str) -> str:
        """Generate short name for brand"""
        words = brand_name.split()
        if len(words) > 1:
            return ''.join([w[0] for w in words]).upper()
        return brand_name[:3].upper()

    def generate_report(
        self,
        competitors: List[CompetitorMetrics],
        all_gap_clusters: List[GapCluster],
        recommendations: List[Recommendation],
        query_stats: Dict[str, Any],
        output_path: str = 'v2_geo_report.html'
    ) -> str:
        """
        Generate complete V2 HTML report

        Args:
            competitors: List of discovered competitors
            all_gap_clusters: All gap clusters across competitors
            recommendations: Prioritized recommendations
            query_stats: Dictionary with query statistics:
                - total_queries: int
                - branded_count: int
                - generic_count: int
                - branded_mention_rate: float
                - generic_mention_rate: float
            output_path: Output file path

        Returns:
            Path to generated report
        """
        html = self._generate_html(
            competitors=competitors,
            all_gap_clusters=all_gap_clusters,
            recommendations=recommendations,
            query_stats=query_stats
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ V2 Report generated: {output_path}")
        return output_path

    def _generate_html(
        self,
        competitors: List[CompetitorMetrics],
        all_gap_clusters: List[GapCluster],
        recommendations: List[Recommendation],
        query_stats: Dict[str, Any]
    ) -> str:
        """Generate complete HTML report"""

        # Generate sections
        executive_summary = self._generate_executive_summary(
            competitors, recommendations, query_stats
        )
        market_discovery = self._generate_market_discovery(competitors, query_stats)
        gap_analysis = self._generate_gap_analysis_sections(all_gap_clusters)
        action_plan = self._generate_action_plan(recommendations)

        # Combine into full HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.brand_name} GEO Audit Report - V2 Automated Analysis</title>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {executive_summary}
        {market_discovery}
        {gap_analysis}
        {action_plan}
        {self._generate_footer()}
    </div>
</body>
</html>"""

        return html

    def _generate_header(self) -> str:
        """Generate report header"""
        return f"""
<header class="report-header">
    <div class="brand-title">{self.brand_name}</div>
    <div class="report-title">GEO Audit Report</div>
    <div class="report-subtitle">Automated Competitive Intelligence Analysis</div>
    <div class="report-meta">
        <span>Industry: {self.industry.replace('_', ' ').title()}</span>
        <span>•</span>
        <span>Generated: {datetime.now().strftime('%B %d, %Y')}</span>
        <span>•</span>
        <span>System: V2 Automated Discovery</span>
    </div>
</header>"""

    def _generate_executive_summary(
        self,
        competitors: List[CompetitorMetrics],
        recommendations: List[Recommendation],
        query_stats: Dict[str, Any]
    ) -> str:
        """Generate executive summary section"""

        # Find top competitor
        top_competitor = competitors[0] if competitors else None

        # Calculate gap
        market_share = query_stats.get('generic_mention_rate', 0)
        competitor_share = top_competitor.mention_rate if top_competitor else 0
        gap = market_share - competitor_share

        # Count high priority gaps
        high_priority_count = sum(1 for r in recommendations if r.impact_level == 'HIGH')

        return f"""
<section class="section">
    <div class="section-header">
        <div class="section-number">1</div>
        <div>
            <div class="section-title">Executive Summary</div>
            <div class="section-subtitle">Key Findings & Strategic Overview</div>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Market Position</div>
            <div class="stat-value">#{1 if gap > 0 else 2}</div>
            <div class="stat-description">{market_share:.1f}% share of voice</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Top Competitor</div>
            <div class="stat-value">{top_competitor.brand_name if top_competitor else 'N/A'}</div>
            <div class="stat-description">{competitor_share:.1f}% share ({gap:+.1f}% gap)</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">High-Priority Gaps</div>
            <div class="stat-value">{high_priority_count}</div>
            <div class="stat-description">Immediate action recommended</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Queries Analyzed</div>
            <div class="stat-value">{query_stats.get('total_queries', 0)}</div>
            <div class="stat-description">{query_stats.get('generic_count', 0)} generic, {query_stats.get('branded_count', 0)} branded</div>
        </div>
    </div>

    <div class="key-findings">
        <h3>Key Findings</h3>
        <ul>
            <li><strong>Branded Query Performance:</strong> {query_stats.get('branded_mention_rate', 0):.1f}% mention rate ({"strong" if query_stats.get('branded_mention_rate', 0) > 90 else "needs improvement"})</li>
            <li><strong>Generic Market Presence:</strong> {market_share:.1f}% mention rate - {"leading position" if gap > 0 else f"trailing {top_competitor.brand_name if top_competitor else 'competitor'}"}</li>
            <li><strong>Competitive Intelligence:</strong> {len(competitors)} active competitors discovered and ranked</li>
            <li><strong>Actionable Opportunities:</strong> {len(recommendations)} priority gaps identified with strategic recommendations</li>
        </ul>
    </div>

    <div class="top-opportunities">
        <h3>Top 3 Opportunities</h3>
        <ol>
            {"".join([f'<li><strong>{rec.gap_theme.title()}</strong> (vs {rec.competitor}) - {rec.impact_level} impact, {rec.affected_query_count} queries affected</li>' for rec in recommendations[:3]])}
        </ol>
    </div>
</section>"""

    def _generate_market_discovery(
        self,
        competitors: List[CompetitorMetrics],
        query_stats: Dict[str, Any]
    ) -> str:
        """Generate market discovery section"""

        # Generate competitor bars
        competitor_bars = ""
        max_rate = max([c.mention_rate for c in competitors] + [1.0])

        for i, comp in enumerate(competitors, 1):
            bar_width = (comp.mention_rate / max_rate) * 100
            rank_class = "rank-1" if i == 1 else "rank-2" if i == 2 else "rank-3" if i == 3 else ""

            competitor_bars += f"""
        <div class="competitor-bar">
            <div class="competitor-rank {rank_class}">#{i}</div>
            <div class="competitor-info">
                <div class="competitor-name">{comp.brand_name}</div>
                <div class="competitor-stats">
                    {comp.mention_rate:.1f}% share • Avg rank #{comp.avg_ranking:.1f} • {comp.mention_count} mentions
                </div>
            </div>
            <div class="competitor-bar-container">
                <div class="competitor-bar-fill" style="width: {bar_width}%"></div>
            </div>
        </div>"""

        return f"""
<section class="section">
    <div class="section-header">
        <div class="section-number">2</div>
        <div>
            <div class="section-title">Market Discovery</div>
            <div class="section-subtitle">Automatically Discovered Competitive Landscape</div>
        </div>
    </div>

    <div class="discovery-intro">
        <p>Analysis of <strong>{query_stats.get('generic_count', 0)} generic industry queries</strong> revealed the following competitive landscape. Competitors are ranked by competitiveness score, which combines mention frequency, ranking position, and response quality.</p>
    </div>

    <h3>Discovered Competitors (Ranked by Competitiveness)</h3>
    <div class="competitors-container">
{competitor_bars}
    </div>

    <div class="insight-box">
        <div class="insight-title">Key Insight</div>
        <div class="insight-text">
            {competitors[0].brand_name if competitors else "No competitor"} is your primary competitor, appearing in <strong>{competitors[0].mention_rate if competitors else 0:.1f}%</strong> of generic queries where {self.brand_name} appears. This indicates {"strong market presence and brand awareness" if competitors and competitors[0].mention_rate > 40 else "moderate competitive pressure"}.
        </div>
    </div>
</section>"""

    def _generate_gap_analysis_sections(
        self,
        all_gap_clusters: List[GapCluster]
    ) -> str:
        """Generate gap analysis sections for all competitors"""

        # Group gaps by competitor
        by_competitor = {}
        for cluster in all_gap_clusters:
            if cluster.competitor not in by_competitor:
                by_competitor[cluster.competitor] = []
            by_competitor[cluster.competitor].append(cluster)

        sections = f"""
<section class="section">
    <div class="section-header">
        <div class="section-number">3</div>
        <div>
            <div class="section-title">Competitive Gap Analysis</div>
            <div class="section-subtitle">Priority Gaps by Competitor</div>
        </div>
    </div>
"""

        for competitor, clusters in by_competitor.items():
            sections += self._generate_competitor_gap_section(competitor, clusters)

        sections += "</section>"
        return sections

    def _generate_competitor_gap_section(
        self,
        competitor: str,
        clusters: List[GapCluster]
    ) -> str:
        """Generate gap analysis for single competitor"""

        gap_cards = ""
        for i, cluster in enumerate(clusters, 1):
            impact_class = "impact-high" if cluster.priority_score > 50 else "impact-medium" if cluster.priority_score > 30 else "impact-low"

            affected_queries_list = "".join([f"<li>{q}</li>" for q in cluster.affected_queries[:5]])
            if len(cluster.affected_queries) > 5:
                affected_queries_list += f"<li><em>...and {len(cluster.affected_queries) - 5} more</em></li>"

            gap_cards += f"""
        <div class="gap-card {impact_class}">
            <div class="gap-header">
                <div class="gap-title">Gap #{i}: {cluster.theme.title()} Category</div>
                <div class="gap-priority">Priority Score: {cluster.priority_score:.1f}</div>
            </div>
            <div class="gap-body">
                <div class="gap-stat">
                    <span class="gap-stat-label">Affected Queries:</span>
                    <span class="gap-stat-value">{len(cluster.affected_queries)}</span>
                </div>
                <div class="gap-stat">
                    <span class="gap-stat-label">Avg Gap Size:</span>
                    <span class="gap-stat-value">{cluster.avg_gap_size:.1f} positions</span>
                </div>

                <div class="gap-queries">
                    <strong>Affected Queries:</strong>
                    <ul>{affected_queries_list}</ul>
                </div>

                <div class="gap-advantage">
                    <strong>{competitor} Advantage:</strong>
                    <ul>
                        <li>Consistently ranks higher in {cluster.theme} queries</li>
                        <li>Average ranking advantage: {cluster.avg_gap_size:.1f} positions</li>
                        <li>Appears in {len(cluster.affected_queries)} related queries</li>
                    </ul>
                </div>
            </div>
        </div>"""

        return f"""
    <div class="competitor-gap-section">
        <h3>{self.brand_name} vs {competitor}</h3>
        <div class="gap-cards-container">
{gap_cards}
        </div>
    </div>"""

    def _generate_action_plan(self, recommendations: List[Recommendation]) -> str:
        """Generate prioritized action plan section"""

        action_items = ""
        for rec in recommendations:
            impact_class = f"impact-{rec.impact_level.lower()}"
            difficulty_class = f"difficulty-{rec.difficulty.lower()}"

            actions_list = "".join([f"<li>{action}</li>" for action in rec.actions])

            action_items += f"""
        <div class="action-item {impact_class}">
            <div class="action-header">
                <div class="action-title">Priority {rec.priority_rank}: {rec.gap_theme.title()} (vs {rec.competitor})</div>
                <div class="action-badges">
                    <span class="badge impact-badge">{rec.impact_level} Impact</span>
                    <span class="badge {difficulty_class}">{rec.difficulty} Difficulty</span>
                    <span class="badge queries-badge">{rec.affected_query_count} Queries</span>
                </div>
            </div>
            <div class="action-body">
                <div class="action-section">
                    <h4>Recommended Actions:</h4>
                    <ul class="action-list">{actions_list}</ul>
                </div>
                <div class="action-impact">
                    <strong>Expected Impact:</strong> {rec.potential_improvement} improvement in {rec.gap_theme} category
                </div>
            </div>
        </div>"""

        return f"""
<section class="section action-plan-section">
    <div class="section-header">
        <div class="section-number">4</div>
        <div>
            <div class="section-title">Prioritized Action Plan</div>
            <div class="section-subtitle">Strategic Recommendations Ranked by Impact</div>
        </div>
    </div>

    <div class="action-items-container">
{action_items}
    </div>
</section>"""

    def _generate_footer(self) -> str:
        """Generate report footer"""
        return f"""
<footer class="report-footer">
    <div class="footer-content">
        <p>Generated by GEO Audit V2 Automated Discovery System</p>
        <p>This report uses automated competitor discovery, intelligent gap analysis, and AI-powered recommendations</p>
        <p>&copy; {datetime.now().year} - Generative Engine Optimization Intelligence</p>
    </div>
</footer>"""

    def _get_css_styles(self) -> str:
        """Get CSS styles for report"""
        return """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #1a1a1a;
        background: #f5f5f5;
    }

    .container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }

    /* Header */
    .report-header {
        background: linear-gradient(135deg, #000 0%, #333 100%);
        color: white;
        padding: 60px 40px;
        border-radius: 8px;
        margin-bottom: 30px;
        text-align: center;
    }

    .brand-title {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .report-title {
        font-size: 32px;
        font-weight: 300;
        margin-bottom: 10px;
    }

    .report-subtitle {
        font-size: 18px;
        opacity: 0.9;
        margin-bottom: 20px;
    }

    .report-meta {
        font-size: 14px;
        opacity: 0.7;
    }

    .report-meta span {
        margin: 0 10px;
    }

    /* Sections */
    .section {
        background: white;
        border-radius: 8px;
        padding: 40px;
        margin-bottom: 30px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 2px solid #f0f0f0;
    }

    .section-number {
        font-size: 48px;
        font-weight: 700;
        color: #e0e0e0;
        margin-right: 20px;
        min-width: 60px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 600;
        color: #1a1a1a;
    }

    .section-subtitle {
        font-size: 16px;
        color: #666;
        margin-top: 5px;
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }

    .stat-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 25px;
        text-align: center;
        border: 1px solid #e9ecef;
    }

    .stat-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }

    .stat-value {
        font-size: 42px;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 10px;
    }

    .stat-description {
        font-size: 14px;
        color: #666;
    }

    /* Competitor Bars */
    .competitors-container {
        margin: 30px 0;
    }

    .competitor-bar {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
    }

    .competitor-rank {
        font-size: 24px;
        font-weight: 700;
        min-width: 50px;
        margin-right: 15px;
    }

    .competitor-rank.rank-1 { color: #FFD700; }
    .competitor-rank.rank-2 { color: #C0C0C0; }
    .competitor-rank.rank-3 { color: #CD7F32; }

    .competitor-info {
        flex: 0 0 300px;
        margin-right: 20px;
    }

    .competitor-name {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .competitor-stats {
        font-size: 13px;
        color: #666;
    }

    .competitor-bar-container {
        flex: 1;
        height: 30px;
        background: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
    }

    .competitor-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        transition: width 0.3s ease;
    }

    /* Gap Cards */
    .gap-cards-container {
        display: grid;
        gap: 20px;
        margin: 20px 0;
    }

    .gap-card {
        border-radius: 8px;
        border-left: 4px solid #ccc;
        background: #f8f9fa;
        overflow: hidden;
    }

    .gap-card.impact-high {
        border-left-color: #dc3545;
        background: #fff5f5;
    }

    .gap-card.impact-medium {
        border-left-color: #ffc107;
        background: #fffef5;
    }

    .gap-card.impact-low {
        border-left-color: #28a745;
        background: #f5fff8;
    }

    .gap-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        background: rgba(0,0,0,0.02);
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }

    .gap-title {
        font-size: 20px;
        font-weight: 600;
    }

    .gap-priority {
        font-size: 14px;
        color: #666;
    }

    .gap-body {
        padding: 20px;
    }

    .gap-stat {
        display: inline-block;
        margin-right: 30px;
        margin-bottom: 15px;
    }

    .gap-stat-label {
        font-size: 13px;
        color: #666;
        margin-right: 8px;
    }

    .gap-stat-value {
        font-size: 18px;
        font-weight: 600;
    }

    .gap-queries, .gap-advantage {
        margin-top: 20px;
    }

    .gap-queries ul, .gap-advantage ul {
        margin-left: 20px;
        margin-top: 10px;
    }

    .gap-queries li, .gap-advantage li {
        margin-bottom: 5px;
        color: #444;
    }

    /* Action Items */
    .action-items-container {
        display: grid;
        gap: 25px;
    }

    .action-item {
        border-radius: 8px;
        border-left: 5px solid #ccc;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .action-item.impact-high {
        border-left-color: #dc3545;
    }

    .action-item.impact-medium {
        border-left-color: #ffc107;
    }

    .action-item.impact-low {
        border-left-color: #28a745;
    }

    .action-header {
        padding: 25px;
        background: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
    }

    .action-title {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 15px;
    }

    .action-badges {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }

    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .impact-badge {
        background: #e3f2fd;
        color: #1976d2;
    }

    .difficulty-high {
        background: #ffebee;
        color: #c62828;
    }

    .difficulty-medium {
        background: #fff3e0;
        color: #ef6c00;
    }

    .difficulty-low {
        background: #e8f5e9;
        color: #2e7d32;
    }

    .queries-badge {
        background: #f3e5f5;
        color: #7b1fa2;
    }

    .action-body {
        padding: 25px;
    }

    .action-list {
        list-style: none;
        margin: 15px 0;
    }

    .action-list li {
        padding: 12px;
        margin-bottom: 10px;
        background: #f8f9fa;
        border-radius: 4px;
        border-left: 3px solid #4CAF50;
    }

    .action-list li:before {
        content: "→ ";
        color: #4CAF50;
        font-weight: bold;
        margin-right: 8px;
    }

    .action-impact {
        margin-top: 20px;
        padding: 15px;
        background: #e8f5e9;
        border-radius: 4px;
        border-left: 3px solid #4CAF50;
    }

    /* Insight Box */
    .insight-box {
        margin: 30px 0;
        padding: 20px;
        background: #e3f2fd;
        border-left: 4px solid #1976d2;
        border-radius: 4px;
    }

    .insight-title {
        font-size: 16px;
        font-weight: 600;
        color: #1565c0;
        margin-bottom: 10px;
    }

    .insight-text {
        color: #424242;
        line-height: 1.7;
    }

    /* Lists */
    .key-findings ul, .top-opportunities ol {
        margin: 20px 0;
        padding-left: 20px;
    }

    .key-findings li, .top-opportunities li {
        margin-bottom: 12px;
        line-height: 1.7;
    }

    h3 {
        font-size: 22px;
        margin: 30px 0 15px 0;
        color: #1a1a1a;
    }

    h4 {
        font-size: 16px;
        margin: 15px 0 10px 0;
        color: #333;
    }

    /* Footer */
    .report-footer {
        background: #1a1a1a;
        color: white;
        padding: 30px;
        text-align: center;
        border-radius: 8px;
        margin-top: 30px;
    }

    .footer-content p {
        margin: 5px 0;
        opacity: 0.8;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }

        .competitor-bar {
            flex-direction: column;
            align-items: flex-start;
        }

        .competitor-info {
            flex: 1;
            margin-bottom: 10px;
        }
    }
</style>"""
