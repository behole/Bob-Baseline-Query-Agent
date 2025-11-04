# Legacy Scripts

This directory contains the original implementation scripts that have been refactored into the new `geo_audit` package.

## Original Files
- `ai_query_tracker.py` - Original monolithic tracker (now `geo_audit.core.tracker`)
- `generate_report.py` - Standard report generator
- `generate_advanced_report.py` - Advanced report with competitive analysis
- `quick_query.py` - Quick single-query testing tool

## Backward Compatibility

The old scripts still work! You can continue using them:

```bash
# Old way (still works)
python3 ai_query_tracker.py -q queries.json -r "Worksheet_Name" --brand "Brand Name"

# New way (recommended)
./geo-audit track --client brand_name --queries queries.json --worksheet "Worksheet_Name"
```

## Migration Guide

To migrate from legacy scripts to the new system:

1. **Create client config**: `./geo-audit init your_client --industry furniture --brand "Your Brand"`

2. **Convert platform config**: The new system uses `config/platforms.yaml` instead of `config.json`
   - Legacy `config.json` is still supported as fallback
   - New format separates platform configs from storage config

3. **Update commands**:
   - `python3 ai_query_tracker.py` → `./geo-audit track`
   - `python3 generate_advanced_report.py` → `./geo-audit report`
   - `python3 test_setup.py` → `./geo-audit test`

## Benefits of New System

- ✅ Plugin-based architecture (easy to add new platforms)
- ✅ Multi-client support (separate configs per brand)
- ✅ Better separation of concerns
- ✅ More testable
- ✅ API-ready architecture
- ✅ YAML configuration (easier to read/edit)
