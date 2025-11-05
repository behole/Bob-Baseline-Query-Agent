# Query Generator - AI-Powered Query Creation

The GEO Audit Platform now includes an AI-powered query generator that creates comprehensive, natural-language queries for brand visibility testing.

## Overview

Instead of manually writing queries, the generator uses Claude AI to create:
- **Generic queries** - Non-branded questions people actually search
- **Branded queries** - Questions mentioning your brand specifically
- **Competitor queries** - Direct comparisons with competitors
- **Product queries** - Product-specific questions
- **How-to queries** - Instructional and informational questions

## Quick Start

### 1. Initialize Your Client
```bash
./geo-audit init pottery_barn --industry furniture --brand "Pottery Barn"
```

### 2. Generate Queries
```bash
./geo-audit generate \
  --client pottery_barn \
  --output pottery_barn_queries.json \
  --count 50 \
  --products "outdoor furniture" \
  --products "dining tables" \
  --products "sofas"
```

### 3. Run Tracking
```bash
./geo-audit track \
  --client pottery_barn \
  --queries pottery_barn_queries.json \
  --worksheet "PotteryBarn_Audit_Nov_2025"
```

## Command Options

```bash
./geo-audit generate [OPTIONS]

Options:
  -c, --client TEXT    Client name (required)
  -o, --output TEXT    Output JSON file path (required)
  -n, --count INTEGER  Total number of queries (default: 50)
  -p, --products TEXT  Product categories (can specify multiple)
  --config TEXT        Config file for API keys (default: config.json)
```

## Examples

### Furniture Brand (50 queries)
```bash
./geo-audit generate \
  --client restoration_hardware \
  --output rh_queries.json \
  --count 50 \
  --products "outdoor furniture" \
  --products "dining tables" \
  --products "sofas" \
  --products "bedroom furniture"
```

### Sunscreen Brand (60 queries)
```bash
./geo-audit generate \
  --client brush_on_block \
  --output bob_queries.json \
  --count 60 \
  --products "powder sunscreen" \
  --products "mineral sunscreen" \
  --products "face sunscreen" \
  --products "body sunscreen"
```

### Skincare Brand (40 queries)
```bash
./geo-audit generate \
  --client skincare_brand \
  --output skincare_queries.json \
  --count 40 \
  --products "anti-aging serums" \
  --products "moisturizers" \
  --products "cleansers"
```

## Query Distribution

The generator automatically distributes queries across types:

| Type | Percentage | Purpose |
|------|------------|---------|
| Generic | 45% | Organic visibility (most important) |
| Branded | 20% | Brand awareness/reputation |
| Competitor | 15% | Competitive positioning |
| Product | 10% | Product-specific visibility |
| How-to | 10% | Informational queries |

**Example for 50 queries:**
- 22 generic queries
- 10 branded queries
- 8 competitor queries
- 5 product queries
- 5 how-to queries

## Query Quality

The AI generates **natural, conversational queries** that match real search patterns:

### ✅ Good Examples (AI-Generated)
```
what's the best outdoor furniture for coastal climates
how to choose a sofa that lasts
where to buy quality leather furniture
does restoration hardware furniture last
restoration hardware vs pottery barn quality
```

### ❌ Bad Examples (Avoid)
```
[brand] + sunscreen
best sunscreen 2024
click here to buy sunscreen
```

## Customization

### Client Configuration

Edit `config/clients/<client_name>.yaml` before generating:

```yaml
brand_name: "Your Brand"
industry: "furniture"  # or "sunscreen", "skincare", "general"

keywords:
  - "your brand"
  - "yourbrand"
  - "yb"

competitors:
  - "Competitor 1"
  - "Competitor 2"
  - "Competitor 3"
```

The generator will:
- Use your brand keywords in branded queries
- Create comparisons with your competitors
- Generate industry-appropriate questions

### Multiple Products

You can specify as many product categories as needed:

