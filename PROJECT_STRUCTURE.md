# Project Structure

```
ai-query-tracker/
│
├── ai_query_tracker.py      # Main application script
├── test_setup.py            # Setup verification and testing
├── quick_query.py           # Run single queries quickly
│
├── config.json              # API keys and configuration (YOU MUST EDIT)
├── queries.json             # Your query library (CUSTOMIZE THIS)
├── google-credentials.json  # Google service account key (YOU MUST ADD)
│
├── requirements.txt         # Python dependencies
├── README.md               # Full documentation
├── QUICKSTART.md           # Quick setup guide
├── .gitignore             # Git ignore rules
│
└── screenshots/            # Auto-generated screenshots
    ├── Q1_Claude_10-06-2025.png
    ├── Q1_ChatGPT_10-06-2025.png
    ├── Q1_Google_AI_10-06-2025.png
    └── Q1_Perplexity_10-06-2025.png
```

## File Descriptions

### Core Scripts

**`ai_query_tracker.py`** - Main application
- Queries all AI platforms
- Generates screenshots
- Logs to Google Sheets
- Analyzes responses for BOB mentions and competitors

**`test_setup.py`** - Verification tool
- Tests all API connections
- Verifies Google Sheets access
- Checks screenshot creation
- Run this first to ensure everything works

**`quick_query.py`** - Single query runner
- Test individual queries
- Faster than running full batch
- Good for testing new queries

### Configuration Files

**`config.json`** - Settings (⚠️ NEVER COMMIT TO GIT)
- API keys for all platforms
- Google credentials path
- Google Sheet ID

**`queries.json`** - Query library
- List of questions to track
- Query numbers (1-30)
- Platform selection per query
- Easy to add/remove queries

**`google-credentials.json`** - Google service account (⚠️ NEVER COMMIT TO GIT)
- Downloaded from Google Cloud Console
- Required for Google Sheets access
- Must be in project root directory

### Documentation

**`README.md`** - Complete guide
- Detailed setup instructions
- Usage examples
- Troubleshooting
- Customization options

**`QUICKSTART.md`** - Fast setup
- 10-minute setup guide
- Essential steps only
- Quick reference

**`requirements.txt`** - Python packages
- All dependencies
- Install with: `pip install -r requirements.txt`

**`.gitignore`** - Git ignore rules
- Protects sensitive files
- Excludes screenshots
- Prevents accidental commits of API keys

### Generated Files

**`screenshots/`** directory
- Auto-created on first run
- Stores all response screenshots
- Organized by query number and platform
- Named: `Q{num}_{platform}_{date}.png`

## Data Flow

```
queries.json 
    ↓
ai_query_tracker.py
    ↓
    ├─→ Claude API      ─→ Screenshot ─→ Google Sheets
    ├─→ ChatGPT API     ─→ Screenshot ─→ Google Sheets  
    ├─→ Google AI API   ─→ Screenshot ─→ Google Sheets
    └─→ Perplexity API  ─→ Screenshot ─→ Google Sheets
```

## Important Notes

### Security
- Never commit `config.json` or `google-credentials.json`
- The `.gitignore` file protects these automatically
- Keep API keys secure and rotate regularly

### Backups
- Google Sheets automatically saves and versions
- Screenshots are saved locally - back them up periodically
- Consider exporting Google Sheets data regularly

### Maintenance
- Check API usage/costs monthly
- Update queries.json as needed
- Review and update competitor lists in the code
- Archive old screenshots to save space

## Typical Workflow

1. **Setup** (one-time):
   ```bash
   pip install -r requirements.txt
   # Edit config.json with your keys
   python test_setup.py
   ```

2. **Weekly tracking**:
   ```bash
   python ai_query_tracker.py
   # Review Google Sheet
   # Fill in manual columns
   ```

3. **Testing new queries**:
   ```bash
   python quick_query.py "New question?"
   # If good, add to queries.json
   ```

4. **Troubleshooting**:
   ```bash
   python test_setup.py
   # Check which component is failing
   ```
