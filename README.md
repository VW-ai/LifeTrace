# SmartHistory - Activity Analytics Platform

A modern, industry-ready platform for processing and analyzing activity data from various sources like Notion and Google Calendar.

## 🚀 Quick Start

```bash
# Start development environment
./runner/deploy.sh local

# Or start with Docker
./runner/deploy.sh docker
```

Access your dashboard at: `http://localhost:5174`

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
│   └── frontend/       # React frontend
│
├── tests/              # Test suites
├── test_features/      # Feature tests
├── .env                # Environment variables
├── credentials.json    # Service credentials
├── token.json         # Authentication tokens
├── smarthistory.db    # SQLite database
├── pytest.ini        # Test configuration
└── requirements-api.txt # Python dependencies
```

## 🏃‍♂️ Runner Scripts

### `./runner/deploy.sh`
Unified deployment script supporting multiple environments:
- `local` - Start development servers
- `docker` - Docker Compose deployment
- `production` - Production deployment
- `aws` - AWS ECS deployment

### `./runner/run_api.py`
Standalone API server runner with database setup.

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

## 🐳 Deployment (deployment/)

Industry-ready deployment configurations:

- **Docker containers** with multi-stage builds
- **Kubernetes** manifests for orchestration
- **Cloud provider** specific configurations (AWS, GCP, Azure)
- **CI/CD pipelines** for automated deployment

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

- **Backend**: FastAPI with dynamic configuration
- **Frontend**: React + TypeScript + Vite
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Docker + Kubernetes ready
- **Monitoring**: Prometheus + Grafana integration

## 📊 Features

- **Multi-source parsing** (Notion, Google Calendar)
- **AI-powered processing** for intelligent categorization
- **Real-time dashboard** with analytics
- **Professional UI** with responsive design
- **Industry-ready deployment** with monitoring
- **Cloud-native architecture** for scalability

For detailed information, see documentation in the `META/` directory.