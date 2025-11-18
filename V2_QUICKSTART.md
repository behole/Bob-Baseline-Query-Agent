# V2 GEO Audit - Quick Start Guide

## What is V2?

V2 is the **fully automated** GEO audit system that:
- Automatically discovers competitors from query results
- Identifies priority competitive gaps
- Generates actionable recommendations with impact estimates
- No manual competitor lists or comparison queries needed!

## Installation

```bash
# Clone/pull latest v2 branch
git checkout v2-automated-geo-audit

# Install requirements (if needed)
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Quick Start

### Option 1: Full Automated Audit (When Query Execution is Integrated)

```bash
python v2_audit.py \
    --brand "Nike" \
    --industry athletic_wear \
    --categories "running shoes,sneakers,athletic wear,basketball shoes"
```

This will:
1. Generate 60 queries (40 generic, 20 branded)
2. Execute queries (when integrated with tracker)
3. Discover top 7 competitors automatically
4. Identify priority gaps for each
5. Generate recommendations
6. Create HTML report

### Option 2: Two-Step Process (Current)

**Step 1: Generate Queries**
```bash
python v2_audit.py \
    --brand "Nike" \
    --industry athletic_wear \
    --categories "running shoes,sneakers,athletic wear"
```

This creates: `reports/nike_queries_v2.json`

**Step 2: Execute Queries**
```bash
# Use existing query execution system
# (Integration pending - use current ai_query_tracker.py)
```

**Step 3: Analyze & Report**
```bash
python v2_audit.py \
    --brand "Nike" \
    --industry athletic_wear \
    --categories "running shoes,sneakers" \
    --results path/to/query_results.json \
    --skip-generation
```

This creates: `reports/nike_v2_geo_report.html`

## CLI Options

```
Required:
  --brand BRAND          Brand name (e.g., "Nike", "Rivian")
  --industry INDUSTRY    Industry (athletic_wear, automotive, furniture, etc.)
  --categories CATS      Comma-separated categories

Optional:
  --queries N           Total queries to generate (default: 60)
  --competitors N       Max competitors to analyze (default: 7)
  --gaps N              Max gaps per competitor (default: 3)
  --results PATH        Path to query results JSON
  --output DIR          Output directory (default: reports/)
  --api-key KEY         Anthropic API key
  --skip-generation     Skip query generation (analysis only)
```

## Examples

### Nike (Athletic Wear)
```bash
python v2_audit.py \
    --brand "Nike" \
    --industry athletic_wear \
    --categories "running shoes,basketball shoes,soccer cleats,training gear"
```

### Rivian (Automotive)
```bash
python v2_audit.py \
    --brand "Rivian" \
    --industry automotive \
    --categories "electric vehicles,electric trucks,electric SUVs,adventure vehicles" \
    --queries 80 \
    --competitors 10
```

### Restoration Hardware (Furniture)
```bash
python v2_audit.py \
    --brand "Restoration Hardware" \
    --industry furniture \
    --categories "luxury furniture,outdoor furniture,modern furniture,home decor" \
    --output reports/rh
```

## Available Industries

- `athletic_wear` - Nike, Adidas, Under Armour, etc.
- `automotive` - Tesla, Rivian, Lucid, Ford, etc.
- `furniture` - RH, West Elm, Pottery Barn, etc.
- `sunscreen` - Supergoop, EltaMD, La Roche-Posay, etc.
- `skincare` - CeraVe, Cetaphil, The Ordinary, etc.
- `fashion` - Zara, H&M, Uniqlo, etc.
- `electronics` - Samsung, LG, Sony, etc.
- `travel` - Airbnb, Booking.com, Expedia, etc.
- `financial_services` - Chase, Bank of America, etc.

See `geo_audit/utils/competitors.py` for complete list.

## Expected Output

### Query Generation Output
```
reports/
├── nike_queries_v2.json          # Generated queries with categories
```

### Full Audit Output
```
reports/
├── nike_queries_v2.json           # Generated queries
└── nike_v2_geo_report.html        # Complete analysis report
```

## Report Sections

The V2 report includes:

1. **Executive Summary**
   - Market position (#1 or #2)
   - Top competitor and gap
   - High-priority gap count
   - Key findings

2. **Market Discovery**
   - Auto-discovered competitors (top 7)
   - Ranked by competitiveness score
   - Share of voice visualization

3. **Competitive Gap Analysis**
   - Priority gaps per competitor
   - Affected queries
   - Gap size and impact

4. **Prioritized Action Plan**
   - High-level recommendations
   - Impact estimates (HIGH/MEDIUM/LOW)
   - Difficulty ratings
   - Potential improvement percentages

## Query Results JSON Format

For `--results` parameter, provide JSON in this format:

```json
[
  {
    "query": "best running shoes",
    "category": "generic",
    "responses": {
      "Claude": "Nike offers excellent running shoes...",
      "ChatGPT": "Top options include Adidas, Brooks...",
      "Perplexity": "For running shoes, consider Nike, Hoka...",
      "Google AI": "Brooks and Nike are popular choices..."
    }
  },
  {
    "query": "Nike Air Max reviews",
    "category": "branded",
    "responses": {
      "Claude": "Nike Air Max shoes are...",
      ...
    }
  }
]
```

## Programmatic Usage

```python
from geo_audit.v2.orchestrator import run_v2_audit

results = run_v2_audit(
    brand_name="Nike",
    industry="athletic_wear",
    product_categories=["running shoes", "sneakers", "athletic wear"],
    anthropic_api_key="sk-ant-...",
    total_queries=60,
    max_competitors=7,
    max_gaps_per_competitor=3,
    query_results_path="path/to/results.json"  # Optional
)

print(f"Report: {results['report_path']}")
print(f"Top Competitor: {results['top_competitor']}")
print(f"Market Share: {results['market_share']:.1f}%")
```

## Key Differences from V1

| Feature | V1 | V2 |
|---------|----|----|
| Competitor Identification | Manual list | Auto-discovered |
| Competitor Queries | Manually written | Not needed |
| Competitor Ranking | Pre-defined | Auto-ranked by competitiveness |
| Gap Analysis | Manual review | Automated priority identification |
| Recommendations | None | AI-generated with impact estimates |
| Metric Skew | Branded queries inflate numbers | Separate branded/generic metrics |

## Next Steps

1. **Try with Nike**: Generate queries and see the v2 structure
2. **Integrate Query Execution**: Connect v2 to existing tracker
3. **Run Full Audit**: Execute queries and generate complete report
4. **Compare to V1**: See how automated discovery improves insights

## Troubleshooting

**"API key required"**
- Set `ANTHROPIC_API_KEY` environment variable
- Or use `--api-key` flag

**"Query execution requires integration"**
- V2 query generation works
- Query execution uses existing system (integration pending)
- Provide results with `--results` flag

**"Worksheet not found"**
- V2 uses standalone JSON files, not Google Sheets
- Migration to Sheets optional

## Support

- See `V2_ARCHITECTURE.md` for technical details
- Check `geo_audit/v2/` for module documentation
- Review examples in `examples/` directory
