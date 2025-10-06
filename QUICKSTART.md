# Quick Start Guide

Get up and running in 10 minutes!

## 1. Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

## 2. Get API Keys (5 min)

Open these links in separate tabs and get your API keys:

- **Claude**: https://console.anthropic.com/ → API Keys
- **ChatGPT**: https://platform.openai.com/ → API Keys  
- **Gemini**: https://aistudio.google.com/ → Get API Key
- **Perplexity**: https://www.perplexity.ai/settings/api

## 3. Set Up Google Sheets (3 min)

### A. Get Credentials:
1. Go to: https://console.cloud.google.com/
2. Create project → Enable "Google Sheets API" and "Google Drive API"
3. Create Service Account → Download JSON key → Save as `google-credentials.json`

### B. Create Sheet:
1. Create new Google Sheet
2. Add these headers in row 1:
   ```
   Query # | Query Text | Platform | Test Date | BOB Mentioned? | Mention Context | Position | Competitors Mentioned | Sources Cited | Accuracy | Screenshot File | Notes
   ```
3. Copy Sheet ID from URL (the long string between /d/ and /edit)
4. Share sheet with service account email (from JSON file) as Editor

## 4. Configure (1 min)

Edit `config.json`:

```json
{
  "anthropic_api_key": "sk-ant-YOUR_KEY",
  "openai_api_key": "sk-YOUR_KEY",
  "google_api_key": "AIza-YOUR_KEY",
  "perplexity_api_key": "pplx-YOUR_KEY",
  "google_credentials_path": "google-credentials.json",
  "spreadsheet_id": "YOUR_SHEET_ID_HERE"
}
```

## 5. Test Setup (30 sec)

```bash
python test_setup.py
```

If all tests pass, you're ready! ✅

## 6. Run Your First Query (30 sec)

```bash
python quick_query.py "What is the best powder sunscreen?"
```

Or run all queries:

```bash
python ai_query_tracker.py
```

---

## Weekly Workflow

1. **Sunday/Monday**: Run `python ai_query_tracker.py`
2. **Review**: Check Google Sheet for new responses
3. **Manual columns**: Fill in Context, Position, Accuracy, Notes
4. **Compare**: See how responses changed from last week

That's it! 🎉

---

## Troubleshooting

❌ **"Permission denied" on Google Sheets**  
→ Make sure you shared the sheet with the service account email

❌ **API errors**  
→ Run `python test_setup.py` to check which API is failing

❌ **Import errors**  
→ Run `pip install -r requirements.txt` again

Need more help? Check the full README.md
