# SmartHistory Setup Guide

Complete installation and configuration instructions for SmartHistory.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- Git

### Installation

Setup once:
```bash
# Clone the repository
git clone <your-repo-url>
cd smartHistory

# Backend dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Frontend dependencies
cd src/frontend && npm ci && cd -
```

### Environment Configuration

Backend environment file: `src/backend/.env.development` (provided).

Key settings to adjust:
- `CORS_ORIGINS` - Add your frontend URL if different from localhost:3000
- Database connection settings
- API keys for Google Calendar and Notion (see Authentication section below)

### Running the Application

**Option 1: Unified Development Servers**
```bash
# Start both backend + frontend
./runner/deploy.sh local
```

**Option 2: Individual Services**
```bash
# Backend (Terminal 1)
source venv/bin/activate
python src/backend/start.py development

# Frontend (Terminal 2)
cd src/frontend && npm run dev
```

Access the application at: `http://localhost:3000`

---

## 📁 Project Structure

```
smartHistory/
├── runner/              # Scripts to run services
│   ├── deploy.sh        # Unified deployment script
│   ├── run_agent.py     # AI agent processing
│   ├── run_api.py       # API server
│   └── setup_api.py     # API setup
│
├── META/                # Project documentation (organized)
│   ├── core/           # Core project files
│   ├── features/       # Feature-specific docs
│   ├── archive/        # Historical documentation
│   ├── proposals/      # Analysis and proposals
│   └── README.md       # META organization guide
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
├── .env                # Environment variables
├── credentials.json    # Service credentials
├── token.json         # Authentication tokens
├── smarthistory.db    # SQLite database
├── pytest.ini        # Test configuration
└── requirements.txt    # Python dependencies
```

---

## 🔧 Authentication & API Setup

### Google Calendar Integration

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Calendar API

2. **Create Credentials**
   - Go to "Credentials" in the API & Services section
   - Create "OAuth 2.0 Client IDs" for desktop application
   - Download the JSON file and save as `credentials.json` in the root directory

3. **First Run Authentication**
   - Run the ingestion script: `python runner/run_ingest.py --start 2025-02-01 --end 2025-09-10 --cal-ids primary`
   - This will open a browser window for OAuth consent
   - Grant permissions and the `token.json` file will be created automatically

### Notion Integration

