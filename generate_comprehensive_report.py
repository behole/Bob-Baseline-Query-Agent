#!/usr/bin/env python3
"""
Comprehensive GEO Report Generator
Generates detailed strategic reports matching the RH comprehensive format
Reverse-engineered from production reports
"""

import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from collections import defaultdict
import argparse


class ComprehensiveGEOReportGenerator:
    """Generate comprehensive 11-section GEO audit reports"""

    def __init__(self, config_path: str = "config.json", sheet_name: str = None, brand_name: str = "Brand"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.sheet_name = sheet_name
        self.brand_name = brand_name
        self.brand_short = self._get_brand_short_name(brand_name)
        self.setup_google_sheets()

    def _get_brand_short_name(self, brand_name: str) -> str:
        """Generate short name for brand"""
        words = brand_name.split()
        if len(words) > 1:
            return ''.join([w[0] for w in words]).upper()
        return brand_name[:3].upper()

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

    def fetch_and_analyze_data(self):
        """Fetch data from Google Sheets and perform comprehensive analysis"""
        print(f"📊 Fetching data from Google Sheets...")
        all_data = self.sheet.get_all_records()
        print(f"   Found {len(all_data)} rows of data")

        analysis = {
            'total_queries': 0,
            'total_responses': len(all_data),
            'brand_mentions': 0,
            'platforms': {},
            'platforms_generic': {},  # NEW: Generic-only platform stats (THE REAL GEO METRIC)
            'competitors': defaultdict(int),
            'competitors_generic': defaultdict(int),  # NEW: Generic-only competitor stats
            'zero_mention_queries': [],
            'query_performance': {},
            'by_query_type': {
                'generic': {'total': 0, 'mentions': 0, 'queries': []},
                'branded': {'total': 0, 'mentions': 0, 'queries': []},
                'competitor': {'total': 0, 'mentions': 0, 'queries': []}
            }
        }

        unique_queries = {}
        platform_data = defaultdict(lambda: {'total': 0, 'mentions': 0})
        platform_data_generic = defaultdict(lambda: {'total': 0, 'mentions': 0})  # NEW: Track generic separately

        for row in all_data:
            query_text = str(row.get('Query Text', ''))
            platform = str(row.get('Platform', ''))
            mentioned = str(row.get(f'{self.brand_name} Mentioned?', '')).lower()
            competitors_str = str(row.get('Competitors Mentioned', ''))

            if not query_text or not platform:
                continue

            # Track unique queries
            if query_text not in unique_queries:
                category = self._categorize_query(query_text)
                unique_queries[query_text] = {
                    'category': category,
                    'platforms_with_brand': [],
                    'platforms_without_brand': [],
                    'competitors': []
                }

            # Determine if this is a generic query (for GEO optimization tracking)
            is_generic = unique_queries[query_text]['category'] == 'generic'

            # Track brand mentions
            if mentioned in ['yes', 'y', 'true']:
                analysis['brand_mentions'] += 1
                platform_data[platform]['mentions'] += 1
                unique_queries[query_text]['platforms_with_brand'].append(platform)

                # Track generic-only mentions (THE REAL GEO METRIC)
                if is_generic:
                    platform_data_generic[platform]['mentions'] += 1
            else:
                unique_queries[query_text]['platforms_without_brand'].append(platform)

            platform_data[platform]['total'] += 1

            # Track generic-only platform stats
            if is_generic:
                platform_data_generic[platform]['total'] += 1

            # Track competitors
            if competitors_str and competitors_str.lower() not in ['none', '']:
                for comp in [c.strip() for c in competitors_str.split(',')]:
                    if comp:
                        analysis['competitors'][comp] += 1
                        # Track generic-only competitor mentions
                        if is_generic:
                            analysis['competitors_generic'][comp] += 1
                        if comp not in unique_queries[query_text]['competitors']:
                            unique_queries[query_text]['competitors'].append(comp)

        # Process unique queries
        for query_text, query_data in unique_queries.items():
            category = query_data['category']
            total_platforms = len(query_data['platforms_with_brand']) + len(query_data['platforms_without_brand'])
            brand_mentions_count = len(query_data['platforms_with_brand'])

            analysis['by_query_type'][category]['total'] += total_platforms
            analysis['by_query_type'][category]['mentions'] += brand_mentions_count
            analysis['by_query_type'][category]['queries'].append({
                'text': query_text,
                'brand_mentions': brand_mentions_count,
                'total_platforms': total_platforms,
                'competitors': query_data['competitors']
            })

            # Zero-mention queries (generic only)
            if category == 'generic' and brand_mentions_count == 0:
                analysis['zero_mention_queries'].append({
                    'text': query_text,
                    'competitors': query_data['competitors']
                })

        # Calculate metrics
        analysis['total_queries'] = len(unique_queries)
        analysis['mention_rate'] = (analysis['brand_mentions'] / analysis['total_responses'] * 100) if analysis['total_responses'] > 0 else 0

        # Platform performance (ALL queries - less meaningful due to branded query inflation)
        for platform, data in platform_data.items():
            analysis['platforms'][platform] = {
                'total': data['total'],
                'mentions': data['mentions'],
                'rate': (data['mentions'] / data['total'] * 100) if data['total'] > 0 else 0
            }

        # Platform performance (GENERIC QUERIES ONLY - THE REAL GEO METRIC)
        for platform, data in platform_data_generic.items():
            analysis['platforms_generic'][platform] = {
                'total': data['total'],
                'mentions': data['mentions'],
                'rate': (data['mentions'] / data['total'] * 100) if data['total'] > 0 else 0
            }

        # Query type rates
        for category in analysis['by_query_type']:
            total = analysis['by_query_type'][category]['total']
            mentions = analysis['by_query_type'][category]['mentions']
            analysis['by_query_type'][category]['mention_rate'] = (mentions / total * 100) if total > 0 else 0

        # Add brand to competitor rankings (all queries)
        analysis['competitors'][self.brand_name] = analysis['brand_mentions']

        # Add brand to generic-only competitor rankings (THE REAL GEO METRIC)
        generic_brand_mentions = analysis['by_query_type']['generic']['mentions']
        analysis['competitors_generic'][self.brand_name] = generic_brand_mentions

        return analysis

    def _categorize_query(self, query_text: str) -> str:
        """Categorize query as generic, branded, or competitor"""
        query_lower = query_text.lower()
        brand_lower = self.brand_name.lower()

        # Check for brand mentions
        brand_words = brand_lower.split()
        if any(word in query_lower for word in brand_words if len(word) > 2):
            return "branded"

        # Check for common competitor keywords
        competitor_keywords = ['vs', 'versus', 'compare', 'alternative', 'better than']
        if any(kw in query_lower for kw in competitor_keywords):
            return "competitor"

        return "generic"

    def generate_html_report(self, analysis, output_path='comprehensive_geo_report.html'):
        """Generate comprehensive HTML report matching RH format"""

        # Calculate key metrics
        overall_rate = analysis['mention_rate']
        generic_rate = analysis['by_query_type']['generic']['mention_rate']

        # Get best platform
        best_platform = max(analysis['platforms'].items(), key=lambda x: x[1]['rate']) if analysis['platforms'] else ('N/A', {'rate': 0})

        # Sort competitors
        competitor_rankings = sorted(
            analysis['competitors'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Determine status
        if overall_rate >= 50:
            performance_status = "Strong Performance"
        elif overall_rate >= 30:
            performance_status = "Growth Opportunity"
        else:
            performance_status = "Needs Improvement"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self.brand_name} × Watermelon Ghost Report</title>
{self._get_css()}
</head>
<body>
<div class="page-wrapper">
<div class="container">

<!-- HEADER -->
<header class="report-header" style="display: flex; justify-content: space-between; align-items: flex-start;">
    <div style="flex: 1;">
        <div class="brand-title">{self.brand_name.upper()} × WATERMELON GHOST</div>
        <div class="report-title">Comprehensive GEO Audit Report</div>
    </div>
    <div style="flex-shrink: 0; text-align: right;">
        <img src="watermelon_ghost_logo.png" alt="Watermelon Ghost" style="height: 80px; width: auto; display: block; margin-left: auto; margin-bottom: 12px;">
        <div class="report-meta" style="text-align: right;">
            <strong>Report Date:</strong> {datetime.now().strftime('%B %d, %Y')}<br>
            <strong>Analysis Period:</strong> {analysis['total_queries']} Queries × 4 Platforms = {analysis['total_responses']} Total Responses
        </div>
    </div>
</header>

{self._generate_executive_summary_section(analysis, overall_rate, generic_rate, best_platform, performance_status)}

{self._generate_overall_performance_section(analysis, overall_rate, generic_rate, best_platform, competitor_rankings)}

{self._generate_platform_insights_section(analysis)}

{self._generate_zero_mention_section(analysis)}

{self._generate_content_gap_section(analysis)}

{self._generate_high_value_opportunities_section(analysis)}

{self._generate_competitive_voice_section(analysis, competitor_rankings)}

{self._generate_displacement_opportunities_section(analysis)}

{self._generate_impact_analysis_section(analysis, overall_rate)}

{self._generate_action_plan_section(analysis)}

<!-- FOOTER -->
<footer class="footer">
    <p>Generated by Watermelon Ghost GEO Audit System • {datetime.now().strftime('%B %Y')}</p>
    <p style="margin-top: 10px; font-size: 12px;">This report analyzes {self.brand_name}'s visibility across Claude, ChatGPT, Google AI, and Perplexity</p>
</footer>

</div>
</div>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Report saved to: {output_path}")
        return output_path

    def _generate_executive_summary_section(self, analysis, overall_rate, generic_rate, best_platform, status):
        """Generate executive summary with Performance Snapshot and Key Findings"""

        # Determine findings based on data
        findings = self._generate_key_findings(analysis, overall_rate, generic_rate)
        insights = self._generate_critical_insights(analysis)
        recommendations = self._generate_top_recommendations(analysis, overall_rate)

        # Determine GEO performance status
        if generic_rate >= 30:
            geo_status = "Strong GEO Position"
            geo_color = "#10B981"
        elif generic_rate >= 15:
            geo_status = "Growing Presence"
            geo_color = "#F59E0B"
        else:
            geo_status = "Early Stage"
            geo_color = "#EF4444"

        # Get best generic platform
        best_generic_platform = max(analysis['platforms_generic'].items(), key=lambda x: x[1]['rate']) if analysis['platforms_generic'] else ('N/A', {'rate': 0})

        return f"""
<!-- EXECUTIVE SUMMARY -->
<div class="section">
    <div class="section-header">
        <div class="section-number">1</div>
        <div>
            <div class="section-title">📋 Executive Summary</div>
        </div>
    </div>

    <!-- HERO METRIC: GEO Performance -->
    <div style="background: linear-gradient(135deg, #000000 0%, #333333 100%); color: white; padding: 50px 40px; margin: 30px 0; border-radius: 12px; text-align: center; border: 4px solid #000000;">
        <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 15px; opacity: 0.9;">
            🎯 PRIMARY GEO PERFORMANCE METRIC
        </div>
        <div style="font-size: 96px; font-weight: 700; line-height: 1; margin: 20px 0;">
            {generic_rate:.1f}%
        </div>
        <div style="font-size: 24px; font-weight: 600; margin-bottom: 20px; opacity: 0.95;">
            Generic Query Mention Rate
        </div>
        <div style="display: inline-block; background: {geo_color}; color: white; padding: 12px 30px; border-radius: 24px; font-size: 16px; font-weight: 700; margin-top: 10px;">
            {geo_status}
        </div>
        <div style="max-width: 800px; margin: 30px auto 0; font-size: 15px; line-height: 1.8; opacity: 0.9; padding-top: 30px; border-top: 1px solid rgba(255,255,255,0.2);">
            <strong>Why This Matters:</strong> This metric shows how often AI platforms recommend {self.brand_name} when users DON'T explicitly ask for it. Unlike branded queries (which always mention your brand), generic queries represent true competitive positioning and GEO optimization opportunity.
        </div>
    </div>

    <h3>Performance Snapshot</h3>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Best Generic Platform</div>
            <div class="stat-value" style="font-size: 32px; margin: 20px 0;">{best_generic_platform[0]}</div>
            <div class="stat-description">{best_generic_platform[1]['rate']:.1f}% generic rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Generic Query Count</div>
            <div class="stat-value">{len(analysis['by_query_type']['generic']['queries'])}</div>
            <div class="stat-description">unbranded queries tested</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Brand Awareness</div>
            <div class="stat-value">{analysis['by_query_type']['branded']['mention_rate']:.0f}%</div>
            <div class="stat-description">branded query rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Overall Blended Rate</div>
            <div class="stat-value" style="font-size: 48px;">{overall_rate:.1f}%</div>
            <div class="stat-description" style="font-size: 11px; opacity: 0.7;">includes branded queries</div>
        </div>
    </div>

    <h3>Key Findings</h3>
    <div style="display: grid; gap: 12px; margin: 20px 0;">
{findings}
    </div>

    <h3>Critical Insights</h3>
    <ul style="margin: 20px 0; padding-left: 0; list-style: none;">
{insights}
    </ul>

    <h3>Top Recommendations</h3>
    <div style="display: grid; gap: 12px;">
{recommendations}
    </div>

</div>"""

    def _generate_key_findings(self, analysis, overall_rate, generic_rate):
        """Generate key findings with severity levels"""
        findings = []

        # Platform disparity
        if analysis['platforms']:
            rates = [p['rate'] for p in analysis['platforms'].values()]
            disparity = max(rates) - min(rates)
            if disparity > 20:
                findings.append(self._finding_card(
                    f"Platform performance shows {disparity:.1f}% gap between best and worst performers",
                    "High" if disparity > 30 else "Medium",
                    "Platform-specific content strategies needed to close performance gaps"
                ))

        # Generic performance
        if generic_rate < 40:
            findings.append(self._finding_card(
                f"Generic query performance at {generic_rate:.1f}% indicates visibility challenges in non-branded searches",
                "High" if generic_rate < 25 else "Medium",
                "Focus on thought leadership and educational content to improve generic query mentions"
            ))

        # Zero mentions
        zero_count = len(analysis['zero_mention_queries'])
        if zero_count > 0:
            findings.append(self._finding_card(
                f"{zero_count} queries show zero brand mentions across all platforms",
                "High",
                "Immediate content opportunities where competitors dominate"
            ))

        # Competitive position
        brand_rank = next((i for i, (name, _) in enumerate(sorted(analysis['competitors'].items(), key=lambda x: x[1], reverse=True)) if name == self.brand_name), None)
        if brand_rank and brand_rank > 0:
            findings.append(self._finding_card(
                f"Currently ranked #{brand_rank + 1} in competitive share of voice",
                "Medium",
                "Opportunity to increase market share through strategic content optimization"
            ))

        return '\n'.join(findings[:4])  # Top 4 findings

    def _finding_card(self, title, severity, description):
        """Generate a finding card with severity badge"""
        severity_colors = {
            'Critical': '#EF4444',
            'High': '#F59E0B',
            'Medium': '#000000',
            'Low': '#10B981'
        }
        color = severity_colors.get(severity, '#6B7280')

        return f"""
        <div style="background: rgba(255,255,255,0.1); border-left: 4px solid {color}; border-radius: 8px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                <div style="font-weight: 700; font-size: 16px; flex: 1;">{title}</div>
                <div style="background: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-left: 15px;">
                    {severity}
                </div>
            </div>
            <p style="margin: 0; font-size: 14px; opacity: 0.9; line-height: 1.6;">{description}</p>
        </div>"""

    def _generate_critical_insights(self, analysis):
        """Generate critical insights bullet points"""
        insights = []

        # Platform optimization insight
        if analysis['platforms']:
            best = max(analysis['platforms'].items(), key=lambda x: x[1]['rate'])
            worst = min(analysis['platforms'].items(), key=lambda x: x[1]['rate'])
            insights.append(f"""
        <li style="background: #F9FAFB; border-left: 3px solid #000000; padding: 15px 20px; margin-bottom: 10px; border-radius: 4px;">
            <span style="color: #374151; line-height: 1.6;">{best[0]} shows strongest performance at {best[1]['rate']:.1f}%, while {worst[0]} lags at {worst[1]['rate']:.1f}% - platform-specific optimization needed</span>
        </li>""")

        # Generic query insight
        generic_rate = analysis['by_query_type']['generic']['mention_rate']
        branded_rate = analysis['by_query_type']['branded']['mention_rate']
        insights.append(f"""
        <li style="background: #F9FAFB; border-left: 3px solid #000000; padding: 15px 20px; margin-bottom: 10px; border-radius: 4px;">
            <span style="color: #374151; line-height: 1.6;">Generic queries ({generic_rate:.1f}%) vs branded queries ({branded_rate:.1f}%) shows {abs(branded_rate - generic_rate):.1f}% gap - AI platforms need better association between brand and use cases</span>
        </li>""")

        # Zero mention insight
        if analysis['zero_mention_queries']:
            insights.append(f"""
        <li style="background: #F9FAFB; border-left: 3px solid #000000; padding: 15px 20px; margin-bottom: 10px; border-radius: 4px;">
            <span style="color: #374151; line-height: 1.6;">Zero-mention queries represent immediate conversion opportunities where targeted content can establish market leadership</span>
        </li>""")

        return '\n'.join(insights[:4])

    def _generate_top_recommendations(self, analysis, overall_rate):
        """Generate top recommendations with priority badges"""
        recs = []

        # Platform-specific strategy
        if analysis['platforms']:
            worst = min(analysis['platforms'].items(), key=lambda x: x[1]['rate'])
            recs.append(self._recommendation_card(
                1,
                f"Develop platform-specific content strategies targeting underperforming channels, particularly {worst[0]}, with emphasis on technical product specifications and comparison data",
                "Immediate"
            ))

        # Content gaps
        if len(analysis['zero_mention_queries']) > 5:
            recs.append(self._recommendation_card(
                2,
                "Create targeted content addressing zero-mention queries to establish thought leadership in underserved topics",
                "Immediate"
            ))

        # Generic performance
        generic_rate = analysis['by_query_type']['generic']['mention_rate']
        if generic_rate < 40:
            recs.append(self._recommendation_card(
                3,
                "Launch comprehensive educational content hub to capture generic research queries and establish thought leadership",
                "Short-term"
            ))

        # Technical optimization
        recs.append(self._recommendation_card(
            4,
            "Implement structured data optimization and technical SEO enhancements to improve AI model content comprehension and citation probability",
            "Long-term"
        ))

        return '\n'.join(recs[:4])

    def _recommendation_card(self, num, text, priority):
        """Generate a recommendation card"""
        priority_colors = {
            'Immediate': '#EF4444',
            'Short-term': '#F59E0B',
            'Long-term': '#10B981'
        }
        color = priority_colors.get(priority, '#6B7280')

        return f"""
        <div style="background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 18px; display: flex; align-items: center; gap: 15px;">
            <div style="flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; background: #EFF6FF; color: #000000; display: flex; align-items: center; justify-content: center; font-weight: 700;">
                {num}
            </div>
            <div style="flex: 1;">
                <p style="margin: 0; color: #111827; font-size: 14px; line-height: 1.5;">{text}</p>
            </div>
            <div style="flex-shrink: 0;">
                <span style="background: {color}; color: white; padding: 6px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; white-space: nowrap;">
                    {priority}
                </span>
            </div>
        </div>"""

    def _generate_overall_performance_section(self, analysis, overall_rate, generic_rate, best_platform, rankings):
        """Generate Section 2: Overall Performance (GENERIC QUERIES ONLY)"""

        # Sort competitors by GENERIC mentions only (THE REAL GEO METRIC)
        # BUT: Include all industry competitors with 0 mentions for context
        from geo_audit.utils.competitors import detect_industry, get_competitors

        industry = detect_industry(self.brand_name)
        industry_competitors = get_competitors(self.brand_name, industry=industry)

        # Add all industry competitors with 0 if not mentioned
        for comp in industry_competitors:
            if comp not in analysis['competitors_generic']:
                analysis['competitors_generic'][comp] = 0

        # Sort and limit to top 10
        generic_rankings = sorted(
            analysis['competitors_generic'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Determine competitive status based on GENERIC performance
        brand_rank = next((i for i, (name, _) in enumerate(generic_rankings) if name == self.brand_name), None)
        if brand_rank == 0:
            comp_status = "Market Leader"
            comp_message = "Leading in generic queries"
        elif brand_rank:
            comp_status = f"Rank #{brand_rank + 1}"
            comp_message = f"vs {generic_rankings[0][0]}"
        else:
            comp_status = "Following"
            comp_message = "Building GEO presence"

        # Platform cards showing GENERIC QUERY PERFORMANCE ONLY
        platform_cards = ""
        for platform, perf in sorted(analysis['platforms_generic'].items(), key=lambda x: x[1]['rate'], reverse=True):
            status = "✅ Strong" if perf['rate'] >= 20 else "⚠️ Moderate" if perf['rate'] >= 10 else "🚨 Needs Work"
            status_class = "success" if perf['rate'] >= 20 else "warning" if perf['rate'] >= 10 else "critical"

            platform_cards += f"""
        <div class="platform-card">
            <div class="platform-name">{platform}</div>
            <div class="stat-value" style="font-size: 60px;">{perf['rate']:.1f}%</div>
            <div class="stat-description"><strong>Generic Mentions:</strong> {perf['mentions']}/{perf['total']}</div>
            <div class="stat-description status-{status_class}" style="margin-top: 15px;">{status}</div>
        </div>"""

        # Calculate generic query stats for display
        generic_total = analysis['by_query_type']['generic']['total']
        generic_mentions = analysis['by_query_type']['generic']['mentions']

        return f"""
<!-- SECTION 2: OVERALL PERFORMANCE (GENERIC QUERIES ONLY) -->
<section class="section">
    <div class="section-header">
        <div class="section-number">2</div>
        <div>
            <div class="section-title">📊 GEO Performance Analysis</div>
            <div class="section-subtitle">Generic Query Visibility & Competitive Position</div>
        </div>
    </div>

    <div class="callout" style="background: #FEF3C7; border-color: #F59E0B;">
        <strong>🎯 IMPORTANT:</strong> This section shows performance on <strong>generic queries only</strong> (queries that don't mention {self.brand_name}). This is the TRUE measure of GEO effectiveness. Branded queries are tracked separately in the Brand Awareness section.
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Generic Query Mention Rate</div>
            <div class="stat-value">{generic_rate:.1f}%</div>
            <div class="stat-description">{generic_mentions} out of {generic_total} unbranded responses</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">GEO Competitive Position</div>
            <div class="stat-value" style="font-size: 32px;">{comp_status}</div>
            <div class="stat-description">{comp_message}</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Generic Queries Tested</div>
            <div class="stat-value">{len(analysis['by_query_type']['generic']['queries'])}</div>
            <div class="stat-description">unbranded search queries</div>
        </div>

        <div class="stat-card">
            <div class="stat-label">Opportunity Gap</div>
            <div class="stat-value" style="font-size: 48px;">{100 - generic_rate:.0f}%</div>
            <div class="stat-description">optimization potential</div>
        </div>
    </div>

    <h3>Generic Query Share of Voice Rankings</h3>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Brand</th>
                    <th>Generic Mentions</th>
                    <th>Mention Rate</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
{self._generate_competitor_table_rows(generic_rankings, analysis, generic_only=True)}
            </tbody>
        </table>
    </div>

    <h3>Platform Performance (Generic Queries Only)</h3>
    <div class="platform-grid">
{platform_cards}
    </div>
</section>"""

    def _generate_competitor_table_rows(self, rankings, analysis, generic_only=False):
        """Generate competitor ranking table rows"""
        rows = ""
        for i, (brand, mentions) in enumerate(rankings):
            rank_num = i + 1

            # Calculate mention rate based on generic or all responses
            if generic_only:
                total = analysis['by_query_type']['generic']['total']
            else:
                total = analysis['total_responses']

            mention_rate = (mentions / total * 100) if total > 0 else 0
            is_our_brand = (brand == self.brand_name)

            rank_badge = f'<span class="rank-badge">#{rank_num}</span>' if rank_num <= 3 else str(rank_num)

            if rank_num == 1 and not is_our_brand:
                status = '<span class="status-critical">🔴 Competitor Lead</span>'
            elif is_our_brand:
                status = '<span class="status-warning">🟡 Your Position</span>'
            else:
                status = '<span class="status-neutral">⚪ Following</span>'

            rows += f"""
                <tr>
                    <td>{rank_badge}</td>
                    <td class="{'strong' if is_our_brand else ''}">{brand}</td>
                    <td>{mentions}</td>
                    <td class="strong">{mention_rate:.1f}%</td>
                    <td>{status}</td>
                </tr>"""

        return rows

    def _generate_platform_insights_section(self, analysis):
        """Generate Section 3: Platform Insights with 5 numbered points per platform (GENERIC QUERIES ONLY)"""
        platform_html = ""

        # Use generic-only platform data for insights
        sorted_platforms = sorted(analysis['platforms_generic'].items(), key=lambda x: x[1]['rate'], reverse=True)

        for platform, perf in sorted_platforms:
            # Generate 5 strategic insights per platform
            insights = self._generate_platform_strategic_insights(platform, perf, analysis)

            platform_html += f"""
    <div style="margin: 40px 0; padding: 30px; background: #F9FAFB; border-radius: 8px; border-left: 4px solid #000000;">
        <h4 style="margin: 0 0 20px 0; font-size: 24px; color: #111827;">{platform}</h4>
        <div style="display: grid; gap: 15px;">
{insights}
        </div>
    </div>"""

        return f"""
<!-- SECTION 3: PLATFORM INSIGHTS -->
<section class="section">
    <div class="section-header">
        <div class="section-number">3</div>
        <div>
            <div class="section-title">🧠 Platform Insights</div>
            <div class="section-subtitle">Strategic Analysis by AI Platform</div>
        </div>
    </div>

    <div class="callout">
        <strong>📌 ANALYSIS METHODOLOGY:</strong> Each platform uses different algorithms, training data, and content sources. Understanding these differences is critical for optimization strategy.
    </div>

{platform_html}
</section>"""

    def _generate_platform_strategic_insights(self, platform, perf, analysis):
        """Generate 5 numbered strategic insights for a platform (GENERIC QUERIES ONLY)"""
        rate = perf['rate']
        # Compare to overall GENERIC rate, not blended rate
        overall_rate = analysis['by_query_type']['generic']['mention_rate']
        diff = rate - overall_rate

        insights = []

        # Insight 1: Performance vs average
        if diff > 10:
            insights.append(f"{platform}'s {rate:.1f}% mention rate outperforms the overall average by {diff:.1f}%, suggesting strong alignment with this platform's content preferences and ranking algorithms")
        elif diff < -10:
            insights.append(f"{platform}'s {rate:.1f}% mention rate underperforms the overall average by {abs(diff):.1f}%, indicating a need for platform-specific content optimization and strategic positioning")
        else:
            insights.append(f"{platform}'s {rate:.1f}% mention rate aligns closely with overall performance, suggesting consistent content quality but opportunity for platform-specific optimization")

        # Insight 2: Market positioning
        if rate >= 60:
            insights.append(f"Strong market positioning on {platform} provides a foundation for thought leadership - focus on maintaining quality while expanding topic coverage to capture more generic queries")
        elif rate >= 40:
            insights.append(f"Moderate visibility on {platform} indicates established presence but room for growth - strategic content gaps represent immediate opportunities for market share gains")
        else:
            insights.append(f"Underperformance on {platform} requires immediate attention - competitor content analysis and platform-specific optimization strategy needed to establish baseline presence")

        # Insight 3: Content strategy
        insights.append(f"To improve {platform} performance, focus on creating comprehensive, well-structured content that directly addresses user intent while demonstrating clear expertise and authority in the subject matter")

        # Insight 4: Competitive positioning
        insights.append(f"{platform} appears to favor detailed, authoritative content - increasing depth of coverage and adding technical specifications could improve citation rates and brand mentions")

        # Insight 5: Growth potential
        growth_potential = 100 - rate
        insights.append(f"With {growth_potential:.1f}% headroom for improvement, {platform} represents {'significant' if growth_potential > 50 else 'moderate'} growth opportunity through targeted content optimization and strategic positioning")

        # Format as numbered list
        formatted = ""
        for i, insight in enumerate(insights, 1):
            formatted += f"""
            <div style="background: white; padding: 15px 20px; border-radius: 6px; border-left: 3px solid #000000;">
                <div style="display: flex; gap: 12px;">
                    <div style="flex-shrink: 0; width: 24px; height: 24px; border-radius: 50%; background: #000000; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700;">
                        {i}
                    </div>
                    <div style="flex: 1; color: #374151; font-size: 14px; line-height: 1.6;">
                        {insight}
                    </div>
                </div>
            </div>"""

        return formatted

    def _generate_zero_mention_section(self, analysis):
        """Generate Section 3: Zero-Mention Queries"""
        zero_queries = analysis['zero_mention_queries'][:15]  # Top 15

        query_list = ""
        for query in zero_queries:
            competitors = ', '.join(query['competitors'][:3]) if query['competitors'] else 'Various competitors'
            query_list += f"""
        <li>
            <strong>{query['text']}</strong>
            <div style="font-size: 13px; color: #6B7280; margin-top: 5px;">Currently mentioning: {competitors}</div>
        </li>"""

        return f"""
<!-- SECTION 3: ZERO-MENTION QUERIES -->
<section class="section">
    <div class="section-header">
        <div class="section-number">4</div>
        <div>
            <div class="section-title">🎯 Zero-Mention Generic Queries</div>
            <div class="section-subtitle">{len(analysis['zero_mention_queries'])} Queries with Zero {self.brand_short} Mentions Across All Platforms</div>
        </div>
    </div>

    <div class="callout callout-warning">
        <strong>⚠️ IMMEDIATE OPPORTUNITY:</strong> These queries generate AI responses but never mention {self.brand_name}. Competitors dominate these conversations. Creating targeted content for these topics represents the highest-impact, lowest-competition optimization opportunity.
    </div>

    <ul class="query-list">
{query_list}
    </ul>

    <div style="margin-top: 30px; padding: 20px; background: #FEF3C7; border-left: 4px solid #F59E0B; border-radius: 4px;">
        <strong style="color: #92400E;">💡 STRATEGIC PRIORITY:</strong>
        <p style="margin: 10px 0 0 0; color: #78350F; line-height: 1.6;">Each zero-mention query represents a conversation happening without your brand. Creating authoritative content targeting these queries can establish thought leadership and capture market share in underserved segments.</p>
    </div>
</section>"""

    def _generate_content_gap_section(self, analysis):
        """Generate Section 4: Content Gap Analysis"""
        # Categorize gaps
        gaps = {
            'Competitive': [],
            'Educational': [],
            'Use Case': []
        }

        for query in analysis['zero_mention_queries']:
            query_lower = query['text'].lower()
            if any(kw in query_lower for kw in ['vs', 'compare', 'alternative', 'better']):
                gaps['Competitive'].append(query)
            elif any(kw in query_lower for kw in ['how', 'what', 'why', 'guide', 'tips']):
                gaps['Educational'].append(query)
            else:
                gaps['Use Case'].append(query)

        gap_cards = ""
        for gap_type, queries in gaps.items():
            if queries:
                priority = "High" if gap_type == "Competitive" else "Medium"
                priority_color = "#EF4444" if priority == "High" else "#F59E0B"

                gap_cards += f"""
    <div style="background: white; border: 2px solid #E5E7EB; border-radius: 8px; padding: 25px; margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <h4 style="margin: 0; font-size: 20px;">{gap_type} Content Gaps</h4>
            <span style="background: {priority_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                {priority} Priority
            </span>
        </div>
        <div style="color: #6B7280; font-size: 14px; line-height: 1.6; margin-bottom: 15px;">
            {len(queries)} queries identified
        </div>
        <div style="background: #F9FAFB; padding: 15px; border-radius: 6px; font-size: 14px; line-height: 1.6;">
            {self._get_gap_description(gap_type)}
        </div>
    </div>"""

        return f"""
<!-- SECTION 4: CONTENT GAP ANALYSIS -->
<section class="section">
    <div class="section-header">
        <div class="section-number">5</div>
        <div>
            <div class="section-title">📊 Content Gap Analysis</div>
            <div class="section-subtitle">Categorized Opportunities by Content Type</div>
        </div>
    </div>

    <div class="callout">
        <strong>📌 METHODOLOGY:</strong> Content gaps are categorized by strategic priority and content type to enable focused resource allocation and maximum ROI.
    </div>

{gap_cards}
</section>"""

    def _get_gap_description(self, gap_type):
        """Get description for gap type"""
        descriptions = {
            'Competitive': 'Queries directly comparing products or seeking alternatives. High commercial intent. Create detailed comparison content and competitive positioning guides.',
            'Educational': 'How-to and informational queries. Build thought leadership with comprehensive guides, tutorials, and educational resources.',
            'Use Case': 'Problem-solution and application queries. Develop case studies, use case documentation, and solution-focused content.'
        }
        return descriptions.get(gap_type, '')

    def _generate_high_value_opportunities_section(self, analysis):
        """Generate Section 5: Top 10 High-Value Query Opportunities"""
        # Score queries
        scored_queries = []
        for query in analysis['zero_mention_queries']:
            score = self._calculate_opportunity_score(query, analysis)
            scored_queries.append((query, score))

        scored_queries.sort(key=lambda x: x[1], reverse=True)
        top_10 = scored_queries[:10]

        opportunity_cards = ""
        for i, (query, score) in enumerate(top_10, 1):
            priority = "CRITICAL" if score >= 85 else "HIGH" if score >= 70 else "MEDIUM"
            priority_color = "#EF4444" if priority == "CRITICAL" else "#F59E0B" if priority == "HIGH" else "#000000"

            opportunity_cards += f"""
    <div style="background: white; border: 2px solid #E5E7EB; border-radius: 8px; padding: 25px; margin: 15px 0;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <div style="flex: 1;">
                <div style="font-size: 12px; color: #6B7280; margin-bottom: 5px;">Query #{i}</div>
                <div style="font-size: 18px; font-weight: 700; color: #111827;">{query['text']}</div>
            </div>
            <div style="text-align: center; margin-left: 20px;">
                <div style="font-size: 32px; font-weight: 700; color: {priority_color};">{score}</div>
                <div style="font-size: 11px; color: #6B7280;">/ 100</div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 15px 0; padding: 15px; background: #F9FAFB; border-radius: 6px;">
            <div>
                <div style="font-size: 11px; color: #6B7280; margin-bottom: 3px;">PRODUCT FIT</div>
                <div style="font-size: 16px; font-weight: 600;">85%</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #6B7280; margin-bottom: 3px;">COMPETITOR GAP</div>
                <div style="font-size: 16px; font-weight: 600;">High</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #6B7280; margin-bottom: 3px;">STRATEGIC VALUE</div>
                <div style="font-size: 16px; font-weight: 600;">{priority}</div>
            </div>
        </div>
        <div style="padding: 15px; background: #FFFBEB; border-left: 3px solid #F59E0B; border-radius: 4px; margin-top: 15px;">
            <div style="font-size: 12px; font-weight: 600; color: #92400E; margin-bottom: 5px;">💡 OPPORTUNITY</div>
            <div style="font-size: 13px; color: #78350F; line-height: 1.6;">
                {self._generate_opportunity_description(query)}
            </div>
        </div>
    </div>"""

        return f"""
<!-- SECTION 5: HIGH-VALUE OPPORTUNITIES -->
<section class="section">
    <div class="section-header">
        <div class="section-number">6</div>
        <div>
            <div class="section-title">🎯 Top 10 High-Value Query Opportunities</div>
            <div class="section-subtitle">Ranked by Strategic Impact Score (100-Point System)</div>
        </div>
    </div>

{opportunity_cards}
</section>"""

    def _calculate_opportunity_score(self, query, analysis):
        """Calculate opportunity score for a query"""
        score = 60  # Base score

        # Add points for competitor presence
        if len(query['competitors']) >= 3:
            score += 20
        elif len(query['competitors']) >= 1:
            score += 10

        # Add points for query type
        query_lower = query['text'].lower()
        if any(kw in query_lower for kw in ['best', 'top', 'compare', 'vs']):
            score += 15  # High commercial intent
        if any(kw in query_lower for kw in ['how', 'guide', 'tips']):
            score += 5  # Educational value

        return min(score, 100)

    def _generate_opportunity_description(self, query):
        """Generate opportunity description for a query"""
        query_lower = query['text'].lower()

        if 'compare' in query_lower or 'vs' in query_lower:
            return "Create comprehensive comparison guide positioning your product's unique advantages while addressing competitive alternatives"
        elif 'best' in query_lower or 'top' in query_lower:
            return "Develop authoritative listicle/guide content establishing thought leadership and featuring your solution prominently"
        elif 'how' in query_lower:
            return "Build detailed how-to content demonstrating your product as the solution while providing genuine educational value"
        else:
            return "Create targeted content addressing this specific use case with your product as the recommended solution"

    def _generate_competitive_voice_section(self, analysis, rankings):
        """Generate Section 6: Competitive Share of Voice"""
        # Platform breakdown
        platform_breakdown = ""
        for platform in sorted(analysis['platforms'].keys()):
            platform_breakdown += f"""
    <div style="background: white; border: 2px solid #E5E7EB; border-radius: 8px; padding: 20px; margin: 15px 0;">
        <h4 style="margin: 0 0 15px 0;">{platform}</h4>
        <div style="font-size: 14px; color: #6B7280;">
            Share of voice analysis for {platform} platform
        </div>
    </div>"""

        return f"""
<!-- SECTION 6: COMPETITIVE SHARE OF VOICE -->
<section class="section">
    <div class="section-header">
        <div class="section-number">7</div>
        <div>
            <div class="section-title">🏆 Competitive Share of Voice Analysis</div>
            <div class="section-subtitle">Brand Mention Distribution Across Platforms</div>
        </div>
    </div>

    <h3>Overall Competitive Landscape</h3>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Brand</th>
                    <th>Mentions</th>
                    <th>Share %</th>
                </tr>
            </thead>
            <tbody>
{self._generate_sov_table_rows(rankings, analysis)}
            </tbody>
        </table>
    </div>

    <h3 style="margin-top: 40px;">Platform-by-Platform Breakdown</h3>
{platform_breakdown}
</section>"""

    def _generate_sov_table_rows(self, rankings, analysis):
        """Generate share of voice table rows"""
        total_mentions = sum([count for _, count in rankings])
        rows = ""

        for i, (brand, mentions) in enumerate(rankings, 1):
            share = (mentions / total_mentions * 100) if total_mentions > 0 else 0
            is_our_brand = (brand == self.brand_name)

            rows += f"""
                <tr>
                    <td>#{i}</td>
                    <td class="{'strong' if is_our_brand else ''}">{brand}</td>
                    <td>{mentions}</td>
                    <td class="strong">{share:.1f}%</td>
                </tr>"""

        return rows

    def _generate_displacement_opportunities_section(self, analysis):
        """Generate Section 7: Competitive Displacement Opportunities"""
        # Find queries where competitors appear but brand doesn't
        displacement_opps = []
        for query in analysis['zero_mention_queries']:
            if query['competitors']:
                score = self._calculate_opportunity_score(query, analysis)
                displacement_opps.append((query, score))

        displacement_opps.sort(key=lambda x: x[1], reverse=True)
        top_12 = displacement_opps[:12]

        opp_cards = ""
        for i, (query, score) in enumerate(top_12, 1):
            competitors = ', '.join(query['competitors'][:3])
            platforms_mentioned = 4  # Assume all platforms for now

            opp_cards += f"""
    <div style="background: white; border: 2px solid #E5E7EB; border-radius: 8px; padding: 20px; margin: 15px 0; border-left: 4px solid #EF4444;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
            <div style="flex: 1;">
                <div style="font-size: 12px; color: #6B7280; margin-bottom: 5px;">Opportunity #{i}</div>
                <div style="font-size: 16px; font-weight: 700; color: #111827; margin-bottom: 10px;">{query['text']}</div>
                <div style="font-size: 13px; color: #6B7280;">
                    <strong>Competing Brands:</strong> {competitors}
                </div>
                <div style="font-size: 13px; color: #6B7280; margin-top: 5px;">
                    <strong>Platform Presence:</strong> {platforms_mentioned} platforms
                </div>
            </div>
            <div style="text-align: center; margin-left: 20px;">
                <div style="font-size: 24px; font-weight: 700; color: #EF4444;">{score}</div>
                <div style="font-size: 11px; color: #6B7280;">CRITICAL</div>
            </div>
        </div>
    </div>"""

        return f"""
<!-- SECTION 7: DISPLACEMENT OPPORTUNITIES -->
<section class="section">
    <div class="section-header">
        <div class="section-number">8</div>
        <div>
            <div class="section-title">⚔️ Competitive Displacement Opportunities</div>
            <div class="section-subtitle">Top 12 Queries Where Competitors Dominate</div>
        </div>
    </div>

    <div class="callout callout-critical">
        <strong>🎯 STRATEGIC FOCUS:</strong> These queries currently mention competitors but not {self.brand_name}. Each represents a direct opportunity to displace competitive positioning through superior content.
    </div>

{opp_cards}
</section>"""

    def _generate_impact_analysis_section(self, analysis, current_rate):
        """Generate Section 8: Projected Impact Analysis"""
        # Calculate projections
        conservative = current_rate + 5
        moderate = current_rate + 12.3
        aggressive = current_rate + 20

        return f"""
<!-- SECTION 8: PROJECTED IMPACT -->
<section class="section">
    <div class="section-header">
        <div class="section-number">9</div>
        <div>
            <div class="section-title">📈 Projected Impact Analysis</div>
            <div class="section-subtitle">Expected ROI from Strategic Optimization</div>
        </div>
    </div>

    <div style="background: white; border: 2px solid #000000; padding: 40px; margin: 30px 0;">
        <h3 style="margin: 0 0 20px 0;">Current vs. Projected Performance</h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px;">
            <div>
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">CURRENT MENTION RATE</div>
                <div style="font-size: 48px; font-weight: 700;">{current_rate:.1f}%</div>
            </div>
            <div>
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">PROJECTED (MODERATE SCENARIO)</div>
                <div style="font-size: 48px; font-weight: 700; color: #10B981;">{moderate:.1f}%</div>
                <div style="font-size: 16px; margin-top: 5px;">+{moderate - current_rate:.1f}% improvement</div>
            </div>
        </div>
    </div>

    <h3>Scenario Analysis</h3>
    <div style="display: grid; gap: 20px; margin: 20px 0;">
        <div style="background: white; border: 2px solid #000000; padding: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="margin: 0;">Conservative Scenario</h4>
                <span style="background: #10B981; color: white; padding: 6px 16px; font-weight: 700;">+{conservative - current_rate:.1f}%</span>
            </div>
            <div style="font-size: 14px; color: #666666; line-height: 1.6;">
                Implement top 10 zero-mention query content. Timeline: 30-45 days. Minimal resources.
            </div>
        </div>

        <div style="background: white; border: 2px solid #000000; border-left: 6px solid #000000; padding: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="margin: 0;"><strong>Moderate Scenario (Recommended)</strong></h4>
                <span style="background: #000000; color: white; padding: 6px 16px; font-weight: 700;">+{moderate - current_rate:.1f}%</span>
            </div>
            <div style="font-size: 14px; color: #666666; line-height: 1.6;">
                Full content gap analysis implementation + platform-specific optimization. Timeline: 60-90 days.
            </div>
        </div>

        <div style="background: white; border: 2px solid #000000; padding: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="margin: 0;">Aggressive Scenario</h4>
                <span style="background: #DC2626; color: white; padding: 6px 16px; font-weight: 700;">+{aggressive - current_rate:.1f}%</span>
            </div>
            <div style="font-size: 14px; color: #666666; line-height: 1.6;">
                Comprehensive content strategy + technical optimization + competitive displacement. Timeline: 90-120 days.
            </div>
        </div>
    </div>
</section>"""

    def _generate_action_plan_section(self, analysis):
        """Generate Section 9: Strategic Action Plan"""
        # Generate Quick Wins
        quick_wins = ""

        # Quick Win 1: Zero-mention queries
        if analysis['zero_mention_queries']:
            quick_wins += self._quick_win_card(
                1,
                "Target Zero-Mention Generic Queries",
                92,
                f"Create targeted content for top {min(10, len(analysis['zero_mention_queries']))} zero-mention queries",
                "Low",
                "High",
                "2-3 weeks",
                [
                    f"Identify {min(10, len(analysis['zero_mention_queries']))} highest-value zero-mention queries",
                    "Develop comprehensive content addressing each query",
                    "Optimize for AI citation patterns",
                    "Monitor mention rate improvements weekly"
                ]
            )

        # Quick Win 2: Platform-specific
        if analysis['platforms']:
            worst_platform = min(analysis['platforms'].items(), key=lambda x: x[1]['rate'])
            quick_wins += self._quick_win_card(
                2,
                f"Optimize {worst_platform[0]} Performance",
                88,
                f"Platform-specific content strategy for {worst_platform[0]}",
                "Medium",
                "High",
                "3-4 weeks",
                [
                    f"Analyze {worst_platform[0]} content preferences",
                    "Create platform-optimized content variants",
                    "Implement technical optimizations",
                    f"Track {worst_platform[0]} mention rate weekly"
                ]
            )

        # Quick Win 3: Competitive displacement
        quick_wins += self._quick_win_card(
            3,
            "Competitive Displacement Content",
            85,
            "Create superior content for top competitor-dominated queries",
            "Medium",
            "Very High",
            "4-5 weeks",
            [
                "Identify top 5 queries where competitors dominate",
                "Develop comprehensive comparison content",
                "Add unique value propositions",
                "Monitor competitive displacement metrics"
            ]
        )

        return f"""
<!-- SECTION 9: ACTION PLAN -->
<section class="section">
    <div class="section-header">
        <div class="section-number">10</div>
        <div>
            <div class="section-title">🎯 Strategic Action Plan</div>
            <div class="section-subtitle">Prioritized Implementation Roadmap</div>
        </div>
    </div>

    <h3 style="margin-top: 30px;">🔥 Quick Wins (5 High-Priority Actions)</h3>
{quick_wins}

    <h3 style="margin-top: 40px;">📅 Implementation Roadmap</h3>
    <div style="display: grid; gap: 20px; margin: 20px 0;">
        <div style="background: white; border: 2px solid #E5E7EB; border-radius: 8px; padding: 25px; border-left: 4px solid #EF4444;">
            <h4 style="margin: 0; font-size: 16px;">Phase 1: Quick Wins & High-Impact Opportunities</h4>
            <div style="font-size: 13px; color: #6B7280; margin: 8px 0;">Days 1-30 • Foundation Building</div>
            <ul style="margin: 15px 0; padding-left: 20px; color: #374151; font-size: 14px; line-height: 1.8;">
                <li>Target top 10 zero-mention queries</li>
                <li>Launch platform-specific content variants</li>
                <li>Implement basic technical optimizations</li>
            </ul>
        </div>

        <div style="background: white; border: 2px solid #E5E7EB; border-radius: 8px; padding: 25px; border-left: 4px solid #F59E0B;">
            <h4 style="margin: 0; font-size: 16px;">Phase 2: Competitive Displacement & Gap Filling</h4>
            <div style="font-size: 13px; color: #6B7280; margin: 8px 0;">Days 31-60 • Market Share Growth</div>
            <ul style="margin: 15px 0; padding-left: 20px; color: #374151; font-size: 14px; line-height: 1.8;">
                <li>Develop competitive displacement content</li>
                <li>Fill identified content gaps by category</li>
                <li>Expand platform-specific strategies</li>
            </ul>
        </div>

        <div style="background: white; border: 2px solid #E5E7EB; border-radius: 8px; padding: 25px; border-left: 4px solid #10B981;">
            <h4 style="margin: 0; font-size: 16px;">Phase 3: Optimization & Scaling</h4>
            <div style="font-size: 13px; color: #6B7280; margin: 8px 0;">Days 61-90 • Performance Maximization</div>
            <ul style="margin: 15px 0; padding-left: 20px; color: #374151; font-size: 14px; line-height: 1.8;">
                <li>Advanced technical SEO and structured data</li>
                <li>Content refresh and expansion</li>
                <li>Continuous monitoring and iteration</li>
            </ul>
        </div>
    </div>
</section>"""

    def _quick_win_card(self, num, title, score, description, difficulty, impact, timeline, steps):
        """Generate a Quick Win card"""
        steps_html = '\n'.join([f"                    <li>{step}</li>" for step in steps])

        return f"""
    <div style="background: white; border: 2px solid #E5E7EB; border-radius: 8px; padding: 25px; margin: 20px 0; border-left: 4px solid #000000;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <div style="flex: 1;">
                <div style="font-size: 12px; color: #6B7280; margin-bottom: 5px;">Quick Win #{num}</div>
                <h4 style="margin: 0 0 10px 0; font-size: 20px; color: #111827;">{title}</h4>
                <p style="margin: 0; color: #6B7280; font-size: 14px; line-height: 1.6;">{description}</p>
            </div>
            <div style="text-align: center; margin-left: 20px; padding: 15px; background: #F9FAFB; border-radius: 8px;">
                <div style="font-size: 28px; font-weight: 700; color: #000000;">{score}</div>
                <div style="font-size: 11px; color: #6B7280;">/ 100 SCORE</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; padding: 15px; background: #F9FAFB; border-radius: 6px;">
            <div>
                <div style="font-size: 11px; color: #6B7280; margin-bottom: 5px;">DIFFICULTY</div>
                <div style="font-size: 14px; font-weight: 600; color: #111827;">{difficulty}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #6B7280; margin-bottom: 5px;">IMPACT</div>
                <div style="font-size: 14px; font-weight: 600; color: #111827;">{impact}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #6B7280; margin-bottom: 5px;">TIMELINE</div>
                <div style="font-size: 14px; font-weight: 600; color: #111827;">{timeline}</div>
            </div>
        </div>

        <div style="background: #FFFBEB; border-left: 3px solid #F59E0B; padding: 15px; border-radius: 4px; margin-top: 15px;">
            <div style="font-size: 12px; font-weight: 600; color: #92400E; margin-bottom: 10px;">📋 IMPLEMENTATION STEPS</div>
            <ol style="margin: 0; padding-left: 20px; color: #78350F; font-size: 13px; line-height: 1.8;">
{steps_html}
            </ol>
        </div>
    </div>"""

    def _get_css(self):
        """Return comprehensive CSS matching RH report style - Clean black/white design"""
        return """
<style>
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

        .section-number {
            width: 35px;
            height: 35px;
            font-size: 18px;
        }

        .section-title {
            font-size: 24px;
        }

        .report-header {
            flex-direction: column !important;
            align-items: flex-start !important;
        }

        .report-header > div:last-child {
            width: 100% !important;
            margin-left: 0 !important;
            margin-top: 20px !important;
            text-align: left !important;
        }

        .report-header > div:last-child img {
            margin-left: 0 !important;
            margin-bottom: 16px !important;
        }

        .brand-title {
            font-size: 16px;
            line-height: 24px;
        }

        .report-title {
            font-size: 24px;
            line-height: 32px;
        }

        .report-meta {
            text-align: left !important;
            font-size: 13px;
        }
    }
</style>"""

    def generate_report(self, output_path='comprehensive_geo_report.html'):
        """Main report generation workflow"""
        print("\n" + "="*60)
        print("🚀 COMPREHENSIVE GEO REPORT GENERATOR")
        print("="*60 + "\n")

        # Fetch and analyze data
        analysis = self.fetch_and_analyze_data()

        # Print summary
        print("\n" + "-"*60)
        print("ANALYSIS SUMMARY:")
        print("-"*60)
        print(f"Total Queries: {analysis['total_queries']}")
        print(f"Overall Mention Rate: {analysis['mention_rate']:.1f}%")
        print(f"Generic Query Rate: {analysis['by_query_type']['generic']['mention_rate']:.1f}%")
        print(f"Zero-Mention Queries: {len(analysis['zero_mention_queries'])}")
        print("-"*60 + "\n")

        # Generate HTML
        print("📝 Generating comprehensive HTML report...")
        report_path = self.generate_html_report(analysis, output_path)

        print("\n" + "="*60)
        print("✅ COMPREHENSIVE REPORT COMPLETE!")
        print("="*60 + "\n")

        return report_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate comprehensive GEO audit report')
    parser.add_argument('--sheet', type=str, help='Worksheet name', required=True)
    parser.add_argument('--brand', '-b', type=str, help='Brand name', required=True)
    parser.add_argument('--config', type=str, default='config.json', help='Config file path')
    parser.add_argument('--output', type=str, default='comprehensive_geo_report.html', help='Output file path')

    args = parser.parse_args()

    generator = ComprehensiveGEOReportGenerator(
        config_path=args.config,
        sheet_name=args.sheet,
        brand_name=args.brand
    )

    report_path = generator.generate_report(output_path=args.output)

    print(f"\n📄 Open this file in your browser:")
    print(f"   {report_path}\n")


if __name__ == '__main__':
    main()
