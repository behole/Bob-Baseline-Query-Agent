# GEO Audit V2 - Automated Competitor Discovery & Gap Analysis

## Overview

Version 2 introduces **fully automated competitor discovery and intelligent gap analysis** to eliminate manual competitor identification and provide actionable, priority-based recommendations.

## Key Improvements Over V1

### V1 Limitations
- Manual competitor lists required
- Pre-written competitor comparison queries needed
- No automated gap identification
- Mixed branded/generic metrics caused skew
- No prioritized action plans

### V2 Features
- **Automated Competitor Discovery**: System identifies competitors from generic query responses
- **Intelligent Ranking**: Top 7 competitors ranked by competitiveness score
- **Gap Analysis**: Automatically identifies where competitors outperform
- **Theme Clustering**: Groups gaps by category (soccer, sustainability, etc.)
- **Priority Recommendations**: AI-generated action plans with impact estimates
- **Clean Metrics**: Separate branded/generic/competitor metrics prevent skew

## Architecture

```
V2 System Flow:
┌─────────────────────────────────────────┐
│ INPUT: Brand + Industry                 │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Query Generation (existing)              │
│ - 30% Branded queries                    │
│ - 70% Generic queries                    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Query Execution (existing)               │
│ - Run through AI platforms               │
│ - Collect responses                      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ COMPETITOR DISCOVERY (NEW)               │
│ geo_audit/v2/discovery/                  │
│ - Extract brand mentions from responses  │
│ - Rank by competitiveness                │
│ - Return top 7 competitors               │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ GAP ANALYSIS (NEW)                       │
│ geo_audit/v2/analysis/gap_analysis.py    │
│ - Compare brand vs each competitor       │
│ - Identify queries where competitor wins │
│ - Cluster gaps by theme                  │
│ - Prioritize top gaps                    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ RECOMMENDATIONS (NEW)                    │
│ geo_audit/v2/analysis/recommendations.py │
│ - Generate high-level actions            │
│ - Estimate impact (HIGH/MEDIUM/LOW)      │
│ - Prioritize by importance               │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ REPORT GENERATION (UPDATED)              │
│ geo_audit/v2/reporting/                  │
│ - Executive summary                      │
│ - Market discovery section               │
│ - Gap analysis per competitor            │
│ - Prioritized action plan                │
└─────────────────────────────────────────┘
```

## Module Structure

```
geo_audit/v2/
├── __init__.py
├── discovery/
│   ├── __init__.py
│   └── competitor_discovery.py    # Automated competitor identification
├── analysis/
│   ├── __init__.py
│   ├── gap_analysis.py            # Gap identification & clustering
│   └── recommendations.py         # Action plan generation
└── reporting/
    ├── __init__.py
    └── report_generator.py        # V2 report generation
```

## Core Classes

### CompetitorDiscovery
**Location**: `geo_audit/v2/discovery/competitor_discovery.py`

Automatically discovers competitors from generic query results using hybrid approach:
1. Industry seed list for validation (from existing `competitors.py`)
2. Pattern-based brand extraction from AI responses
3. Competitive ranking algorithm

**Key Method**:
```python
discover_from_results(query_results, max_competitors=7) -> List[CompetitorMetrics]
```

**Returns**: Top 7 competitors with metrics:
- Mention rate (%)
- Average ranking position
- Detail score
- Competitiveness score

### GapAnalyzer
**Location**: `geo_audit/v2/analysis/gap_analysis.py`

Identifies specific queries where competitors outperform the target brand.

**Key Method**:
```python
identify_gaps(query_results, competitor_name, max_priority_gaps=3) -> List[GapCluster]
```

**Returns**: Priority gap clusters with:
- Theme (soccer, sustainability, etc.)
- Affected queries
- Average gap size
- Priority score

### RecommendationEngine
**Location**: `geo_audit/v2/analysis/recommendations.py`

Generates actionable recommendations with impact estimates.

**Key Method**:
```python
generate_recommendations(gap_clusters, target_brand) -> List[Recommendation]
```

**Returns**: Prioritized recommendations with:
- High-level actions (4 per gap)
- Impact level (HIGH/MEDIUM/LOW)
- Potential improvement (%)
- Difficulty estimate

## Competitive Ranking Algorithm

```python
Competitiveness Score =
    (Mention Rate × 40%) +
    (1 / Avg Ranking × 30%) +
    (Detail Score × 20%) +
    (Sentiment × 10%)
```

- **Mention Rate**: How often brand appears in generic queries (0-100%)
- **Avg Ranking**: Average position in responses (1-10, lower is better)
- **Detail Score**: Amount of detail/attention brand receives (0-10)
- **Sentiment**: Positive/negative tone (0-10, currently neutral=5)

## Gap Prioritization Algorithm

```python
Priority Score =
    (Query Count × 10, max 40) +
    (Avg Gap Size × 5, max 30) +
    (Strategic Importance × 3, max 30)
```

- **Query Count**: Number of affected queries
- **Gap Size**: Ranking difference (competitor rank - target rank)
- **Strategic Importance**: Category significance (1-10 scale)

## Usage Example

```python
from geo_audit.v2 import CompetitorDiscovery, GapAnalyzer, RecommendationEngine

# 1. Discover competitors from generic query results
discovery = CompetitorDiscovery(target_brand="Nike", industry="athletic_wear")
competitors = discovery.discover_from_results(
    query_results=generic_results,
    max_competitors=7
)

# 2. Analyze gaps for each competitor
analyzer = GapAnalyzer(target_brand="Nike")
all_gaps = []

for competitor in competitors:
    gaps = analyzer.identify_gaps(
        query_results=all_results,
        competitor_name=competitor.brand_name,
        max_priority_gaps=3
    )
    all_gaps.extend(gaps)

# 3. Generate recommendations
rec_engine = RecommendationEngine()
recommendations = rec_engine.generate_recommendations(
    gap_clusters=all_gaps,
    target_brand="Nike"
)

# 4. Format action plan
action_plan = rec_engine.format_action_plan(recommendations, format_type='html')
```

## Integration with Existing System

V2 modules integrate seamlessly with V1:

**Reuses:**
- `geo_audit/utils/query_generator.py` - Query generation
- `geo_audit/utils/competitors.py` - Industry seed lists
- `geo_audit/core/tracker.py` - Query execution
- `geo_audit/platforms/` - AI platform integrations

**Extends:**
- Adds automated discovery layer
- Adds gap analysis layer
- Adds recommendation layer
- Updates report generation

**No Breaking Changes**: V1 functionality remains intact

## Next Steps

1. ✅ Create v2 modules (COMPLETE)
2. ⏳ Create v2 report generator
3. ⏳ Create CLI wrapper for v2
4. ⏳ Test with Nike dataset
5. ⏳ Validate vs Adidas comparison
6. ⏳ Full documentation
7. ⏳ Migration guide for existing clients

## Benefits

### For Nike Analysis
- Automatically discovers Adidas, Brooks, New Balance, etc.
- Identifies specific soccer/sustainability/trail gaps
- Provides actionable, prioritized recommendations
- No manual competitor list needed
- No skewed metrics from branded queries

### For Any Brand
- Just provide: Brand name + Industry
- System handles everything else
- Get comprehensive, accurate competitive analysis
- Clear action plan with impact estimates
- Scales to any industry

## Future Enhancements

- Sentiment analysis integration
- Trend detection over time
- Category-specific weighting
- Custom theme definitions
- Multi-language support
- Integration with BI dashboards
