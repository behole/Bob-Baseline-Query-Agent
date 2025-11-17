# GEO Audit - SUPER SIMPLE Usage Guide

## ONE-COMMAND FULL AUDIT

```bash
./run_full_audit.sh
```

This runs **everything**:
1. Client setup (prompts you for brand, industry, products)
2. **Auto-detects competitors** for your industry
3. AI query generation (uses competitors for comparison queries)
4. Platform tracking
5. HTML report (includes competitor analysis)
6. Cloudflare deployment (optional)

**Time:** ~20-30 minutes (depending on query count)

**What gets auto-detected:**
- Competitors based on your industry selection
- You can accept, edit, or replace the suggested list

---

## MANUAL STEP-BY-STEP (if you want control)

### 1. Initialize Client
```bash
./geo-audit init nike --industry "athletic wear" --brand "Nike"
```
- Creates client config with industry & brand
- Add competitors manually to `config/clients/nike.yaml` if needed

### 2. Generate Queries
```bash
./geo-audit generate --client nike --output nike_queries.json --count 60
```
- Prompts for product categories if not provided
- Uses AI to create 60 queries

### 3. Run Tracking
```bash
./geo-audit track --client nike --queries nike_queries.json --worksheet "Nike_Audit_2025-11-17"
```
- Queries all 4 AI platforms
- Creates screenshots
- Logs to Google Sheets

### 4. Generate Report
```bash
python3 generate_comprehensive_report.py --brand Nike --sheet "Nike_Audit_2025-11-17" --output nike_report.html
```
- **11 comprehensive sections** matching professional audit format
- Executive summary with Performance Snapshot and Key Findings
- Platform insights (5 strategic points per platform)
- Content Gap Analysis by category
- Top 10 High-Value Query Opportunities (100-point scoring)
- Competitive Displacement Opportunities
- Projected Impact Analysis with 3 scenarios
- Strategic Action Plan with Quick Wins (scored 85-92/100)
- Implementation roadmap (3 phases, 90 days)

### 5. Deploy to Cloudflare
```bash
cp nike_report.html /Users/jjoosshhmbpm1/reports-worker/watermelonghost/public/
cd /Users/jjoosshhmbpm1/reports-worker/watermelonghost
npm run deploy
```

Report will be at: `https://reports.watermelonghost.com/nike_report.html`

---

## QUICK REFERENCE

| Command | What it does |
|---------|-------------|
| `./run_full_audit.sh` | **Run everything** with prompts |
| `./geo-audit init <client>` | Create client config |
| `./geo-audit generate ...` | Generate AI queries |
| `./geo-audit track ...` | Query platforms & log data |
| `./geo-audit test` | Test API connections |
| `python3 test_setup.py` | Verify setup |

---

## FILES YOU'LL GET

- `<client>_queries.json` - Generated queries
- `<client>_geo_report.html` - Final report
- `screenshots/` - Response screenshots
- Google Sheet - Raw tracking data

---

## INDUSTRIES WITH AUTO-COMPETITORS

The system has built-in competitor lists for:
- Athletic Wear / Sports
- Furniture / Home Furnishings
- Skincare / Beauty
- Sunscreen / Sun Protection
- Fashion / Apparel
- Electronics / Technology
- Food & Beverage
- Automotive
- Healthcare / Wellness
- Travel / Hospitality
- Real Estate / Property
- Financial Services
- Education / E-Learning
- Entertainment / Media

Don't see your industry? Select "General" and add competitors manually.

## TROUBLESHOOTING

**"No queries generated"**
→ Check API key in `config.json`

**"Permission denied on Google Sheets"**
→ Share sheet with service account email

**"Not enough queries"**
→ Increase `--count 80` or re-run generate

**"No competitors detected"**
→ Select a different industry or add them manually

**"Cloudflare deploy failed"**
→ Check you're in the right directory

---

## TIPS

✅ **First time?** Run `./geo-audit test` first
✅ **Weekly tracking?** Use same client, new worksheet name
✅ **Need more queries?** Just increase the `--count` number
✅ **Want faster?** Reduce query count to 30-40

---

That's it! 🎉
