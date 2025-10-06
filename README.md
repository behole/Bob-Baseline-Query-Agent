# AI Query Tracker

Track how AI platforms (Claude, ChatGPT, Google AI, Perplexity) respond to your queries over time. Perfect for competitive intelligence, brand monitoring, and tracking AI response evolution.

## Features

✅ Query multiple AI platforms with the same questions  
✅ Automatic logging to Google Sheets  
✅ Screenshot generation with date stamps  
✅ Basic BOB mention detection and competitor analysis  
✅ Citation tracking for Perplexity and Google AI  
✅ Batch processing of multiple queries  

---

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your API Keys

You'll need API keys for each platform:

#### **Anthropic (Claude)**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new key

#### **OpenAI (ChatGPT)**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new secret key

#### **Google AI (Gemini)**
1. Go to https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key"
4. Create a new API key

#### **Perplexity**
1. Go to https://www.perplexity.ai/settings/api
2. Sign up or log in
3. Generate an API key

### 3. Set Up Google Sheets API

#### Get Google Sheets Credentials:

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable **Google Sheets API**:
   - Click "Enable APIs and Services"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Enable **Google Drive API** (same process)
5. Create Service Account:
   - Go to "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Give it a name (e.g., "AI Query Tracker")
   - Click "Create and Continue"
   - Skip role assignment (click "Continue")
   - Click "Done"
6. Download JSON Key:
   - Click on your service account email
   - Go to "Keys" tab
   - Click "Add Key" → "Create New Key"
   - Choose "JSON"
   - Save as `google-credentials.json` in this directory

#### Create Your Google Sheet:

1. Create a new Google Sheet
2. Add these **exact column headers** in row 1:
   ```
   A: Query #
   B: Query Text
   C: Platform
   D: Test Date
   E: BOB Mentioned?
   F: Mention Context
   G: Position
   H: Competitors Mentioned
   I: Sources Cited
   J: Accuracy
   K: Screenshot File
   L: Notes
   ```
3. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[THIS_IS_YOUR_SHEET_ID]/edit
   ```
4. **Share the sheet** with your service account email:
   - Click "Share" in your Google Sheet
   - Paste the service account email (from the JSON file, looks like: `name@project-id.iam.gserviceaccount.com`)
   - Give it "Editor" access
   - Click "Send"

### 4. Configure the Application

Edit `config.json` with your credentials:

```json
{
  "anthropic_api_key": "sk-ant-...",
  "openai_api_key": "sk-...",
  "google_api_key": "AI...",
  "perplexity_api_key": "pplx-...",
  "google_credentials_path": "google-credentials.json",
  "spreadsheet_id": "YOUR_GOOGLE_SHEET_ID"
}
```

### 5. Add Your Queries

Edit `queries.json` with your questions:

```json
[
  {
    "num": 1,
    "text": "What is the best powder sunscreen?",
    "platforms": ["Claude", "ChatGPT", "Google AI", "Perplexity"]
  },
  {
    "num": 2,
    "text": "Best sunscreen for oily skin?",
    "platforms": ["Claude", "ChatGPT", "Google AI", "Perplexity"]
  }
]
```

---

## Usage

### Run All Queries

```bash
python ai_query_tracker.py
```

This will:
1. Query all platforms with your questions
2. Generate screenshots (saved in `screenshots/` folder)
3. Log everything to your Google Sheet
4. Analyze responses for BOB mentions and competitors

### Run Specific Queries

You can also import and use the tracker in your own script:

```python
from ai_query_tracker import AIQueryTracker

tracker = AIQueryTracker('config.json')

# Run a single query
tracker.run_query(
    query_num=1,
    query_text="What is the best powder sunscreen?",
    platforms=['Claude', 'ChatGPT']
)

# Or run a batch
queries = [
    {"num": 1, "text": "Query 1"},
    {"num": 2, "text": "Query 2"}
]
tracker.run_batch(queries)
```

---

## Output

### Google Sheet
All responses are automatically logged with:
- Query number and text
- Platform name
- Test date
- BOB mention detection (auto)
- Competitors mentioned (auto)
- Citations/sources (auto)
- Screenshot filename
- Columns for manual review (Context, Position, Accuracy, Notes)

### Screenshots
Saved in `screenshots/` folder with naming format:
```
Q1_Claude_10-06-2025.png
Q1_ChatGPT_10-06-2025.png
Q1_Google_AI_10-06-2025.png
Q1_Perplexity_10-06-2025.png
```

Each screenshot includes:
- Platform name and date stamp
- Full query text
- Complete response

---

## Weekly Tracking Workflow

To track changes over time:

1. **Week 1**: Run the script with your queries
2. **Week 2**: Run again with the same queries - new rows will be added
3. **Compare**: Use Google Sheets to filter by Query # and see how responses evolved

### Pro Tip: 
Use Google Sheets filters and pivot tables to:
- Compare how often BOB is mentioned across platforms
- Track position changes over time
- Identify trending competitors
- Analyze which platforms cite which sources

---

## Manual Review Columns

The script automatically fills most columns, but these require **manual review**:

- **E - BOB Mentioned?**: Auto-detected, but may need verification
- **F - Mention Context**: Review and categorize (Top recommendation, Listed among options, etc.)
- **G - Position**: Check where BOB appears (1st, 2nd, 3rd, etc.)
- **J - Accuracy**: Verify if BOB information is correct
- **L - Notes**: Add any observations

---

## Customization

### Change Models

Edit the model names in `ai_query_tracker.py`:

```python
# Line 63 - Claude model
model="claude-sonnet-4-20250514"

# Line 79 - ChatGPT model
model="gpt-4o"  # or "gpt-4-turbo", "gpt-3.5-turbo"

# Line 95 - Gemini model
model='gemini-2.0-flash-exp'  # or "gemini-pro"

# Line 110 - Perplexity model
"model": "llama-3.1-sonar-large-128k-online"
```

### Add More Competitors

Edit the competitor list (line 219):

```python
competitors = [
    'Supergoop', 'ColorScience', 'Peter Thomas Roth', 
    'Your Brand Here', 'Another Brand'
]
```

### Adjust Screenshot Styling

Customize colors, fonts, and layout in the `create_screenshot` method (line 127).

---

## Troubleshooting

### "Permission Denied" on Google Sheets
- Make sure you shared the sheet with your service account email
- Verify the service account has "Editor" access

### API Rate Limits
- The script includes 2-second delays between calls
- For large batches, consider adding longer delays

### Font Errors
- The script tries to use system fonts but falls back to defaults
- You can specify custom font paths in the `create_screenshot` method

### API Errors
- Check that all API keys are valid
- Verify you have credits/quota on each platform

---

## Cost Estimates

Approximate costs per query (prices as of Oct 2024):

- **Claude (Sonnet 4)**: ~$0.003 per query
- **ChatGPT (GPT-4o)**: ~$0.015 per query
- **Google AI (Gemini)**: Free tier available, then ~$0.001 per query
- **Perplexity**: ~$0.005 per query

**Total per query across all 4 platforms**: ~$0.024

**For 30 queries weekly**: ~$0.72/week or ~$3/month

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation for each platform
3. Verify your Google Sheets setup and permissions

---

## License

MIT License - Free to use and modify for your needs.
# Bob-Baseline-Query-Agent
