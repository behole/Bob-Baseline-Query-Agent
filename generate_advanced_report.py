#!/usr/bin/env python3
"""
Advanced GEO Report Generator - Matches Partner's Format
Generates comprehensive competitive analysis reports with Figma styling
"""

import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from collections import defaultdict
import argparse


class AdvancedGEOReportGenerator:
    """Generate comprehensive GEO audit reports with competitive analysis"""

    def __init__(self, config_path: str = "config.json", sheet_name: str = None, brand_name: str = "Brush On Block"):
        """Initialize with config and brand"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.sheet_name = sheet_name
        self.brand_name = brand_name
        self.brand_short = self._get_brand_short_name(brand_name)

        # Setup Google Sheets
        self.setup_google_sheets()

    def _get_brand_short_name(self, brand_name: str) -> str:
        """Generate short name for brand"""
        words = brand_name.split()
        if len(words) > 1:
            return ''.join([w[0] for w in words])
        return brand_name[:3].upper()

    def _get_competitor_list(self) -> list:
        """Get competitor list based on brand"""
        if any(term in self.brand_name.lower() for term in ['restoration hardware', 'rh']):
            return [
                'Pottery Barn', 'West Elm', 'Arhaus', 'Room & Board',
                'Crate and Barrel', 'CB2', 'Williams Sonoma Home',
                'Ethan Allen', 'Mitchell Gold', 'Four Hands'
            ]
        elif any(term in self.brand_name.lower() for term in ['brush on block', 'bob', 'sunscreen']):
            return [
                'Supergoop', 'ColorScience', 'Peter Thomas Roth', 'EltaMD',
                'La Roche-Posay', 'Neutrogena', 'CeraVe', 'Blue Lizard'
            ]
        return []

    def _categorize_query(self, query_text: str) -> str:
        """Categorize query as generic, branded, or competitor"""
        query_lower = query_text.lower()
        brand_lower = self.brand_name.lower()

        # Check for brand mentions
        brand_words = brand_lower.split()
        if any(word in query_lower for word in brand_words if len(word) > 2):
            return "branded"

        # Check for competitor mentions
        competitors = self._get_competitor_list()
        if any(comp.lower() in query_lower for comp in competitors):
            return "competitor"

        return "generic"

    def setup_google_sheets(self):
        """Setup Google Sheets API connection"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(
            self.config['google_credentials_path'],
            scopes=scopes
        )

        self.gc = gspread.authorize(creds)
        self.spreadsheet = self.gc.open_by_key(self.config['spreadsheet_id'])

        if self.sheet_name:
            try:
                self.sheet = self.spreadsheet.worksheet(self.sheet_name)
                print(f"📋 Using worksheet: '{self.sheet_name}'")
            except gspread.WorksheetNotFound:
                print(f"❌ Worksheet '{self.sheet_name}' not found!")
                raise
        else:
            self.sheet = self.spreadsheet.sheet1
            print(f"📋 Using default worksheet: '{self.sheet.title}'")

    def fetch_data(self):
        """Fetch data from Google Sheet"""
        print(f"📊 Fetching data from Google Sheets...")
        all_data = self.sheet.get_all_records()
        print(f"   Found {len(all_data)} rows of data")
        return all_data

    def analyze_data(self, data):
        """Comprehensive analysis matching partner's format"""
        brand_column = f'{self.brand_name} Mentioned?'

        analysis = {
            'total_queries': 0,
            'total_responses': len(data),
            'brand_mentions': 0,
            'by_query_type': {
                'generic': {'total': 0, 'brand_mentions': 0, 'queries': []},
                'branded': {'total': 0, 'brand_mentions': 0, 'queries': []},
                'competitor': {'total': 0, 'brand_mentions': 0, 'queries': []}
            },
            'by_platform': {},
            'competitors_share_of_voice': defaultdict(int),
            'zero_mention_queries': [],
            'query_performance': {},
            'platform_details': {}
        }

        # Track unique queries
        unique_queries = {}

        for row in data:
            query_num = row.get('Query #', 0)
            query_text = row.get('Query Text', '')
            platform = row.get('Platform', '')
            brand_mentioned = row.get(brand_column, 'No')
            competitors_str = row.get('Competitors Mentioned', '')

            if not query_text or not platform:
                continue

            # Initialize query tracking
            if query_text not in unique_queries:
                query_category = self._categorize_query(query_text)
                unique_queries[query_text] = {
                    'category': query_category,
                    'platforms_with_brand': [],
                    'platforms_without_brand': [],
                    'query_num': query_num
                }

            # Track brand mentions
            if brand_mentioned in ['Yes', 'Direct']:
                analysis['brand_mentions'] += 1
                unique_queries[query_text]['platforms_with_brand'].append(platform)
            else:
                unique_queries[query_text]['platforms_without_brand'].append(platform)

            # Track competitors
            if competitors_str and competitors_str != 'None':
                for comp in [c.strip() for c in competitors_str.split(',')]:
                    if comp:
                        analysis['competitors_share_of_voice'][comp] += 1

            # Track by platform
            if platform not in analysis['by_platform']:
                analysis['by_platform'][platform] = {
                    'total_responses': 0,
                    'brand_mentions': 0,
                    'mention_rate': 0.0
                }

            analysis['by_platform'][platform]['total_responses'] += 1
            if brand_mentioned in ['Yes', 'Direct']:
                analysis['by_platform'][platform]['brand_mentions'] += 1

        # Calculate platform mention rates
        for platform in analysis['by_platform']:
            total = analysis['by_platform'][platform]['total_responses']
            mentions = analysis['by_platform'][platform]['brand_mentions']
            analysis['by_platform'][platform]['mention_rate'] = (mentions / total * 100) if total > 0 else 0

        # Process queries by category
        for query_text, query_data in unique_queries.items():
            category = query_data['category']
            total_platforms = len(query_data['platforms_with_brand']) + len(query_data['platforms_without_brand'])
            brand_mentions_count = len(query_data['platforms_with_brand'])

            analysis['by_query_type'][category]['total'] += total_platforms
            analysis['by_query_type'][category]['brand_mentions'] += brand_mentions_count
            analysis['by_query_type'][category]['queries'].append({
                'text': query_text,
                'num': query_data['query_num'],
                'brand_mentions': brand_mentions_count,
                'total_platforms': total_platforms
            })

            # Identify zero-mention queries (generic only)
            if category == 'generic' and brand_mentions_count == 0:
                analysis['zero_mention_queries'].append(query_text)

        # Calculate total unique queries
        analysis['total_queries'] = len(unique_queries)

        # Calculate mention rates by query type
        for category in analysis['by_query_type']:
            total = analysis['by_query_type'][category]['total']
            mentions = analysis['by_query_type'][category]['brand_mentions']
            analysis['by_query_type'][category]['mention_rate'] = (mentions / total * 100) if total > 0 else 0

        # Add brand to competitor share of voice for ranking
        analysis['competitors_share_of_voice'][self.brand_name] = analysis['brand_mentions']

        return analysis

    def generate_html_report(self, analysis, output_path='advanced_report.html'):
        """Generate HTML report with Figma styling matching partner's format"""

        # Calculate key metrics
        overall_mention_rate = (analysis['brand_mentions'] / analysis['total_responses'] * 100) if analysis['total_responses'] > 0 else 0
        generic_mention_rate = analysis['by_query_type']['generic']['mention_rate']

        # Sort competitors by share of voice
        competitor_rankings = sorted(
            analysis['competitors_share_of_voice'].items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Get best platform
        best_platform = max(analysis['by_platform'].items(), key=lambda x: x[1]['mention_rate']) if analysis['by_platform'] else ('N/A', {'mention_rate': 0})

        # Determine competitive gap
        brand_rank = next((i for i, (name, _) in enumerate(competitor_rankings) if name == self.brand_name), None)
        if brand_rank == 0:
            competitive_status = "Market Leader"
            gap_message = "Leading the market"
        elif brand_rank and brand_rank == 1:
            leader_mentions = competitor_rankings[0][1]
            brand_mentions = analysis['brand_mentions']
            gap = ((leader_mentions - brand_mentions) / analysis['total_responses'] * 100)
            competitive_status = f"-{gap:.1f}%"
            gap_message = f"vs {competitor_rankings[0][0]} ({leader_mentions / analysis['total_responses'] * 100:.1f}%)"
        else:
            competitive_status = "Following"
            gap_message = "Multiple competitors ahead"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{self.brand_name} GEO Audit Report</title>
<style>
    {self._get_figma_css()}
</style>
</head>
<body>
<div class="page-wrapper">
<div class="container">

<!-- HEADER -->
<header class="report-header">
    <div class="brand-title">{self.brand_name.upper()} × GEO AUDIT</div>
    <div class="report-title">Comprehensive GEO Audit Report</div>
    <div class="report-meta"><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y')}</div>
</header>

<!-- SECTION 1: EXECUTIVE SUMMARY -->
<section class="section">
    <div class="section-header">
        <div class="section-number">1</div>
        <div>
            <div class="section-title">📊 Executive Summary</div>
            <div class="section-subtitle">Overall Performance Analysis</div>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Overall Mention Rate</div>
            <div class="stat-value">{overall_mention_rate:.1f}%</div>
            <div class="stat-description">{analysis['brand_mentions']} out of {analysis['total_responses']} total responses</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Generic Query Performance ⭐</div>
            <div class="stat-value">{generic_mention_rate:.1f}%</div>
            <div class="stat-description">KEY METRIC - True competitive position</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Competitive Gap</div>
            <div class="stat-value">{competitive_status}</div>
            <div class="stat-description">{gap_message}</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Best Platform</div>
            <div class="stat-value">{best_platform[0]}</div>
            <div class="stat-description">{best_platform[1]['mention_rate']:.1f}% mention rate</div>
        </div>
    </div>

    {'<div class="callout callout-success"><strong>✅ STRONG PERFORMANCE:</strong> ' + self.brand_short + ' mention rate of ' + f"{overall_mention_rate:.1f}% indicates solid AI visibility.</div>" if overall_mention_rate > 40 else ''}
    {'<div class="callout callout-warning"><strong>⚠️ MODERATE PERFORMANCE:</strong> ' + self.brand_short + ' mention rate of ' + f"{overall_mention_rate:.1f}% shows room for improvement.</div>" if 20 <= overall_mention_rate <= 40 else ''}
    {'<div class="callout callout-critical"><strong>🚨 LOW VISIBILITY:</strong> ' + self.brand_short + ' mention rate of ' + f"{overall_mention_rate:.1f}% requires immediate action.</div>" if overall_mention_rate < 20 else ''}
</section>

<!-- SECTION 2: COMPETITIVE LANDSCAPE -->
<section class="section">
    <div class="section-header">
        <div class="section-number">2</div>
        <div>
            <div class="section-title">Generic Query Competitive Analysis</div>
            <div class="section-subtitle">{len(analysis['by_query_type']['generic']['queries'])} Non-Branded Queries | The TRUE Market Position</div>
        </div>
    </div>

    <div class="callout">
        <strong>📌 WHY THIS MATTERS:</strong> Branded queries show AI knows you exist. Generic queries reveal if you're actually recommended. This is where market share is won or lost.
    </div>

    <h3>Share of Voice Rankings</h3>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Brand</th>
                    <th>Total Mentions</th>
                    <th>Mention Rate</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""

        # Add competitor rankings
        for i, (brand, mentions) in enumerate(competitor_rankings[:10]):
            rank_num = i + 1
            mention_rate = (mentions / analysis['total_responses'] * 100)
            is_our_brand = (brand == self.brand_name)

            if rank_num <= 3:
                rank_badge = f'<span class="rank-badge">#{rank_num}</span>'
            else:
                rank_badge = str(rank_num)

            if rank_num == 1 and not is_our_brand:
                status = '<span class="status-critical">🔴 Competitor Lead</span>'
            elif is_our_brand:
                status = '<span class="status-warning">🟡 Your Position</span>'
            else:
                status = '<span class="status-neutral">⚪ Following</span>'

            html += f"""
                <tr>
                    <td>{rank_badge}</td>
                    <td class="{'strong' if is_our_brand else ''}">{brand}</td>
                    <td>{mentions}</td>
                    <td class="strong">{mention_rate:.1f}%</td>
                    <td>{status}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
"""

        # Platform performance
        html += """
    <h3>Performance by Platform (All Queries)</h3>
    <div class="platform-grid">
"""

        for platform, perf in sorted(analysis['by_platform'].items(), key=lambda x: x[1]['mention_rate'], reverse=True):
            performance_class = ''
            if perf['mention_rate'] >= 50:
                performance_status = '✅ Strong Performance'
                performance_class = 'success'
            elif perf['mention_rate'] >= 30:
                performance_status = '⚠️ Moderate'
                performance_class = 'warning'
            else:
                performance_status = '🚨 Needs Improvement'
                performance_class = 'critical'

            html += f"""
        <div class="platform-card">
            <div class="platform-name">{platform}</div>
            <div class="stat-value" style="font-size: 60px;">{perf['mention_rate']:.1f}%</div>
            <div class="stat-description"><strong>{self.brand_short} Mentions:</strong> {perf['brand_mentions']}/{perf['total_responses']}</div>
            <div class="stat-description status-{performance_class}" style="margin-top: 15px;">{performance_status}</div>
        </div>
"""

        html += """
    </div>
</section>
"""

        # Zero-mention queries section
        if analysis['zero_mention_queries']:
            html += f"""
<!-- SECTION 3: CRITICAL QUERIES -->
<section class="section">
    <div class="section-header">
        <div class="section-number">3</div>
        <div>
            <div class="section-title">🎯 Zero-Mention Generic Queries</div>
            <div class="section-subtitle">Highest Priority Optimization Targets</div>
        </div>
    </div>

    <p style="margin-bottom: 20px;">These generic queries returned zero {self.brand_short} mentions across all platforms - immediate optimization targets:</p>

    <ul class="query-list">
"""
            for query in sorted(analysis['zero_mention_queries'])[:15]:
                html += f'        <li>{query}</li>\n'

            if len(analysis['zero_mention_queries']) > 15:
                html += f'        <li><strong>...and {len(analysis["zero_mention_queries"]) - 15} more queries</strong></li>\n'

            html += """
    </ul>
</section>
"""

        # Action plan section
        html += self._generate_action_plan(analysis)

        # Footer
        html += f"""
<!-- FOOTER -->
<div class="footer">
    <p><strong>Generated by GEO Query Tracker</strong></p>
    <p>Data Source: {analysis['total_queries']} queries tested across {len(analysis['by_platform'])} AI platforms</p>
</div>

</div>
</div>
</body>
</html>
"""

        # Save report
        with open(output_path, 'w') as f:
            f.write(html)

        print(f"✅ Report saved to: {output_path}")
        return output_path

    def _generate_action_plan(self, analysis):
        """Generate intelligent tiered action plan"""
        overall_rate = (analysis['brand_mentions'] / analysis['total_responses'] * 100) if analysis['total_responses'] > 0 else 0
        generic_rate = analysis['by_query_type']['generic']['mention_rate']

        # Get worst performing platform
        worst_platform = min(analysis['by_platform'].items(), key=lambda x: x[1]['mention_rate']) if analysis['by_platform'] else None

        html = """
<!-- SECTION 4: ACTION PLAN -->
<section class="section">
    <div class="section-header">
        <div class="section-number">4</div>
        <div>
            <div class="section-title">🎯 Prioritized Action Plan</div>
            <div class="section-subtitle">Based on ROI potential and competitive gaps</div>
        </div>
    </div>

    <h3>🔥 TIER 1: Immediate High-Impact Actions</h3>
"""

        # Dynamic Tier 1 recommendations
        tier1_count = 1

        # If worst platform is really bad
        if worst_platform and worst_platform[1]['mention_rate'] < 20:
            html += f"""
    <div class="action-item tier-1">
        <h4>{tier1_count}. Fix {worst_platform[0]} Gap ({worst_platform[1]['mention_rate']:.1f}% mention rate):</h4>
        <p>Create comprehensive content optimized for {worst_platform[0]}'s training data. Focus on authoritative, well-structured information.</p>
        <p style="margin-top: 10px;"><strong>Target:</strong> Increase {worst_platform[0]} mention rate from {worst_platform[1]['mention_rate']:.1f}% to 35% within 30 days</p>
    </div>
"""
            tier1_count += 1

        # If there are zero-mention queries
        if len(analysis['zero_mention_queries']) > 0:
            html += f"""
    <div class="action-item tier-1">
        <h4>{tier1_count}. Target {len(analysis['zero_mention_queries'])} Zero-Mention Generic Queries:</h4>
        <p>Create definitive content for high-value queries where {self.brand_short} currently has zero visibility.</p>
        <p style="margin-top: 10px;"><strong>Target:</strong> Achieve 30% mention rate across these queries within 60 days</p>
    </div>
"""
            tier1_count += 1

        # If generic performance is lower than overall
        if generic_rate < overall_rate - 10:
            html += f"""
    <div class="action-item tier-1">
        <h4>{tier1_count}. Improve Generic Query Performance:</h4>
        <p>Generic mention rate ({generic_rate:.1f}%) lags overall performance. Focus on category-defining content and thought leadership.</p>
        <p style="margin-top: 10px;"><strong>Target:</strong> Close the gap between generic and overall mention rates</p>
    </div>
"""
            tier1_count += 1

        # Check if competitor is ahead
        competitor_rankings = sorted(analysis['competitors_share_of_voice'].items(), key=lambda x: x[1], reverse=True)
        if competitor_rankings[0][0] != self.brand_name:
            top_competitor = competitor_rankings[0][0]
            html += f"""
    <div class="action-item tier-1">
        <h4>{tier1_count}. Competitive Content Strategy vs {top_competitor}:</h4>
        <p>{top_competitor} currently leads in share of voice. Analyze their content strategy and create comparison/alternative content.</p>
        <p style="margin-top: 10px;"><strong>Target:</strong> Capture leadership position within 90 days</p>
    </div>
"""

        html += """
    <h3>⚡ TIER 2: Medium-Term Optimization</h3>

    <div class="action-item tier-2">
        <h4>1. Platform-Specific Content Optimization:</h4>
        <p>Create platform-specific content strategies based on each AI's training preferences and citation patterns</p>
    </div>

    <div class="action-item tier-2">
        <h4>2. Fill Citation Gaps:</h4>
        <p>Ensure authoritative publications and review sites have comprehensive brand coverage</p>
    </div>

    <div class="action-item tier-2">
        <h4>3. Enhance Structured Data:</h4>
        <p>Implement comprehensive schema markup and structured data across all web properties</p>
    </div>

    <h3>🔄 TIER 3: Ongoing Maintenance</h3>

    <div class="action-item tier-3">
        <h4>1. Monitor & Refine Branded Queries:</h4>
        <p>Maintain strong performance on branded queries while improving accuracy of information</p>
    </div>

    <div class="action-item tier-3">
        <h4>2. Track Competitor Movements:</h4>
        <p>Weekly monitoring of competitor strategy and positioning shifts</p>
    </div>

    <div class="action-item tier-3">
        <h4>3. Platform Diversification:</h4>
        <p>Prepare for emerging AI platforms before they gain significant market share</p>
    </div>
</section>
"""

        return html

    def _get_figma_css(self):
        """Return Figma design system CSS"""
        return """
        /* Figma Design System - Exact Specifications */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Helvetica Neue', -apple-system, sans-serif;
            background: #f5f5f5;
            color: #000000;
        }

        .page-wrapper {
            background: white;
            max-width: 1920px;
            margin: 0 auto;
        }

        .container {
            width: 1400px;
            margin: 0 auto;
            padding: 40px;
        }

        /* HEADER */
        .report-header {
            padding: 61px 0 40px;
            border-bottom: 2px solid #000000;
        }

        .brand-title {
            font-size: 19.2px;
            font-weight: 700;
            line-height: 28.8px;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .report-title {
            font-size: 28.8px;
            font-weight: 700;
            line-height: 43.2px;
            margin-bottom: 12px;
        }

        .report-meta {
            font-size: 14.4px;
            line-height: 21.6px;
            color: #666666;
            text-align: right;
        }

        /* SECTIONS */
        .section {
            padding: 40px 0;
            border-bottom: 2px solid #000000;
        }

        .section-header {
            display: flex;
            align-items: baseline;
            margin-bottom: 30px;
        }

        .section-number {
            background: #000000;
            color: #FFFFFF;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 21px;
            font-weight: 700;
            margin-right: 20px;
            flex-shrink: 0;
        }

        .section-title {
            font-size: 29.1px;
            font-weight: 700;
            line-height: 48px;
        }

        .section-subtitle {
            font-size: 14.4px;
            line-height: 21.6px;
            color: #666666;
            margin-top: 4px;
        }

        h3 {
            font-size: 22.4px;
            font-weight: 700;
            line-height: 33.6px;
            margin: 30px 0 20px;
        }

        h4 {
            font-size: 18.4px;
            font-weight: 700;
            line-height: 28.6px;
            margin: 0 0 10px;
        }

        /* STAT CARDS */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 30px 0;
        }

        .stat-card {
            background: #FFFFFF;
            border: 2px solid #000000;
            padding: 24px 20px;
            text-align: center;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .stat-label {
            font-size: 12px;
            line-height: 18px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 72px;
            font-weight: 700;
            line-height: 1;
            margin: 15px 0;
        }

        .stat-description {
            font-size: 12px;
            line-height: 18px;
            color: #666666;
        }

        /* CALLOUTS */
        .callout {
            background: #FFFFFF;
            border: 2px solid #000000;
            padding: 25px 26px;
            margin: 30px 0;
            font-size: 15.8px;
            line-height: 32px;
        }

        .callout-critical {
            background: #FEE2E2;
            border-color: #DC2626;
        }

        .callout-warning {
            background: #FEF3C7;
            border-color: #F59E0B;
        }

        .callout-success {
            background: #D1FAE5;
            border-color: #10B981;
        }

        /* TABLES */
        .table-container {
            background: #FFFFFF;
            border: 2px solid #000000;
            margin: 30px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        table thead {
            background: #000000;
            color: #FFFFFF;
        }

        table th {
            font-size: 15.9px;
            font-weight: 700;
            padding: 16px;
            text-align: left;
            border-right: 1px solid #FFFFFF;
        }

        table th:last-child {
            border-right: none;
        }

        table td {
            font-size: 15.9px;
            padding: 15.5px 16px;
            border-right: 1px solid #E0E0E0;
            border-bottom: 1px solid #E0E0E0;
        }

        table td:last-child {
            border-right: none;
        }

        table td.strong {
            font-weight: 700;
        }

        .rank-badge {
            background: #000000;
            color: #FFFFFF;
            padding: 5px 15px;
            display: inline-block;
            font-size: 14.4px;
            font-weight: 700;
        }

        /* STATUS COLORS */
        .status-critical { color: #DC2626; }
        .status-warning { color: #F59E0B; }
        .status-neutral { color: #6B7280; }
        .status-success { color: #10B981; }

        /* PLATFORM CARDS */
        .platform-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 30px 0;
        }

        .platform-card {
            background: #FFFFFF;
            border: 2px solid #000000;
            padding: 31px 27px;
            text-align: center;
            min-height: 220px;
        }

        .platform-name {
            font-size: 19.2px;
            font-weight: 700;
            line-height: 28.8px;
            margin-bottom: 20px;
        }

        /* LISTS */
        .query-list {
            list-style: none;
            padding: 0;
            margin: 20px 0;
        }

        .query-list li {
            background: #FFFFFF;
            border: 2px solid #000000;
            padding: 19px 16px;
            margin: 10px 0;
            font-size: 15.9px;
            line-height: 32px;
        }

        /* ACTION ITEMS */
        .action-item {
            background: #FFFFFF;
            border: 2px solid #000000;
            padding: 25px 26px;
            margin: 20px 0;
        }

        .action-item.tier-1 {
            border-left: 6px solid #DC2626;
        }

        .action-item.tier-2 {
            border-left: 6px solid #F59E0B;
        }

        .action-item.tier-3 {
            border-left: 6px solid #10B981;
        }

        /* FOOTER */
        .footer {
            text-align: center;
            padding: 40px;
            font-size: 14.4px;
            color: #666666;
            border-top: 2px solid #000000;
        }

        /* RESPONSIVE */
        @media (max-width: 1400px) {
            .container {
                width: 100%;
                padding: 40px 20px;
            }

            .stats-grid,
            .platform-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 768px) {
            .stats-grid,
            .platform-grid {
                grid-template-columns: 1fr;
            }
        }
        """

    def generate_report(self, output_path='advanced_report.html'):
        """Main report generation workflow"""
        print("\n" + "="*60)
        print("🚀 ADVANCED GEO REPORT GENERATOR")
        print("="*60 + "\n")

        # Fetch data
        data = self.fetch_data()

        # Analyze
        print("🔍 Analyzing data with competitive intelligence...")
        analysis = self.analyze_data(data)

        # Print summary
        print("\n" + "-"*60)
        print("ANALYSIS SUMMARY:")
        print("-"*60)
        print(f"Total Queries: {analysis['total_queries']}")
        print(f"  - Generic: {len(analysis['by_query_type']['generic']['queries'])}")
        print(f"  - Branded: {len(analysis['by_query_type']['branded']['queries'])}")
        print(f"  - Competitor: {len(analysis['by_query_type']['competitor']['queries'])}")
        print(f"\n{self.brand_short} Overall Mention Rate: {(analysis['brand_mentions'] / analysis['total_responses'] * 100):.1f}%")
        print(f"{self.brand_short} Generic Query Rate: {analysis['by_query_type']['generic']['mention_rate']:.1f}%")
        print(f"Zero-Mention Queries: {len(analysis['zero_mention_queries'])}")
        print("-"*60 + "\n")

        # Generate HTML
        print("📝 Generating comprehensive HTML report...")
        report_path = self.generate_html_report(analysis, output_path)

        return report_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate advanced GEO audit report')
    parser.add_argument('--sheet', type=str, help='Worksheet name', required=True)
    parser.add_argument('--brand', '-b', type=str, help='Brand name', required=True)
    parser.add_argument('--config', type=str, default='config.json', help='Config file path')
    parser.add_argument('--output', type=str, default='advanced_geo_report.html', help='Output file path')

    args = parser.parse_args()

    generator = AdvancedGEOReportGenerator(
        config_path=args.config,
        sheet_name=args.sheet,
        brand_name=args.brand
    )

    report_path = generator.generate_report(output_path=args.output)

    print("\n" + "="*60)
    print("✅ ADVANCED REPORT COMPLETE!")
    print("="*60)
    print(f"\n📄 Open this file in your browser:")
    print(f"   {report_path}\n")


if __name__ == '__main__':
    main()