```bash
./geo-audit generate \
  --client my_brand \
  --output queries.json \
  --products "category 1" \
  --products "category 2" \
  --products "category 3" \
  --products "category 4"
```

## How It Works

1. **Loads Client Config**: Gets brand name, industry, competitors from YAML
2. **Calculates Distribution**: Determines how many queries of each type
3. **Generates via AI**: Uses Claude to create natural, conversational queries
4. **Saves to JSON**: Outputs standard format ready for tracking

## Tips for Best Results

### 1. Be Specific with Products
```bash
# Better
--products "outdoor sectional sofas" \
--products "teak dining tables"

# Less specific
--products "furniture" \
--products "home goods"
```

### 2. Add Competitors to Client Config

```yaml
competitors:
  - "Top Competitor 1"
  - "Top Competitor 2"
  - "Top Competitor 3"
```

More competitors = better competitive analysis.

### 3. Adjust Query Count by Use Case

- **Quick test**: 20-30 queries
- **Standard audit**: 50-60 queries
- **Comprehensive audit**: 80-100 queries

### 4. Review Before Running

Always review generated queries before running tracking:

```bash
cat pottery_barn_queries.json | head -20
```

You can manually edit the JSON if needed.

## Integration with Workflow

The query generator fits into your complete workflow:

```bash
# 1. Initialize client
./geo-audit init <client>

# 2. Generate queries
./geo-audit generate --client <client> --output queries.json

# 3. Run tracking
./geo-audit track --client <client> --queries queries.json --worksheet "Audit"

# 4. Generate report
python3 generate_advanced_report.py --sheet "Audit" --brand "<Brand>" --output report.html
```

## API Key Requirements

The query generator requires an Anthropic API key in `config.json`:

```json
{
  "anthropic_api_key": "sk-ant-...",
  ...
}
```

Each query generation run costs approximately:
- **Small (20-30 queries)**: ~$0.05-0.10
- **Standard (50-60 queries)**: ~$0.15-0.25
- **Large (80-100 queries)**: ~$0.30-0.50

## Troubleshooting

### "Client config not found"
```bash
./geo-audit init <client> --industry <industry>
```

### "Anthropic API key not found"
Add to `config.json`:
```json
{
  "anthropic_api_key": "sk-ant-your-key-here"
}
```

### "Generated fewer queries than requested"
Normal! If you request 50 but have 0 competitors, competitor queries are skipped. The final count will be ~40-45.

### Generated queries don't match your brand
Edit `config/clients/<client>.yaml` and add:
- More specific `keywords`
- More relevant `competitors`
- Better product categories via `--products`

## Advanced Usage

### Programmatic Usage

You can also use the QueryGenerator class directly in Python:

```python
from geo_audit.utils.query_generator import QueryGenerator

generator = QueryGenerator(api_key="sk-ant-...")

queries = generator.generate_queries(
    brand_name="Pottery Barn",
    industry="furniture",
    product_categories=["sofas", "dining tables"],
    competitors=["West Elm", "Crate & Barrel"],
    total_queries=50
)

generator.save_to_file(queries, "my_queries.json")
```

### Custom Query Types

To generate only specific types:

```python
queries = generator.generate_queries(
    brand_name="My Brand",
    industry="furniture",
    product_categories=["products"],
    competitors=[],
    total_queries=30,
    include_types=['generic', 'how-to']  # Only these types
)
```

## Future Enhancements

Planned features:
- [ ] Long-tail query generation
- [ ] Seasonal query variations
- [ ] Regional/localized queries
- [ ] Voice search optimization
- [ ] Question-based queries (FAQ style)
- [ ] Multiple language support

## Examples in Repo

Check these files for examples:
- `queries.json` - Brush On Block queries (manual)
- `restoration_hardware_queries.json` - RH queries (manual)
- `lip_oil_spf_queries.json` - Product-specific queries

The generator produces similar quality automatically!
