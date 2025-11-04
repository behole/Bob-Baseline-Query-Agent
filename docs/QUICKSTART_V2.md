# GEO Audit Platform v2.0 - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements-new.txt
```

### 2. Test Connections

```bash
./geo-audit test --legacy-config config.json
```

You should see all platforms and storage marked with ✅

### 3. Initialize a Client

```bash
./geo-audit init restoration_hardware --industry furniture --brand "Restoration Hardware"
```

This creates `config/clients/restoration_hardware.yaml`

### 4. Run Tracking

```bash
./geo-audit track \
  --client restoration_hardware \
  --queries restoration_hardware_queries.json \
  --worksheet "RH_Audit_Nov_2025"
```

### 5. View Results

Open your Google Sheet - results are saved in the worksheet!

## Command Reference

### Test Connections
```bash
./geo-audit test
```

### Initialize New Client
```bash
./geo-audit init <client_name> --industry <industry> --brand "Brand Name"
```

### Run Tracking
```bash
./geo-audit track \
  --client <client_name> \
  --queries <path_to_queries.json> \
  --worksheet "Worksheet_Name"
```

### Get Help
```bash
./geo-audit --help
./geo-audit track --help
```

## Query File Format

```json
[
  {
    "num": 1,
    "text": "what's the best outdoor furniture",
    "platforms": ["Claude", "ChatGPT", "Google AI", "Perplexity"]
  }
]
```

## Client Config Format

`config/clients/brand_name.yaml`:

```yaml
brand_name: "Your Brand"
industry: "furniture"

keywords:
  - "your brand"
  - "yourbrand"

competitors:
  - "Competitor 1"
  - "Competitor 2"

settings:
  screenshot_dir: "screenshots/brand_name"
```

## Platform Config Format

`config/platforms.yaml`:

```yaml
platforms:
  Claude:
    api_key: "sk-ant-..."
    model: "claude-sonnet-4-20250514"

  ChatGPT:
    api_key: "sk-..."
    model: "gpt-4o"

  Google AI:
    api_key: "..."
    model: "gemini-2.0-flash-exp"

  Perplexity:
    api_key: "..."
    model: "sonar-pro"

storage:
  credentials_path: "config/google-credentials.json"
  spreadsheet_id: "your-sheet-id"
```

## Legacy Scripts Still Work!

The old scripts are fully functional:

```bash
# Old way
python3 ai_query_tracker.py -q queries.json -r "Worksheet" --brand "Brand"

# New way (same result)
./geo-audit track --client brand --queries queries.json --worksheet "Worksheet"
```

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements-new.txt
```

### "Permission denied: ./geo-audit"
```bash
chmod +x geo-audit
```

### "Config file not found"
```bash
# Use legacy config
./geo-audit test --legacy-config config.json
```

## What's Next?

1. **Customize client configs**: Edit `config/clients/*.yaml`
2. **Add more queries**: Create new JSON query files
3. **Generate reports**: `python3 generate_advanced_report.py` (CLI integration coming soon)
4. **Explore the code**: Check out `geo_audit/` package

## Get Help

- Architecture docs: `docs/ARCHITECTURE.md`
- Legacy migration: `legacy/README.md`
- Full README: `README.md`
