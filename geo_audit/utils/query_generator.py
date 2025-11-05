"""
AI-Powered Query Generator for GEO Audits

Generates comprehensive query sets for brand visibility testing across:
- Generic (non-branded) queries
- Branded queries
- Competitor comparison queries
- Product-specific queries
- How-to/informational queries
"""

import json
from typing import List, Dict, Any, Optional
import anthropic


class QueryGenerator:
    """Generate queries for GEO audit tracking"""

    def __init__(self, api_key: str):
        """
        Initialize query generator

        Args:
            api_key: Anthropic API key for Claude
        """
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_queries(
        self,
        brand_name: str,
        industry: str,
        product_categories: List[str],
        competitors: List[str],
        total_queries: int = 50,
        include_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate comprehensive query set for a brand

        Args:
            brand_name: Brand to generate queries for
            industry: Industry (e.g., "furniture", "sunscreen", "skincare")
            product_categories: List of product types (e.g., ["outdoor furniture", "dining tables"])
            competitors: List of competitor brands
            total_queries: Total number of queries to generate
            include_types: Query types to include (defaults to all)

        Returns:
            List of query dictionaries
        """
        if include_types is None:
            include_types = ['generic', 'branded', 'competitor', 'product', 'how-to']

        # Calculate distribution
        distribution = self._calculate_distribution(total_queries, include_types)

        all_queries = []
        query_num = 1

        # Generate each type
        if 'generic' in include_types and distribution['generic'] > 0:
            print(f"🔍 Generating {distribution['generic']} generic queries...")
            generic = self._generate_generic_queries(
                industry=industry,
                product_categories=product_categories,
                count=distribution['generic']
            )
            for q in generic:
                all_queries.append({
                    'num': query_num,
                    'text': q,
                    'platforms': ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']
                })
                query_num += 1

        if 'branded' in include_types and distribution['branded'] > 0:
            print(f"🎯 Generating {distribution['branded']} branded queries...")
            branded = self._generate_branded_queries(
                brand_name=brand_name,
                product_categories=product_categories,
                count=distribution['branded']
            )
            for q in branded:
                all_queries.append({
                    'num': query_num,
                    'text': q,
                    'platforms': ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']
                })
                query_num += 1

        if 'competitor' in include_types and distribution['competitor'] > 0 and len(competitors) > 0:
            print(f"⚔️ Generating {distribution['competitor']} competitor queries...")
            competitor = self._generate_competitor_queries(
                brand_name=brand_name,
                competitors=competitors[:5],  # Top 5 competitors
                count=distribution['competitor']
            )
            for q in competitor:
                all_queries.append({
                    'num': query_num,
                    'text': q,
                    'platforms': ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']
                })
                query_num += 1

        if 'product' in include_types and distribution['product'] > 0:
            print(f"📦 Generating {distribution['product']} product-specific queries...")
            product = self._generate_product_queries(
                brand_name=brand_name,
                product_categories=product_categories,
                count=distribution['product']
            )
            for q in product:
                all_queries.append({
                    'num': query_num,
                    'text': q,
                    'platforms': ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']
                })
                query_num += 1

        if 'how-to' in include_types and distribution['how-to'] > 0:
            print(f"💡 Generating {distribution['how-to']} how-to queries...")
            howto = self._generate_howto_queries(
                industry=industry,
                product_categories=product_categories,
                count=distribution['how-to']
            )
            for q in howto:
                all_queries.append({
                    'num': query_num,
                    'text': q,
                    'platforms': ['Claude', 'ChatGPT', 'Google AI', 'Perplexity']
                })
                query_num += 1

        print(f"\n✅ Generated {len(all_queries)} total queries")
        return all_queries

    def _calculate_distribution(self, total: int, types: List[str]) -> Dict[str, int]:
        """Calculate query distribution across types"""
        # Default distribution percentages
        percentages = {
            'generic': 0.45,      # 45% generic (most important for organic visibility)
            'branded': 0.20,      # 20% branded
            'competitor': 0.15,   # 15% competitor comparisons
            'product': 0.10,      # 10% product-specific
            'how-to': 0.10        # 10% how-to/informational
        }

        # Filter to only included types
        active_percentages = {k: v for k, v in percentages.items() if k in types}

        # Normalize to sum to 1.0
        total_pct = sum(active_percentages.values())
        normalized = {k: v/total_pct for k, v in active_percentages.items()}

        # Calculate counts
        distribution = {}
        remaining = total
        for qtype, pct in normalized.items():
            if qtype == types[-1]:  # Last type gets remaining
                distribution[qtype] = remaining
            else:
                count = int(total * pct)
                distribution[qtype] = count
                remaining -= count

        return distribution

    def _generate_generic_queries(
        self,
        industry: str,
        product_categories: List[str],
        count: int
    ) -> List[str]:
        """Generate generic (non-branded) queries"""
        prompt = f"""Generate {count} natural, conversational search queries for the {industry} industry. These should be generic questions people would ask without mentioning any specific brand.

Product categories to focus on: {', '.join(product_categories)}

Requirements:
- NO brand names mentioned
- Natural language (how people actually search)
- Mix of:
  - "what's the best..." queries
  - "where to buy..." queries
  - "how to choose..." queries
  - Problem-solving queries
  - Comparison queries (category-level, not brand)
- Lowercase, conversational tone
- No numbering, just the queries

Example format:
what's the best outdoor furniture for coastal climates
how to choose a durable sofa that lasts
where to buy quality leather furniture

Now generate {count} queries:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        queries = response.content[0].text.strip().split('\n')
        queries = [q.strip() for q in queries if q.strip()]
        return queries[:count]

    def _generate_branded_queries(
        self,
        brand_name: str,
        product_categories: List[str],
        count: int
    ) -> List[str]:
        """Generate branded queries (mention the brand)"""
        prompt = f"""Generate {count} natural search queries that specifically mention "{brand_name}".

Product categories: {', '.join(product_categories)}

Requirements:
- Every query must include "{brand_name}" or common abbreviation
- Mix of:
  - "Does {brand_name}..." verification queries
  - "Is {brand_name}..." evaluation queries
  - "How to use {brand_name}..." instructional queries
  - "{brand_name} vs..." comparison starters
  - Product-specific questions
- Natural, conversational language
- Lowercase
- No numbering

Example format:
does restoration hardware furniture last
is restoration hardware worth the price
how to care for restoration hardware leather sofas

Now generate {count} queries for {brand_name}:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        queries = response.content[0].text.strip().split('\n')
        queries = [q.strip() for q in queries if q.strip()]
        return queries[:count]

    def _generate_competitor_queries(
        self,
        brand_name: str,
        competitors: List[str],
        count: int
    ) -> List[str]:
        """Generate competitor comparison queries"""
        if not competitors:
            return []

        competitor_list = ', '.join(competitors)
        prompt = f"""Generate {count} comparison queries between "{brand_name}" and its competitors: {competitor_list}.

Requirements:
- Each query should compare {brand_name} to one competitor
- Mix of direct comparisons: "{brand_name} vs {competitors[0] if competitors else 'competitors'}"
- Some should be evaluation: "is {brand_name} better than {competitors[0] if competitors else 'competitors'}"
- Some price comparisons
- Some quality/feature comparisons
- Natural, conversational language
- Lowercase
- No numbering

Example format:
restoration hardware vs pottery barn quality
is restoration hardware better than west elm
restoration hardware vs arhaus pricing

Now generate {count} queries:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        queries = response.content[0].text.strip().split('\n')
        queries = [q.strip() for q in queries if q.strip()]
        return queries[:count]

    def _generate_product_queries(
        self,
        brand_name: str,
        product_categories: List[str],
        count: int
    ) -> List[str]:
        """Generate product-specific queries"""
        prompt = f"""Generate {count} product-specific queries for "{brand_name}".

Product categories: {', '.join(product_categories)}

Requirements:
- Ask about specific products or product lines
- Mix of:
  - Availability questions
  - Price questions
  - Feature questions
  - Use case questions
- Natural language
- Lowercase
- No numbering

Example format:
where to buy restoration hardware cloud sofa
how much is restoration hardware dining table
does restoration hardware have outdoor furniture

Now generate {count} queries:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        queries = response.content[0].text.strip().split('\n')
        queries = [q.strip() for q in queries if q.strip()]
        return queries[:count]

    def _generate_howto_queries(
        self,
        industry: str,
        product_categories: List[str],
        count: int
    ) -> List[str]:
        """Generate how-to/informational queries"""
        prompt = f"""Generate {count} how-to and informational queries for the {industry} industry.

Product categories: {', '.join(product_categories)}

Requirements:
- All queries should start with "how to", "what is", "how do I", "best way to"
- Generic (no brand names)
- Educational/informational focus
- Mix of:
  - Design advice
  - Care/maintenance
  - Selection guidance
  - Style tips
- Natural language
- Lowercase
- No numbering

Example format:
how to arrange furniture in a large living room
what is the best way to clean leather furniture
how to create a cohesive interior design

Now generate {count} queries:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        queries = response.content[0].text.strip().split('\n')
        queries = [q.strip() for q in queries if q.strip()]
        return queries[:count]

    def save_to_file(self, queries: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save queries to JSON file

        Args:
            queries: List of query dictionaries
            output_path: Path to output JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(queries, f, indent=2)

        print(f"\n💾 Saved to: {output_path}")
