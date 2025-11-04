"""
Core Tracker - Orchestrates queries across AI platforms
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..platforms import (
    PlatformClient,
    PlatformResponse,
    ClaudeClient,
    ChatGPTClient,
    GoogleAIClient,
    PerplexityClient
)
from ..storage import StorageBackend, GoogleSheetsBackend
from ..utils.brand_keywords import generate_brand_keywords, detect_brand_mention, extract_mention_context
from ..utils.competitors import get_competitors, detect_competitors_mentioned
from ..utils.screenshot import ScreenshotGenerator


class GEOTracker:
    """
    Main tracker orchestrator - coordinates queries across platforms,
    analyzes responses, and saves results to storage.
    """

    # Platform class registry
    PLATFORM_REGISTRY = {
        'Claude': ClaudeClient,
        'ChatGPT': ChatGPTClient,
        'Google AI': GoogleAIClient,
        'Perplexity': PerplexityClient,
    }

    def __init__(
        self,
        brand_name: str,
        platforms_config: Dict[str, Dict[str, Any]],
        storage_config: Dict[str, Any],
        industry: Optional[str] = None,
        screenshot_dir: str = "screenshots"
    ):
        """
        Initialize GEO Tracker

        Args:
            brand_name: Brand to track
            platforms_config: Platform configurations (API keys, models, etc.)
            storage_config: Storage backend configuration
            industry: Industry for competitor detection (auto-detected if None)
            screenshot_dir: Directory for screenshots
        """
        self.brand_name = brand_name
        self.brand_keywords = generate_brand_keywords(brand_name)
        self.competitors = get_competitors(brand_name, industry)

        # Initialize platforms
        self.platforms: Dict[str, PlatformClient] = {}
        self._initialize_platforms(platforms_config)

        # Initialize storage
        self.storage = GoogleSheetsBackend(storage_config)

        # Initialize screenshot generator
        self.screenshot_gen = ScreenshotGenerator(screenshot_dir)

        print(f"\n🎯 GEO Tracker initialized for: {brand_name}")
        print(f"📊 Active platforms: {', '.join(self.platforms.keys())}")
        print(f"🔍 Brand keywords: {', '.join(self.brand_keywords)}")
        print(f"🏢 Competitors: {len(self.competitors)} tracked")

    def _initialize_platforms(self, platforms_config: Dict[str, Dict[str, Any]]) -> None:
        """
        Initialize platform clients from configuration

        Args:
            platforms_config: Dict mapping platform names to their configs
        """
        for platform_name, config in platforms_config.items():
            if platform_name not in self.PLATFORM_REGISTRY:
                print(f"⚠️ Unknown platform: {platform_name}")
                continue

            try:
                client_class = self.PLATFORM_REGISTRY[platform_name]
                client = client_class(config)
                self.platforms[platform_name] = client
                print(f"  ✅ {platform_name} initialized")
            except Exception as e:
                print(f"  ❌ {platform_name} failed: {e}")

    def run_query(
        self,
        query_text: str,
        query_num: int,
        worksheet_name: str,
        platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Run a single query across specified platforms

        Args:
            query_text: The question to ask
            query_num: Query number for tracking
            worksheet_name: Worksheet to save results to
            platforms: List of platform names (uses all if None)

        Returns:
            List of result dictionaries
        """
        if platforms is None:
            platforms = list(self.platforms.keys())

        date_str = datetime.now().strftime("%Y-%m-%d")
        results = []

        print(f"\n🚀 Query #{query_num}: {query_text[:60]}...")

        for platform_name in platforms:
            if platform_name not in self.platforms:
                print(f"  ⚠️ {platform_name} not available")
                continue

            print(f"  🤖 Querying {platform_name}...")

            # Query the platform
            platform = self.platforms[platform_name]
            response = platform.query(query_text)

            # Analyze response
            analysis = self._analyze_response(response)

            # Generate screenshot
            screenshot_path = ""
            if response.success:
                try:
                    screenshot_path = self.screenshot_gen.generate(
                        query=query_text,
                        response=response.response_text,
                        platform=platform_name,
                        query_num=query_num,
                        date_str=date_str
                    )
                except Exception as e:
                    print(f"    ⚠️ Screenshot failed: {e}")

            # Build result
            result = {
                'Query #': query_num,
                'Query Text': query_text,
                'Platform': platform_name,
                'Test Date': date_str,
                f'{self.brand_name} Mentioned?': 'Yes' if analysis['brand_mentioned'] else 'No',
                'Mention Context': analysis['mention_context'],
                'Position': analysis['position'],
                'Competitors Mentioned': ', '.join(analysis['competitors']),
                'Sources Cited': analysis['sources_count'],
                'Accuracy': analysis['accuracy'],
                'Screenshot File': screenshot_path,
                'Notes': analysis['notes']
            }

            results.append(result)

            # Save to storage
            self.storage.write_row(worksheet_name, result)

            status = "✅" if response.success else "❌"
            mention = "🎯" if analysis['brand_mentioned'] else "❌"
            print(f"    {status} Response | {mention} Brand mention")

        return results

    def run_query_batch(
        self,
        queries: List[Dict[str, Any]],
        worksheet_name: str,
        create_worksheet: bool = True
    ) -> Dict[str, Any]:
        """
        Run multiple queries in batch

        Args:
            queries: List of query dicts with 'num', 'text', 'platforms'
            worksheet_name: Worksheet to save results to
            create_worksheet: Create worksheet if it doesn't exist

        Returns:
            Summary dictionary
        """
        # Create worksheet if needed
        if create_worksheet:
            headers = [
                'Query #',
                'Query Text',
                'Platform',
                'Test Date',
                f'{self.brand_name} Mentioned?',
                'Mention Context',
                'Position',
                'Competitors Mentioned',
                'Sources Cited',
                'Accuracy',
                'Screenshot File',
                'Notes'
            ]
            self.storage.create_worksheet(worksheet_name, headers)

        # Run all queries
        total_queries = len(queries)
        total_responses = 0
        brand_mentions = 0

        print(f"\n{'='*60}")
        print(f"🚀 BATCH RUN: {total_queries} queries")
        print(f"📊 Worksheet: {worksheet_name}")
        print(f"{'='*60}")

        for query in queries:
            results = self.run_query(
                query_text=query['text'],
                query_num=query['num'],
                worksheet_name=worksheet_name,
                platforms=query.get('platforms')
            )

            total_responses += len(results)
            brand_mentions += sum(1 for r in results if r[f'{self.brand_name} Mentioned?'] == 'Yes')

        # Summary
        mention_rate = (brand_mentions / total_responses * 100) if total_responses > 0 else 0

        summary = {
            'total_queries': total_queries,
            'total_responses': total_responses,
            'brand_mentions': brand_mentions,
            'mention_rate': mention_rate,
            'worksheet_name': worksheet_name
        }

        print(f"\n{'='*60}")
        print(f"✅ BATCH COMPLETE")
        print(f"{'='*60}")
        print(f"📊 Total Queries: {total_queries}")
        print(f"📝 Total Responses: {total_responses}")
        print(f"🎯 Brand Mentions: {brand_mentions} ({mention_rate:.1f}%)")
        print(f"{'='*60}\n")

        return summary

    def _analyze_response(self, response: PlatformResponse) -> Dict[str, Any]:
        """
        Analyze a platform response for brand mentions, competitors, etc.

        Args:
            response: PlatformResponse to analyze

        Returns:
            Analysis dictionary
        """
        if not response.success:
            return {
                'brand_mentioned': False,
                'mention_context': '',
                'position': '',
                'competitors': [],
                'sources_count': 0,
                'accuracy': '',
                'notes': f'Error: {response.error}'
            }

        # Brand mention detection
        brand_mentioned = detect_brand_mention(response.response_text, self.brand_keywords)
        mention_context = extract_mention_context(response.response_text, self.brand_keywords) if brand_mentioned else ''

        # Position detection (simple heuristic)
        position = ''
        if brand_mentioned:
            response_lower = response.response_text.lower()
            for i, keyword in enumerate(self.brand_keywords):
                pos = response_lower.find(keyword)
                if pos != -1:
                    # Estimate position based on character position
                    total_len = len(response.response_text)
                    if pos < total_len * 0.2:
                        position = 'Top'
                    elif pos < total_len * 0.5:
                        position = 'Middle'
                    else:
                        position = 'Bottom'
                    break

        # Competitor detection
        competitors = detect_competitors_mentioned(response.response_text, self.competitors)

        # Sources count (for Perplexity)
        sources_count = 0
        if response.platform_name == 'Perplexity':
            citations = response.raw_response.get('citations', [])
            sources_count = len(citations)

        # Notes
        notes = []
        if len(competitors) > 0:
            notes.append(f"Competitors mentioned: {', '.join(competitors)}")
        if sources_count > 0:
            notes.append(f"{sources_count} sources cited")

        return {
            'brand_mentioned': brand_mentioned,
            'mention_context': mention_context,
            'position': position,
            'competitors': competitors,
            'sources_count': sources_count,
            'accuracy': '',  # Can be filled in manually or with future analysis
            'notes': '; '.join(notes) if notes else ''
        }

    def test_connections(self) -> Dict[str, bool]:
        """
        Test all platform and storage connections

        Returns:
            Dict mapping service names to success status
        """
        print("\n🔍 Testing Connections...")
        results = {}

        # Test platforms
        for name, platform in self.platforms.items():
            print(f"  Testing {name}...", end=" ")
            success = platform.test_connection()
            results[name] = success
            print("✅" if success else "❌")

        # Test storage
        print(f"  Testing Storage...", end=" ")
        success = self.storage.test_connection()
        results['Storage'] = success
        print("✅" if success else "❌")

        return results
