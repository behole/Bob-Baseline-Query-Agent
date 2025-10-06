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


class BOBReportGenerator:
    """Generate SEMrush-style reports from tracking data"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize with config"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Setup Google Sheets
        self.setup_google_sheets()
        
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
        self.sheet = self.gc.open_by_key(self.config['spreadsheet_id']).sheet1
        
    def fetch_data(self):
        """Fetch all data from Google Sheet"""
        print("📊 Fetching data from Google Sheets...")
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
            'queries_with_bob': set(),
            'queries_without_bob': set(),
            'platform_performance': {}
        }
        
        # Track unique queries
        unique_queries = set()
        
        for row in data:
            query_num = row.get('Query #', 0)
            platform = row.get('Platform', '')
            bob_mentioned = row.get('BOB Mentioned?', 'No')
            position = row.get('Position', 'N/A')
            competitors = row.get('Competitors Mentioned', '')
            sources = row.get('Sources Cited', '')
            query_text = row.get('Query Text', '')
            
            # Count queries
            unique_queries.add(query_num)
            
            # Count by platform
            if platform:
                analysis['by_platform'][platform] += 1
            
            # BOB mentions
            if bob_mentioned == 'Yes' or bob_mentioned == 'Direct':
                analysis['bob_mentions']['total'] += 1
                analysis['bob_mentions']['by_platform'][platform] += 1
                analysis['bob_mentions']['direct'] += 1
                analysis['queries_with_bob'].add(query_text)
            elif bob_mentioned == 'Indirect':
                analysis['bob_mentions']['indirect'] += 1
                analysis['queries_with_bob'].add(query_text)
            elif bob_mentioned == 'Inaccurate':
                analysis['bob_mentions']['inaccurate'] += 1
            else:
                analysis['bob_mentions']['none'] += 1
                analysis['queries_without_bob'].add(query_text)
            
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
            
            # Sources
            if sources and sources != 'None':
                for source in sources.split(','):
                    source = source.strip()
                    if source:
                        analysis['sources_cited'][source] += 1
        
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
        
        return analysis
    
    def generate_html_report(self, analysis, data, output_path='bob_report.html'):
        """Generate a professional HTML report"""
        print("\n📝 Generating HTML report...")
        
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
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brush On Block - AI Visibility Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .header .date {{
            margin-top: 10px;
            opacity: 0.8;
            font-size: 0.9em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        
        .metric-card.positive {{
            border-left-color: #10b981;
        }}
        
        .metric-card.negative {{
            border-left-color: #ef4444;
        }}
        
        .metric-card.neutral {{
            border-left-color: #f59e0b;
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .metric-card.positive .metric-value {{
            color: #10b981;
        }}
        
        .metric-card.negative .metric-value {{
            color: #ef4444;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .platform-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .platform-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }}
        
        .platform-name {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .platform-stat {{
            font-size: 0.9em;
            color: #666;
            margin: 5px 0;
        }}
        
        .list-item {{
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
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
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .alert {{
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .alert-info {{
            background: #dbeafe;
            border-left: 4px solid #3b82f6;
            color: #1e40af;
        }}
        
        .alert-warning {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            color: #92400e;
        }}
        
        .alert-success {{
            background: #d1fae5;
            border-left: 4px solid #10b981;
            color: #065f46;
        }}
        
        .query-list {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
        }}
        
        .query-item {{
            padding: 10px;
            border-left: 3px solid #667eea;
            margin: 10px 0;
            background: white;
            padding-left: 15px;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
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
            <h2>✅ Queries Where BOB Is Mentioned</h2>
            <p style="color: #666; margin-bottom: 15px;">
                {len(analysis['queries_with_bob'])} queries successfully triggered BOB mentions:
            </p>
            <div class="query-list">
"""
        
        for query in sorted(analysis['queries_with_bob'])[:15]:
            html += f'                <div class="query-item">{query}</div>\n'
        
        if len(analysis['queries_with_bob']) > 15:
            html += f'                <div style="text-align: center; padding: 10px; color: #666;">...and {len(analysis['queries_with_bob']) - 15} more</div>\n'
        
        html += f"""
            </div>
        </div>
        
        <div class="section">
            <h2>❌ Queries Where BOB Is NOT Mentioned</h2>
            <p style="color: #666; margin-bottom: 15px;">
                {len(analysis['queries_without_bob'])} queries did not mention BOB - optimization opportunities:
            </p>
            <div class="query-list">
"""
        
        for query in sorted(analysis['queries_without_bob'])[:15]:
            html += f'                <div class="query-item">{query}</div>\n'
        
        if len(analysis['queries_without_bob']) > 15:
            html += f'                <div style="text-align: center; padding: 10px; color: #666;">...and {len(analysis['queries_without_bob']) - 15} more</div>\n'
        
        html += """
            </div>
        </div>
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            <div style="line-height: 2;">
"""
        
        # Dynamic recommendations based on data
        if mention_rate < 20:
            html += """
                <p><strong>1. Increase Content Marketing:</strong> Create more high-quality content targeting the queries where BOB is not mentioned.</p>
                <p><strong>2. Optimize Website SEO:</strong> Ensure brushonblock.com ranks well for target keywords.</p>
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
    
    def generate_report(self, output_format='html'):
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
            report_path = self.generate_html_report(analysis, data)
            return report_path
        
        return analysis


def main():
    """Main entry point"""
    generator = BOBReportGenerator('config.json')
    report_path = generator.generate_report(output_format='html')
    
    print("\n" + "="*60)
    print(f"✅ REPORT COMPLETE!")
    print("="*60)
    print(f"\n📄 Open this file in your browser:\n   {report_path}\n")


if __name__ == '__main__':
    main()
