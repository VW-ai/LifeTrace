# LifeTrace Onboarding Guide
## From Zero to Insights in 5 Steps

**Last Updated:** October 5, 2025

---

## Overview
This guide walks you through setting up LifeTrace from scratch, starting with an empty database and ending with a fully functional personal productivity tracker with AI-generated insights.

**Total Time:** 15-30 minutes (depending on data volume)

---

## Prerequisites

Before you begin, make sure you have:
- ✅ Backend server running (`./runner/deploy.sh local`)
- ✅ Frontend running (`cd src/frontend && npm run dev`)
- ✅ Google Calendar with events (recommended: at least 1 month of data)
- ✅ Notion workspace with pages/notes (optional but recommended)

---

## Step 1: Configure API Connections (5 minutes)

### 1.1 Access API Configuration
1. Open LifeTrace in your browser: `http://localhost:3000`
2. Navigate to: **Settings → API Configuration**
3. You'll see the system health dashboard

### 1.2 Configure Notion API

**What you'll need:**
- Notion Integration Token (starts with `ntn_...`)

**Steps:**
1. Go to [developers.notion.com](https://developers.notion.com/)
2. Click "New integration"
3. Give it a name: "LifeTrace"
4. Copy the "Internal Integration Token"
5. In LifeTrace Settings:
   - Click **"Configure"** button next to Notion API
   - Paste your token
   - Click **"Test Connection"** → Should show ✅ Success
   - Click **"Save Configuration"**
6. Status should update to: ✅ **Connected**

**Grant Access to Your Workspace:**
1. Open any Notion page in your workspace
2. Click "..." menu → "Connections" → "Connect to LifeTrace"
3. This allows LifeTrace to read your Notion content

### 1.3 Configure OpenAI API (for AI tagging)

**What you'll need:**
- OpenAI API Key (starts with `sk-proj-...`)

**Steps:**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key (you won't see it again!)
4. In LifeTrace Settings:
   - Click **"Configure"** button next to OpenAI API
   - Paste your key
   - Set Model: `gpt-4o-mini` (recommended, cost-effective)
   - Set Embedding Model: `text-embedding-3-small`
   - Click **"Test Connection"** → Should show ✅ Success
   - Click **"Save Configuration"**

### 1.4 Configure Google Calendar

**What you'll need:**
- Google Cloud Project with Calendar API enabled
- OAuth 2.0 credentials

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "LifeTrace"
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`
6. Place it in project root: `/home/victor/lifetrace/LifeTrace/credentials.json`
7. Run OAuth flow from terminal:
   ```bash
   cd /home/victor/lifetrace/LifeTrace
   python runner/run_ingest.py --start 2025-01-01 --end 2025-01-31 --cal-ids primary
   ```
8. Browser will open → Sign in to Google → Allow access
9. This creates `token.json` in project root
10. Refresh Settings page → Google Calendar: ✅ **Connected**

**✅ Checkpoint:** All three APIs should show "Connected" status

---

## Step 2: Import Your Data (10-15 minutes)

### 2.1 Navigate to Data Ingestion
1. Go to: **Settings → Data Ingestion**

### 2.2 Backfill Google Calendar (Historical Data)

**Recommended:** Import 3-6 months of calendar history

1. In "Calendar Backfill" section:
   - Set **Number of Months**: `6` (adjust as needed)
   - Click **"Backfill 6 Months"**
2. Wait for completion toast: "Calendar backfill completed: X events imported"
3. Note the date range shown

**What this does:**
- Imports all calendar events from the last 6 months
- Stores them in `raw_activities` table
- Events include: title, time, duration, attendees, description

### 2.3 Import Recent Notion Content

1. In "Notion Data Import" section:
   - Set **Hours Since Last Update**: `2160` (90 days)
   - Click **"Import Notion Data"**
2. Wait for completion: "Notion import completed: X blocks imported"

**What this does:**
- Imports Notion pages and blocks edited in last 90 days
- Creates context for AI tagging (abstracts, embeddings)
- Stores in `notion_pages` and `notion_blocks` tables

### 2.4 Index Notion Blocks for Semantic Search

**Why:** Enables AI to find relevant context when tagging activities

1. In "Notion Block Indexing" section:
   - Select Scope: **"All"**
   - Click **"Index Blocks"**
2. Wait for: "Notion indexing completed: X blocks indexed"

**What this does:**
- Generates 30-100 word abstracts for each block
- Creates vector embeddings for semantic search
- Enables context retrieval during tag generation

**✅ Checkpoint:** Check "Import Status" section - should show recent import times

---

## Step 3: Generate AI Tags (5-10 minutes)

### 3.1 Navigate to Tag Generation
1. Go to: **Settings → Tag Generation**

### 3.2 Build Taxonomy (Optional but Recommended)

**Why:** Creates a structured tag hierarchy for better organization

1. In "Taxonomy Building" section:
   - Set Date Range: Last 30 days (or your data range)
   - Click **"Build Taxonomy"**
2. Wait for: "Taxonomy build completed"

**What this creates:**
- Tag categories (Work, Personal, Health, etc.)
- Tag relationships and synonyms
- Structured taxonomy file for AI guidance

### 3.3 Generate Tags for Your Activities

**This is the magic step!**

1. In "Tag Processing" section:
   - ✅ Enable **"Use Database"**
   - ✅ Enable **"Regenerate System Tags"** (first time)
   - Click **"Start Tag Generation"**
2. Watch progress in "Recent Processing Jobs"
3. Wait for completion: Job status → "Completed"

**What happens:**
1. Loads all raw activities from database
2. For each activity:
   - Retrieves relevant Notion context using semantic search
   - Sends to OpenAI with activity details + context
   - AI generates 1-10 relevant tags
   - Tags are validated against taxonomy
3. Creates `processed_activities` with tags
4. Updates `tags` table with usage statistics

**✅ Checkpoint:** Processing job shows "Completed" with counts

---

## Step 4: Review and Refine (2-3 minutes)

### 4.1 Check Tag Quality

1. Go to: **Settings → Tag Cleanup**
2. Set thresholds:
   - Removal Threshold: `0.3`
   - Merge Threshold: `0.7`
3. Enable **"Dry Run"**
4. Click **"Analyze Tags"**

**What to look for:**
- Tags marked for removal (too generic, meaningless)
- Tags suggested for merging (synonyms)
- Tag usage statistics

### 4.2 Execute Cleanup (if needed)

1. Review dry-run results
2. If satisfied, disable "Dry Run"
3. Click **"Execute Cleanup"**
4. Tags are cleaned/merged automatically

---

## Step 5: Explore Your Data (2 minutes)

### 5.1 Go to Dashboard
1. Navigate to: **Dashboard** (main page)
2. You should now see:
   - Activity timeline
   - Tag distribution charts
   - Top activities by tag
   - Time tracking statistics

### 5.2 Use Filters
1. Try filtering by:
   - Date range (last week, month, custom)
   - Tags (Work, Personal, etc.)
   - Data source (Calendar, Notion)
2. Search for specific activities

### 5.3 Explore Views
1. **Timeline View**: See activities over time
2. **Galaxy View**: Tag relationship network
3. **River View**: Tag frequency streams
4. **Calendar View**: Monthly activity heatmap

**✅ You're Done!** Your LifeTrace is now fully operational!

---

## Ongoing Maintenance

### Daily/Weekly Workflow

**Option A: Automated (Recommended)**
Set up a cron job to run daily:
```bash
# Add to crontab
0 1 * * * cd /path/to/LifeTrace && python runner/run_ingest.py --hours 24 && python runner/run_process_range.py --today
```

**Option B: Manual**
1. Go to **Settings → Data Ingestion**
2. Set hours to `168` (1 week)
3. Click "Import Calendar Data" and "Import Notion Data"
4. Go to **Settings → Tag Generation**
5. Click "Start Tag Generation"

### Monthly Maintenance

1. **Review Tags** (Settings → Tag Cleanup)
   - Run analysis monthly
   - Clean up low-quality tags
   - Merge synonyms

2. **Rebuild Taxonomy** (Settings → Tag Generation)
   - Click "Build Taxonomy" with last 30 days
   - Keeps taxonomy fresh with new patterns

3. **Check Logs** (Settings → Processing Logs)
   - Look for errors
   - Monitor API usage
   - Verify data quality

---

## Troubleshooting

### "No activities found to process"

**Cause:** No data imported yet
**Fix:** Go to Step 2 - import calendar and Notion data first

### "Failed to connect to Notion API"

**Possible causes:**
1. API key is invalid → Get new key from developers.notion.com
2. Haven't granted workspace access → Connect integration to pages
3. Key not loaded → Restart backend server

**Fix:** Check backend logs for specific error

### "Processing failed: No OpenAI API key"

**Cause:** OpenAI not configured
**Fix:** Complete Step 1.3 - configure OpenAI API

### Tags seem generic or low-quality

**Causes:**
1. Limited Notion context
2. Taxonomy not built
3. Calendar events lack detail

**Fixes:**
1. Add more detailed notes to Notion
2. Build taxonomy (Step 3.2)
3. Add descriptions to calendar events
4. Run tag cleanup (Step 4)

### "Database connection failed"

**Cause:** Database file missing or corrupted
**Fix:**
```bash
cd /home/victor/lifetrace/LifeTrace
python src/backend/database/cli.py migrate --direction up
```

---

## Tips for Best Results

### Calendar Events
- ✅ Use descriptive titles
- ✅ Add descriptions with context
- ✅ Include attendees
- ❌ Avoid single-word titles like "Meeting"

### Notion Notes
- ✅ Write detailed daily notes
- ✅ Use headers to structure content
- ✅ Link related pages
- ❌ Don't leave pages blank

### Tag Generation
- ✅ Build taxonomy before first run
- ✅ Use database mode for better results
- ✅ Let AI generate multiple tags per activity
- ❌ Don't regenerate tags too often (expensive)

### Data Quality
- ✅ Import regularly (weekly)
- ✅ Review tags monthly
- ✅ Clean up meaningless tags
- ✅ Rebuild taxonomy quarterly

---

## Next Steps

After completing setup:

1. **Explore Advanced Features**
   - Reprocess date ranges with new taxonomy
   - Use semantic search for Notion context
   - Export data for analysis

2. **Optimize Performance**
   - Adjust tag generation thresholds
   - Fine-tune cleanup parameters
   - Build custom taxonomy categories

3. **Integrate More Data Sources**
   - Add multiple Google Calendars
   - Index more Notion workspaces
   - (Future: Apple Calendar, Todoist, etc.)

4. **Share Insights**
   - Export reports
   - Generate productivity summaries
   - Track progress over time

---

## Support

### Documentation
- `SETUP.md` - Installation instructions
- `META/features/UPDATE-SETTING.md` - Settings page features
- `META/features/API-KEY-MANAGEMENT.md` - API configuration details

### Logs
- Backend logs: Check console where `deploy.sh` is running
- Frontend logs: Browser developer console (F12)
- Processing logs: **Settings → Processing Logs**

### Common Issues
- Database schema: `python src/backend/database/cli.py migrate`
- API connection: **Settings → API Configuration** → Test Connection
- Data import: Check **Settings → Data Ingestion** → Import Status

---

## Success Metrics

After setup, you should have:
- ✅ 100+ raw activities imported
- ✅ 100+ processed activities with tags
- ✅ 20-50 unique tags generated
- ✅ Dashboard showing activity distribution
- ✅ Search and filtering working
- ✅ All views displaying data

**If any metric is 0, review the corresponding step above.**

---

## Feedback & Iteration

LifeTrace improves over time as you:
1. Add more detailed Notion notes
2. Accumulate more calendar history
3. Refine taxonomy structure
4. Clean up low-quality tags
5. Adjust AI prompts and thresholds

**Give it 2-4 weeks** of regular use to see the full value!

---

**Congratulations!** You're now tracking your life with AI-powered insights. 🎉
