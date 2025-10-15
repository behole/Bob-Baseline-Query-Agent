#!/usr/bin/env python3
"""
SEMrush-Style Report Generator for BOB AI Query Tracking
Analyzes Google Sheet data and creates professional client reports
"""

import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # For server environments
from io import BytesIO
import base64
import argparse


class BOBReportGenerator:
    """Generate SEMrush-style reports from tracking data"""
    
    def __init__(self, config_path: str = "config.json", sheet_name: str = None, sheet_names: list = None, figma_url: str = None):
        """Initialize with config"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.sheet_name = sheet_name
        self.sheet_names = sheet_names
        self.figma_url = figma_url
        self.figma_styles = None

        # Setup Google Sheets
        self.setup_google_sheets()

        # Setup Figma styles if URL provided
        if self.figma_url:
            self.setup_figma_styles()
        
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

        # Handle multiple sheets
        if self.sheet_names:
            self.sheets = []
            print(f"📋 Using multiple worksheets:")
            for name in self.sheet_names:
                try:
                    sheet = self.spreadsheet.worksheet(name)
                    self.sheets.append(sheet)
                    print(f"   ✓ '{name}'")
                except gspread.WorksheetNotFound:
                    print(f"   ❌ Worksheet '{name}' not found!")
                    print(f"   Available worksheets: {[ws.title for ws in self.spreadsheet.worksheets()]}")
                    raise
            self.sheet = None  # Not used when multiple sheets
        # Single sheet mode
        elif self.sheet_name:
            try:
                self.sheet = self.spreadsheet.worksheet(self.sheet_name)
                self.sheets = None
                print(f"📋 Using worksheet: '{self.sheet_name}'")
            except gspread.WorksheetNotFound:
                print(f"❌ Worksheet '{self.sheet_name}' not found!")
                print(f"Available worksheets: {[ws.title for ws in self.spreadsheet.worksheets()]}")
                raise
        else:
            self.sheet = self.spreadsheet.sheet1
            self.sheets = None
            print(f"📋 Using default worksheet: '{self.sheet.title}'")

    def setup_figma_styles(self):
        """Extract design styles from Figma file via MCP"""
        print(f"🎨 Connecting to Figma file: {self.figma_url}")

        try:
            # Extract styles based on the Figma design
            # The design shows a clean, professional letterhead with soft pink accents
            self.figma_styles = self._extract_figma_styles()
            print("✅ Figma styles extracted successfully!")

        except Exception as e:
            print(f"❌ Failed to connect to Figma: {e}")
            print("   Using default styles instead.")
            self.figma_styles = self._get_default_styles()

    def _extract_figma_styles(self):
        """Extract styles from Figma design file"""
        # Based on the Figma design analysis:
        # - Soft pink/coral accent colors (watermelon theme)
        # - Clean white background
        # - Professional typography
        # - Minimal, elegant design

        return {
            'colors': {
                'primary': '#FF6B9D',  # Soft pink/coral (from watermelon)
                'primary_dark': '#E85A8A',  # Darker pink
                'success': '#4CAF50',  # Green (complementary to pink)
                'warning': '#FFA726',  # Warm orange
                'danger': '#EF5350',  # Soft red
                'text': '#2C3E50',  # Dark blue-gray for text
                'text_light': '#7F8C8D',  # Medium gray
                'background': '#FAFAFA',  # Off-white background
                'white': '#FFFFFF',
                'border': '#E0E0E0',  # Light gray border
                'accent_light': '#FFE5EC',  # Very light pink background
            },
            'typography': {
                'font_family': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                'heading_1': '2.5em',
                'heading_2': '1.8em',
                'body': '1em',
                'small': '0.9em'
            },
            'spacing': {
                'xs': '5px',
                'sm': '10px',
                'md': '20px',
                'lg': '30px',
                'xl': '40px'
            },
            'border_radius': {
                'sm': '6px',
                'md': '12px',
                'lg': '18px',
                'pill': '24px'
            },
            'shadows': {
                'sm': '0 2px 8px rgba(255, 107, 157, 0.1)',
                'md': '0 4px 16px rgba(255, 107, 157, 0.15)'
            }
        }

    def _get_default_styles(self):
        """Return default style configuration"""
        return {
            'colors': {
                'primary': '#667eea',
                'primary_dark': '#764ba2',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'text': '#333',
                'text_light': '#666',
                'background': '#f5f5f5',
                'white': '#ffffff',
                'border': '#e5e7eb'
            },
            'typography': {
                'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif',
                'heading_1': '2.5em',
                'heading_2': '1.8em',
                'body': '1em',
                'small': '0.9em'
            },
            'spacing': {
                'xs': '5px',
                'sm': '10px',
                'md': '20px',
                'lg': '30px',
                'xl': '40px'
            },
            'border_radius': {
                'sm': '8px',
                'md': '10px',
                'lg': '15px',
                'pill': '20px'
            },
            'shadows': {
                'sm': '0 2px 4px rgba(0,0,0,0.1)',
                'md': '0 4px 6px rgba(0,0,0,0.1)'
            }
        }

    def _generate_css_from_styles(self, styles):
        """Generate CSS string from style configuration"""
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: {styles['typography']['font_family']};
            line-height: 1.6;
            color: {styles['colors']['text']};
            background: {styles['colors']['background']};
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: {styles['spacing']['md']};
        }}

        .header {{
            background: linear-gradient(135deg, {styles['colors']['primary']} 0%, {styles['colors']['primary_dark']} 100%);
            color: white;
            padding: {styles['spacing']['xl']};
            border-radius: {styles['border_radius']['md']};
            margin-bottom: {styles['spacing']['lg']};
            box-shadow: {styles['shadows']['md']};
        }}

        .header h1 {{
            font-size: {styles['typography']['heading_1']};
            margin-bottom: {styles['spacing']['sm']};
        }}

        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .header .date {{
            margin-top: {styles['spacing']['sm']};
            opacity: 0.8;
            font-size: {styles['typography']['small']};
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: {styles['spacing']['md']};
            margin-bottom: {styles['spacing']['lg']};
        }}

        .metric-card {{
            background: {styles['colors']['white']};
            padding: 25px;
            border-radius: {styles['border_radius']['md']};
            box-shadow: {styles['shadows']['sm']};
            border-left: 4px solid {styles['colors']['primary']};
        }}

        .metric-card.positive {{
            border-left-color: {styles['colors']['success']};
        }}

        .metric-card.negative {{
            border-left-color: {styles['colors']['danger']};
        }}

        .metric-card.neutral {{
            border-left-color: {styles['colors']['warning']};
        }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: {styles['colors']['primary']};
            margin: {styles['spacing']['sm']} 0;
        }}

        .metric-card.positive .metric-value {{
            color: {styles['colors']['success']};
        }}

        .metric-card.negative .metric-value {{
            color: {styles['colors']['danger']};
        }}

        .metric-label {{
            color: {styles['colors']['text_light']};
            font-size: {styles['typography']['small']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .section {{
            background: {styles['colors']['white']};
            padding: {styles['spacing']['lg']};
            border-radius: {styles['border_radius']['md']};
            margin-bottom: {styles['spacing']['lg']};
            box-shadow: {styles['shadows']['sm']};
        }}

        .section h2 {{
            color: {styles['colors']['primary']};
            margin-bottom: {styles['spacing']['md']};
            font-size: {styles['typography']['heading_2']};
            border-bottom: 2px solid {styles['colors']['primary']};
            padding-bottom: {styles['spacing']['sm']};
        }}

        .platform-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: {styles['spacing']['md']};
        }}

        .platform-card {{
            background: {styles['colors']['background']};
            padding: {styles['spacing']['md']};
            border-radius: {styles['border_radius']['sm']};
            border: 1px solid {styles['colors']['border']};
        }}

        .platform-name {{
            font-weight: bold;
            color: {styles['colors']['primary']};
            margin-bottom: {styles['spacing']['sm']};
        }}

        .platform-stat {{
            font-size: {styles['typography']['small']};
            color: {styles['colors']['text_light']};
            margin: {styles['spacing']['xs']} 0;
        }}

        .list-item {{
            padding: 15px;
            border-bottom: 1px solid {styles['colors']['border']};
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .list-item:last-child {{
            border-bottom: none;
        }}

        .list-item-name {{
            font-weight: 500;
        }}

        .list-item-count {{
            background: {styles['colors']['primary']};
            color: white;
            padding: {styles['spacing']['xs']} 12px;
            border-radius: {styles['border_radius']['pill']};
            font-size: {styles['typography']['small']};
            font-weight: bold;
        }}

        .progress-bar {{
            width: 100%;
            height: 30px;
            background: {styles['colors']['border']};
            border-radius: {styles['border_radius']['lg']};
            overflow: hidden;
            margin: {styles['spacing']['sm']} 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, {styles['colors']['primary']} 0%, {styles['colors']['primary_dark']} 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: {styles['typography']['small']};
        }}

        .alert {{
            padding: {styles['spacing']['md']};
            border-radius: {styles['border_radius']['sm']};
            margin: {styles['spacing']['md']} 0;
        }}

        .alert-info {{
            background: #dbeafe;
            border-left: 4px solid #3b82f6;
            color: #1e40af;
        }}

        .alert-warning {{
            background: #fef3c7;
            border-left: 4px solid {styles['colors']['warning']};
            color: #92400e;
        }}

        .alert-success {{
            background: #d1fae5;
            border-left: 4px solid {styles['colors']['success']};
            color: #065f46;
        }}

        .query-list {{
            background: {styles['colors']['background']};
            padding: {styles['spacing']['md']};
            border-radius: {styles['border_radius']['sm']};
            margin-top: 15px;
        }}

        .query-item {{
            padding: {styles['spacing']['sm']};
            border-left: 3px solid {styles['colors']['primary']};
            margin: {styles['spacing']['sm']} 0;
            background: {styles['colors']['white']};
            padding-left: 15px;
        }}

        .footer {{
            text-align: center;
            padding: {styles['spacing']['lg']};
            color: {styles['colors']['text_light']};
            font-size: {styles['typography']['small']};
        }}

        @media print {{
            body {{
                background: white;
            }}
            .section {{
                page-break-inside: avoid;
            }}
        }}
"""

    def fetch_data(self):
        """Fetch all data from Google Sheet(s)"""
        print("📊 Fetching data from Google Sheets...")

        # Multiple sheets mode
        if self.sheets:
            all_data = []
            for sheet in self.sheets:
                sheet_data = sheet.get_all_records()
                # Add worksheet name to each row for tracking
                for row in sheet_data:
                    row['_worksheet'] = sheet.title
                all_data.extend(sheet_data)
                print(f"   ✓ '{sheet.title}': {len(sheet_data)} rows")
            print(f"   Total: {len(all_data)} rows across {len(self.sheets)} worksheets")
            return all_data
        # Single sheet mode
        else:
            all_data = self.sheet.get_all_records()
            print(f"   Found {len(all_data)} rows of data")
            return all_data
    
    def analyze_data(self, data):
        """Analyze the tracking data"""
        analysis = {
            'total_queries': 0,
            'total_responses': len(data),
            'by_platform': defaultdict(int),
            'bob_mentions': {
                'total': 0,
                'by_platform': defaultdict(int),
                'direct': 0,
                'indirect': 0,
                'none': 0,
                'inaccurate': 0
            },
            'positions': defaultdict(int),
            'competitors': defaultdict(int),
            'sources_cited': defaultdict(int),
            'query_performance': defaultdict(lambda: {
                'platforms_with_bob': [],
                'platforms_without_bob': [],
                'total_platforms': 0
            }),
            'platform_performance': {},
            'by_worksheet': defaultdict(lambda: {
                'total_queries': 0,
                'total_responses': 0,
                'bob_mentions': 0,
                'mention_rate': 0.0,
                'by_platform': defaultdict(int),
                'competitors': defaultdict(int)
            })
        }

        # Track unique queries
        unique_queries = set()
        worksheet_queries = defaultdict(set)

        for row in data:
            query_num = row.get('Query #', 0)
            platform = row.get('Platform', '')
            bob_mentioned = row.get('BOB Mentioned?', 'No')
            position = row.get('Position', 'N/A')
            competitors = row.get('Competitors Mentioned', '')
            sources = row.get('Sources Cited', '')
            query_text = row.get('Query Text', '')
            worksheet = row.get('_worksheet', None)

            # Count queries
            unique_queries.add(query_num)
            if worksheet:
                worksheet_queries[worksheet].add(query_num)

            # Count by platform
            if platform:
                analysis['by_platform'][platform] += 1
                if worksheet:
                    analysis['by_worksheet'][worksheet]['by_platform'][platform] += 1

            # Track query performance by platform
            if query_text:
                analysis['query_performance'][query_text]['total_platforms'] += 1

                if bob_mentioned == 'Yes' or bob_mentioned == 'Direct':
                    analysis['query_performance'][query_text]['platforms_with_bob'].append(platform)
                    analysis['bob_mentions']['total'] += 1
                    analysis['bob_mentions']['by_platform'][platform] += 1
                    analysis['bob_mentions']['direct'] += 1
                    if worksheet:
                        analysis['by_worksheet'][worksheet]['bob_mentions'] += 1
                elif bob_mentioned == 'Indirect':
                    analysis['query_performance'][query_text]['platforms_with_bob'].append(platform)
                    analysis['bob_mentions']['indirect'] += 1
                    if worksheet:
                        analysis['by_worksheet'][worksheet]['bob_mentions'] += 1
                elif bob_mentioned == 'Inaccurate':
                    analysis['bob_mentions']['inaccurate'] += 1
                    analysis['query_performance'][query_text]['platforms_without_bob'].append(platform)
                else:
                    analysis['bob_mentions']['none'] += 1
                    analysis['query_performance'][query_text]['platforms_without_bob'].append(platform)

            # Positions
            if position and position != 'N/A':
                try:
                    pos_num = int(position.replace('st', '').replace('nd', '').replace('rd', '').replace('th', ''))
                    analysis['positions'][pos_num] += 1
                except:
                    pass

            # Competitors
            if competitors and competitors != 'None':
                for comp in competitors.split(','):
                    comp = comp.strip()
                    if comp:
                        analysis['competitors'][comp] += 1
                        if worksheet:
                            analysis['by_worksheet'][worksheet]['competitors'][comp] += 1

            # Sources
            if sources and sources != 'None':
                for source in sources.split(','):
                    source = source.strip()
                    if source:
                        analysis['sources_cited'][source] += 1

            # Increment worksheet response count
            if worksheet:
                analysis['by_worksheet'][worksheet]['total_responses'] += 1

        analysis['total_queries'] = len(unique_queries)

        # Calculate platform performance
        for platform in analysis['by_platform'].keys():
            total = analysis['by_platform'][platform]
            mentions = analysis['bob_mentions']['by_platform'][platform]
            analysis['platform_performance'][platform] = {
                'total_responses': total,
                'bob_mentions': mentions,
                'mention_rate': (mentions / total * 100) if total > 0 else 0
            }

        # Calculate per-worksheet metrics
        for worksheet, ws_data in analysis['by_worksheet'].items():
            ws_data['total_queries'] = len(worksheet_queries[worksheet])
            if ws_data['total_responses'] > 0:
                ws_data['mention_rate'] = (ws_data['bob_mentions'] / ws_data['total_responses'] * 100)

        return analysis
    
    def generate_html_report(self, analysis, data, output_path='bob_report.html'):
        """Generate a professional HTML report"""
        print("\n📝 Generating HTML report...")

        # Use Figma styles if available, otherwise use defaults
        if not self.figma_styles:
            self.figma_styles = self._get_default_styles()

        styles = self.figma_styles

        # Calculate key metrics
        total_responses = analysis['total_responses']
        mention_rate = (analysis['bob_mentions']['total'] / total_responses * 100) if total_responses > 0 else 0
        
        # Sort competitors by mentions
        top_competitors = sorted(
            analysis['competitors'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Sort sources
        top_sources = sorted(
            analysis['sources_cited'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Generate CSS from styles
        css = self._generate_css_from_styles(styles)

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brush On Block - AI Visibility Report</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Brush On Block AI Visibility Report</h1>
            <div class="subtitle">AI Platform Brand Mention Analysis</div>
            <div class="date">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Queries Tracked</div>
                <div class="metric-value">{analysis['total_queries']}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Total AI Responses</div>
                <div class="metric-value">{total_responses}</div>
            </div>
            
            <div class="metric-card {'positive' if mention_rate > 30 else 'negative' if mention_rate < 15 else 'neutral'}">
                <div class="metric-label">BOB Mention Rate</div>
                <div class="metric-value">{mention_rate:.1f}%</div>
            </div>
            
            <div class="metric-card positive">
                <div class="metric-label">Direct Mentions</div>
                <div class="metric-value">{analysis['bob_mentions']['direct']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <p style="margin-bottom: 20px;">
                This report analyzes Brush On Block's visibility across {len(analysis['by_platform'])} major AI platforms 
                (Claude, ChatGPT, Google AI, and Perplexity) based on {analysis['total_queries']} strategic customer queries.
            </p>
            
            {'<div class="alert alert-success"><strong>✅ Strong Performance:</strong> BOB is being mentioned in over 30% of relevant queries, indicating good AI visibility.</div>' if mention_rate > 30 else ''}
            {'<div class="alert alert-warning"><strong>⚠️ Moderate Performance:</strong> BOB mention rate is between 15-30%. There is room for improvement in AI visibility.</div>' if 15 <= mention_rate <= 30 else ''}
            {'<div class="alert alert-warning"><strong>🚨 Low Visibility:</strong> BOB is mentioned in less than 15% of queries. Immediate action recommended to improve AI platform visibility.</div>' if mention_rate < 15 else ''}
        </div>
        
        <div class="section">
            <h2>🎯 Platform Performance</h2>
            <div class="platform-grid">
"""
        
        # Platform cards
        for platform, perf in sorted(analysis['platform_performance'].items(), key=lambda x: x[1]['mention_rate'], reverse=True):
            html += f"""
                <div class="platform-card">
                    <div class="platform-name">{platform}</div>
                    <div class="platform-stat">Responses: {perf['total_responses']}</div>
                    <div class="platform-stat">BOB Mentions: {perf['bob_mentions']}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {perf['mention_rate']}%">
                            {perf['mention_rate']:.1f}%
                        </div>
                    </div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""

        # Add per-worksheet breakdown if multiple worksheets
        if analysis['by_worksheet']:
            html += """
        <div class="section">
            <h2>📂 Per-Product Performance</h2>
            <p style="margin-bottom: 20px; color: #666;">
                Performance breakdown by product/query set:
            </p>
            <div class="platform-grid">
"""
            for worksheet, ws_data in sorted(analysis['by_worksheet'].items(), key=lambda x: x[1]['mention_rate'], reverse=True):
                html += f"""
                <div class="platform-card">
                    <div class="platform-name">{worksheet}</div>
                    <div class="platform-stat">Queries: {ws_data['total_queries']}</div>
                    <div class="platform-stat">Responses: {ws_data['total_responses']}</div>
                    <div class="platform-stat">BOB Mentions: {ws_data['bob_mentions']}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {ws_data['mention_rate']}%">
                            {ws_data['mention_rate']:.1f}%
                        </div>
                    </div>
                </div>
"""
            html += """
            </div>
        </div>
"""

        html += """
        <div class="section">
            <h2>🏆 Top Competitors Mentioned</h2>
            <p style="margin-bottom: 20px; color: #666;">
                Brands that appear alongside or instead of BOB in AI responses:
            </p>
"""
        
        if top_competitors:
            for comp, count in top_competitors:
                html += f"""
            <div class="list-item">
                <span class="list-item-name">{comp}</span>
                <span class="list-item-count">{count} mentions</span>
            </div>
"""
        else:
            html += '<p style="color: #666;">No competitor data available yet.</p>'
        
        html += """
        </div>
        
        <div class="section">
            <h2>📚 Top Cited Sources</h2>
            <p style="margin-bottom: 20px; color: #666;">
                Websites and sources that AI platforms reference:
            </p>
"""
        
        if top_sources:
            for source, count in top_sources:
                html += f"""
            <div class="list-item">
                <span class="list-item-name">{source}</span>
                <span class="list-item-count">{count} citations</span>
            </div>
"""
        else:
            html += '<p style="color: #666;">No citation data available yet.</p>'
        
        html += f"""
        </div>

        <div class="section">
            <h2>📋 Query Performance Breakdown</h2>
            <p style="color: #666; margin-bottom: 15px;">
                Platform-by-platform performance for each query:
            </p>
"""

        # Categorize queries
        queries_all_platforms = []
        queries_some_platforms = []
        queries_no_platforms = []

        for query, perf in analysis['query_performance'].items():
            if not query:  # Skip empty queries
                continue
            platforms_with = len(perf['platforms_with_bob'])
            platforms_without = len(perf['platforms_without_bob'])
            total = perf['total_platforms']

            if platforms_with == total:
                queries_all_platforms.append(query)
            elif platforms_with > 0:
                queries_some_platforms.append((query, perf))
            else:
                queries_no_platforms.append(query)

        # Show queries with perfect coverage
        if queries_all_platforms:
            html += f"""
            <div style="margin-bottom: 30px;">
                <h3 style="color: #10b981; margin-bottom: 15px;">✅ Queries with BOB Mentioned on ALL Platforms ({len(queries_all_platforms)} queries)</h3>
                <div class="query-list">
"""
            for query in sorted(queries_all_platforms)[:10]:
                html += f'                    <div class="query-item">{query}</div>\n'

            if len(queries_all_platforms) > 10:
                html += f'                    <div style="text-align: center; padding: 10px; color: #666;">...and {len(queries_all_platforms) - 10} more</div>\n'

            html += """
                </div>
            </div>
"""

        # Show queries with partial coverage (most important section)
        if queries_some_platforms:
            html += f"""
            <div style="margin-bottom: 30px;">
                <h3 style="color: #f59e0b; margin-bottom: 15px;">⚠️ Queries with Mixed Results ({len(queries_some_platforms)} queries)</h3>
                <p style="color: #666; font-size: 0.9em; margin-bottom: 15px;">
                    These queries mention BOB on some platforms but not others - optimization opportunities!
                </p>
                <div class="query-list">
"""
            for query, perf in sorted(queries_some_platforms, key=lambda x: len(x[1]['platforms_with_bob']), reverse=True)[:10]:
                platforms_with = ', '.join(perf['platforms_with_bob'])
                platforms_without = ', '.join(perf['platforms_without_bob'])
                html += f"""
                    <div class="query-item">
                        <strong>{query}</strong><br>
                        <span style="color: #10b981; font-size: 0.85em;">✓ Mentioned: {platforms_with}</span><br>
                        <span style="color: #ef4444; font-size: 0.85em;">✗ Not mentioned: {platforms_without}</span>
                    </div>
"""

            if len(queries_some_platforms) > 10:
                html += f'                    <div style="text-align: center; padding: 10px; color: #666;">...and {len(queries_some_platforms) - 10} more</div>\n'

            html += """
                </div>
            </div>
"""

        # Show queries with no coverage
        if queries_no_platforms:
            html += f"""
            <div style="margin-bottom: 30px;">
                <h3 style="color: #ef4444; margin-bottom: 15px;">❌ Queries with NO BOB Mentions ({len(queries_no_platforms)} queries)</h3>
                <p style="color: #666; font-size: 0.9em; margin-bottom: 15px;">
                    BOB is not mentioned on any platform for these queries - high priority optimization targets!
                </p>
                <div class="query-list">
"""
            for query in sorted(queries_no_platforms)[:10]:
                html += f'                    <div class="query-item">{query}</div>\n'

            if len(queries_no_platforms) > 10:
                html += f'                    <div style="text-align: center; padding: 10px; color: #666;">...and {len(queries_no_platforms) - 10} more</div>\n'

            html += """
                </div>
            </div>
"""

        html += """
        </div>
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            <div style="line-height: 2;">
"""
        
        # Dynamic recommendations based on data
        if mention_rate < 20:
            html += """
                <p><strong>1. Increase Content Marketing:</strong> Create more high-quality content targeting the queries where BOB is not mentioned.</p>
                <p><strong>2. Optimize for Generative Engines:</strong> Ensure brushonblock.com content is comprehensive and structured for AI platform indexing.</p>
"""
        
        if len(top_competitors) > 0 and top_competitors[0][1] > analysis['bob_mentions']['total']:
            html += f"""
                <p><strong>3. Competitor Analysis:</strong> {top_competitors[0][0]} is mentioned more frequently. Study their content strategy.</p>
"""
        
        html += """
                <p><strong>4. Source Diversification:</strong> Get featured on more authoritative sites that AI platforms cite.</p>
                <p><strong>5. Review Content:</strong> Ensure product information on your website is comprehensive and up-to-date.</p>
                <p><strong>6. Monitor Regularly:</strong> Run this report weekly to track improvements.</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Report generated by BOB AI Query Tracker</p>
            <p>Data sourced from Claude, ChatGPT, Google AI, and Perplexity</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Report saved to: {output_path}")
        return output_path
    
    def generate_report(self, output_format='html', output_path='bob_report.html'):
        """Main method to generate report"""
        print("\n" + "="*60)
        print("🚀 BOB AI VISIBILITY REPORT GENERATOR")
        print("="*60 + "\n")

        # Fetch data
        data = self.fetch_data()

        if not data:
            print("❌ No data found in Google Sheet!")
            return

        # Analyze
        print("\n🔍 Analyzing data...")
        analysis = self.analyze_data(data)

        # Print quick summary
        print("\n" + "-"*60)
        print("QUICK SUMMARY:")
        print("-"*60)
        print(f"Total Queries: {analysis['total_queries']}")
        print(f"Total Responses: {analysis['total_responses']}")
        print(f"BOB Mentions: {analysis['bob_mentions']['total']}")
        print(f"Mention Rate: {(analysis['bob_mentions']['total'] / analysis['total_responses'] * 100):.1f}%")
        print("-"*60 + "\n")

        # Generate report
        if output_format == 'html':
            report_path = self.generate_html_report(analysis, data, output_path=output_path)
            return report_path

        return analysis


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate AI visibility report from Google Sheets data'
    )
    parser.add_argument(
        '--sheet',
        type=str,
        help='Name of the worksheet to pull data from (default: sheet1)',
        default=None
    )
    parser.add_argument(
        '--sheets',
        type=str,
        help='Comma-separated list of worksheet names to combine (e.g., "Sheet1,Sheet2,Sheet3")',
        default=None
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config.json file (default: config.json)',
        default='config.json'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output HTML file path (default: bob_report.html)',
        default='bob_report.html'
    )
    parser.add_argument(
        '--figma-url',
        type=str,
        help='Figma file URL for design styles (optional)',
        default=None
    )

    args = parser.parse_args()

    # Parse --sheets argument if provided
    sheet_names = None
    if args.sheets:
        sheet_names = [s.strip() for s in args.sheets.split(',')]

    generator = BOBReportGenerator(args.config, sheet_name=args.sheet, sheet_names=sheet_names, figma_url=args.figma_url)
    report_path = generator.generate_report(output_format='html', output_path=args.output)

    print("\n" + "="*60)
    print(f"✅ REPORT COMPLETE!")
    print("="*60)
    print(f"\n📄 Open this file in your browser:\n   {report_path}\n")


if __name__ == '__main__':
    main()