1. **Create Notion Integration**
   - Go to [Notion Developers](https://developers.notion.com/)
   - Create a new integration
   - Copy the Internal Integration Token

2. **Configure Workspace Access**
   - In your Notion workspace, go to Settings & Members
   - Add your integration under "Connections"
   - Grant access to the pages you want to analyze

3. **Add API Key**
   - Add `NOTION_API_KEY=your_integration_token` to your `.env` file

---

## 🏃‍♂️ Runner Scripts

### `./runner/deploy.sh`
Unified deployment helper:
- `local` - Start development servers (backend + frontend)
- `docker` - Docker Compose setup for development

Example:
```bash
./runner/deploy.sh local
```

### `./runner/run_api.py`
Standalone API server runner with database setup.

```bash
python runner/run_api.py
```

### `./runner/run_ingest.py`
Database ingestion and indexing (no tagging):
- Ensures database schema (migrations + column repair)
- Ingests Google Calendar events via API (OAuth Desktop credentials)
- Ingests Notion workspace pages/blocks via API (NOTION_API_KEY)
- Indexes Notion abstracts + embeddings for leaf blocks

Examples:
```bash
# Ingest data for specific date range
python runner/run_ingest.py --start 2025-02-01 --end 2025-09-10 --cal-ids primary

# Ingest from multiple calendars
python runner/run_ingest.py --start 2025-02-01 --end 2025-09-10 --cal-ids primary,work@company.com
```

### `./runner/run_process_range.py`
Processing + tagging for a date range (no ingestion):
- Purges processed_activities in range and re-tags with enriched context (up to 10 tags)
- Uses date-based Notion retrieval to enrich each calendar event with relevant abstracts

Examples:
```bash
# Process and tag activities for date range
python runner/run_process_range.py --start 2025-02-01 --end 2025-09-10

# Regenerate system tags
python runner/run_process_range.py --start 2025-02-01 --end 2025-09-10 --regenerate-system-tags
```

### `./runner/run_build_taxonomy.py`
Generate data-driven taxonomy and synonyms from your Calendar + Notion context using AI:
- Produces `src/backend/agent/resources/hierarchical_taxonomy_generated.json`
- Produces `src/backend/agent/resources/synonyms_generated.json`
- TagGenerator auto-loads these files if present

Example:
```bash
python runner/run_build_taxonomy.py --start 2025-02-01 --end 2025-09-10
```

### `./runner/run_parsers.py`
Data parsing utilities for Notion and Google Calendar.

### `./runner/run_agent.py`
AI agent for intelligent activity processing and analysis.

---

## 🏗️ Technical Architecture

### Calendar-as-Query → Notion-as-Context (Tagging Flow)

1. **Data Ingestion**
   - Ingest Notion workspace into DB: `notion_pages`, `notion_blocks` (tree, text, is_leaf), `notion_block_edits`
   - Index leaf blocks: generate 30–100 word abstracts + embeddings for retrieval

2. **Tagging Process**
   - At tagging time, retrieve top‑K Notion abstracts around each event date (±window) by embedding similarity
   - TagGenerator enriches event text with abstracts and selects up to 10 tags using calibrated scoring (synonyms/taxonomy/weights)
   - Persist `processed_activities` and `activity_tags` with confidence; triggers update tag usage

3. **Storage**
   - SQLite for development
   - PostgreSQL recommended for production
   - All processed data stored with confidence scores and metadata

### Tagging Logs (Observability)

- `runner/run_process_range.py` writes a JSONL log per run to `logs/`
- Each line records: calendar summary/details, retrieved Notion abstracts (with scores), normalized tag scores, and selected tags

Monitor processing:
```bash
tail -f logs/tagging_run_2025-02-01_to_2025-09-10_*.jsonl
```

---

## 🐳 Deployment Options

### Local Development
Use the runner scripts as described above.

### Docker Compose
```bash
./runner/deploy.sh docker
```

### Production Deployment
See detailed instructions in `deployment/DEPLOYMENT.md`:
- AWS deployment configurations
- Nginx reverse proxy setup
- Database migration guides
- Monitoring and logging setup

### Static Frontend (GitHub Pages)
For frontend-only hosting:
```bash
cd src/frontend
npm run build
npm run export
```

---

## 🔧 Development Workflow

### Database Setup
1. SQLite database is created automatically on first run
2. Schema migrations run automatically
3. For production, configure PostgreSQL connection in environment variables

### Adding New Data Sources
1. Create parser in `src/backend/parsers/`
2. Add ingestion logic to `runner/run_ingest.py`
3. Update database schema if needed
4. Add API endpoints in `src/backend/api/`

### Frontend Development
```bash
cd src/frontend
npm run dev          # Development server
npm run build        # Production build
npm run lint         # Linting
npm run type-check   # TypeScript checking
```

### Backend Development
```bash
cd src/backend
python start.py development  # Development server with hot reload
pytest                       # Run tests
python -m pytest tests/     # Run specific test directory
```

---

## 📊 Configuration Details

### Environment Variables

**Backend (.env.development)**
```env
# Database
DATABASE_URL=sqlite:///./smarthistory.db

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# API Keys
NOTION_API_KEY=your_notion_token
OPENAI_API_KEY=your_openai_key

# Logging
LOG_LEVEL=INFO
```

**Frontend (if needed)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Performance Tuning

**Database Optimization**
- Ensure proper indexing on frequently queried columns
- Consider connection pooling for production
- Monitor query performance with logging

**AI Processing**
- Adjust batch sizes in processing scripts
- Configure embedding model settings
- Set appropriate confidence thresholds for tagging

---

## 🧪 Testing

### Backend Tests
```bash
cd src/backend
pytest                           # All tests
pytest tests/test_api.py        # Specific test file
pytest -v                       # Verbose output
pytest --cov                    # Coverage report
```

### Frontend Tests
```bash
cd src/frontend
npm test                        # Jest tests
npm run test:e2e               # End-to-end tests (if configured)
```

### Integration Tests
```bash
# From project root
python runner/run_tests.py      # Full integration test suite
```

---

## 🐛 Troubleshooting

### Common Issues

**Authentication Problems**
- Ensure `credentials.json` is in the root directory
- Check OAuth scopes in Google Cloud Console
- Verify Notion integration has proper workspace access

**Database Issues**
- Delete `smarthistory.db` to reset development database
- Check database file permissions
- Verify SQLite version compatibility

**API Connection Issues**
- Confirm backend is running on correct port (8000)
- Check CORS settings if frontend can't connect
- Verify firewall settings for local development

**Processing/Tagging Issues**
- Check logs in `logs/` directory
- Verify API keys are correctly configured
- Monitor AI model rate limits and quotas

### Getting Help

1. Check the `META/` directory for detailed documentation
2. Review logs in the `logs/` directory
3. Use verbose flags (`-v`) with runner scripts for detailed output
4. Check GitHub issues for known problems and solutions

---

## 📚 Additional Resources

- **[META/core/DESIGN.md](META/core/DESIGN.md)** - System architecture details
- **[META/core/REGULATION.md](META/core/REGULATION.md)** - Development guidelines
- **[META/features/TAGGING_PIPELINE.md](META/features/TAGGING_PIPELINE.md)** - Detailed tagging flow
- **[deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md)** - Production deployment guide

---

**Ready to dive deeper? Explore the `META/` directory for comprehensive technical documentation.**