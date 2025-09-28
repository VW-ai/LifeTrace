# SmartHistory - Activity Analytics Platform

A modern, industry-ready platform for processing and analyzing activity data from various sources like Notion and Google Calendar.

## 🚀 Quick Start

Setup once:
```bash
# Backend deps
python -m venv venv && source venv/bin/activate
pip install -r src/backend/requirements.txt

# Frontend deps
cd src/frontend && npm ci && cd -
```

Environment:
- Backend dev env file: `src/backend/.env.development` (provided). Adjust `CORS_ORIGINS` if needed.

Run:
```bash
# Unified dev servers (backend + frontend)
./runner/deploy.sh local

# Or start individually
python src/backend/start.py development
cd src/frontend && npm run dev
```

Access the app at: `http://localhost:3000`

## 📁 Project Structure

```
smartHistory/
├── runner/              # Scripts to run services
│   ├── deploy.sh        # Unified deployment script
│   ├── run_agent.py     # AI agent processing
│   ├── run_api.py       # API server
│   ├── run_parsers.py   # Data parsers
│   └── setup_api.py     # API setup
│
├── META/                # Project documentation
│   ├── README.md        # Detailed project information
│   ├── DESIGN.md        # Architecture design
│   ├── REGULATION.md    # Development guidelines
│   ├── PROGRESS.md      # Development progress
│   └── *.md            # Other documentation
│
├── deployment/          # Deployment configurations
│   ├── DEPLOYMENT.md    # Deployment guide
│   ├── docker-compose.yml # Local Docker setup
│   ├── Dockerfile.*     # Container definitions
│   ├── aws/            # AWS deployment configs
│   └── nginx.conf      # Reverse proxy config
│
├── src/                # Source code
│   ├── backend/        # FastAPI backend
│   └── frontend/       # Next.js frontend
│
├── tests/              # Test suites
├── test_features/      # Feature tests
├── .env                # Environment variables
├── credentials.json    # Service credentials
├── token.json         # Authentication tokens
├── smarthistory.db    # SQLite database
├── pytest.ini        # Test configuration
└── src/backend/requirements.txt # Backend Python dependencies
```

## 🏃‍♂️ Runner Scripts

### `./runner/deploy.sh`
Unified helpers:
- `local` - Start development servers (backend + frontend)
- `docker` - Docker Compose (dev/single-host)

### `./runner/run_api.py`
Standalone API server runner with database setup.

### `./runner/run_ingest.py`
DB-only ingestion and indexing (no tagging). Useful for debugging backfill.
- Ensures schema (migrations + column repair)
- Ingests Google Calendar events via API (OAuth Desktop credentials)
- Ingests Notion workspace pages/blocks via API (NOTION_API_KEY)
- Indexes Notion abstracts + embeddings for leaf blocks

Examples:
```
python runner/run_ingest.py --start 2025-02-01 --end 2025-09-10 --cal-ids primary
```

### `./runner/run_process_range.py`
Processing + tagging only for a date range (no ingestion).
- Purges processed_activities in range and re-tags with enriched context (up to 10 tags)
- Uses date-based Notion retrieval to enrich each calendar event with relevant abstracts

Examples:
```
python runner/run_process_range.py --start 2025-02-01 --end 2025-09-10
python runner/run_process_range.py --start 2025-02-01 --end 2025-09-10 --regenerate-system-tags
```

### `./runner/run_build_taxonomy.py`
Generate data-driven taxonomy and synonyms from your Calendar + Notion context using AI.
- Produces `src/backend/agent/resources/hierarchical_taxonomy_generated.json`
  and `src/backend/agent/resources/synonyms_generated.json`
- TagGenerator auto-loads these files if present.

Example:
```
python runner/run_build_taxonomy.py --start 2025-02-01 --end 2025-09-10
```

### `./runner/run_parsers.py`
Data parsing utilities for Notion and Google Calendar.

### `./runner/run_agent.py`
AI agent for intelligent activity processing.

## 📚 Documentation (META/)

All project documentation is organized in the `META/` directory:

- **README.md** - Comprehensive project documentation
- **DESIGN.md** - System architecture and design decisions  
- **REGULATION.md** - Development guidelines and standards
- **API_QUICKSTART.md** - API usage guide
- **DEPLOYMENT.md** - Detailed deployment instructions

## 🐳 Deployment

- Local dev and Docker Compose: see `deployment/DEPLOYMENT.md`.
- GitHub Pages for frontend-only hosting is supported (static export). See `deployment/DEPLOYMENT.md`.

## ⚙️ Configuration Files (Root)

Core configuration files remain in the root:

- `.env` - Environment variables
- `credentials.json` - Service account credentials
- `token.json` - API tokens
- `smarthistory.db` - SQLite database
- `pytest.ini` - Test configuration
- `requirements-api.txt` - Python dependencies

## 🔧 Development

1. **Setup**: Copy service credentials to root directory
2. **Backend**: `cd src/backend && python start.py development`  
3. **Frontend**: `cd src/frontend && npm run dev`
4. **Database**: SQLite file created automatically

## 🏗️ Architecture

- Backend: FastAPI with environment-based config
- Frontend: Next.js + TypeScript + Tailwind
- Database: SQLite for development
- Deployment: Local/dev Docker Compose; static frontend export to GH Pages

### Calendar-as-Query → Notion-as-Context (Tagging Flow)
- Ingest Notion workspace into DB: `notion_pages`, `notion_blocks` (tree, text, is_leaf), `notion_block_edits`
- Index leaf blocks: generate 30–100 word abstracts + embeddings for retrieval
- At tagging time, retrieve top‑K Notion abstracts around each event date (±window) by embedding similarity
- TagGenerator enriches event text with abstracts and selects up to 10 tags using calibrated scoring (synonyms/taxonomy/weights)
- Persist `processed_activities` and `activity_tags` with confidence; triggers update tag usage

See also:
- `META/TAGGING_PIPELINE.md` – detailed, end‑to‑end flow and debugging tips

### Tagging Logs (Observability)
- `runner/run_process_range.py` writes a JSONL log per run to `logs/`.
- Each line records: calendar summary/details, retrieved Notion abstracts (with scores), normalized tag scores, and selected tags.
- Example:
```
tail -f logs/tagging_run_2025-02-01_to_2025-09-10_*.jsonl
```

## 📊 Features

- **Multi-source parsing** (Notion, Google Calendar)
- **AI-powered processing** for intelligent categorization
- **Real-time dashboard** with analytics
- **Professional UI** with responsive design
- **Industry-ready deployment** with monitoring
- **Cloud-native architecture** for scalability

For detailed information, see documentation in the `META/` directory.
