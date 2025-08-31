# SmartHistory API Quick Start Guide

Get the SmartHistory REST API up and running in minutes.

## Prerequisites

- Python 3.8+ installed
- SmartHistory project cloned locally
- Virtual environment set up

## 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install API dependencies
pip install fastapi uvicorn[standard] pydantic httpx pytest pytest-asyncio python-multipart

# Verify installation
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed')"
```

## 2. Set Up Environment

```bash
# Create .env file (optional - development mode works without API keys)
echo "SMARTHISTORY_ENV=development" > .env
echo "SMARTHISTORY_API_KEY=dev-key-12345" >> .env
```

## 3. Start the API Server

```bash
# Start the development server
python run_api.py

# Or with custom settings
python run_api.py --host 0.0.0.0 --port 8080 --reload
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 4. Test the API

### Quick Health Check
```bash
curl http://localhost:8000/health
```

### Get Raw Activities
```bash
curl http://localhost:8000/api/v1/activities/raw
```

### Get System Stats
```bash
curl http://localhost:8000/api/v1/system/stats
```

## 5. Run Tests

```bash
# Unit tests
cd src/backend
python run_tests.py

# Manual integration test  
python ../../test_features/api_manual_test.py

# Specific test file
python run_tests.py --pattern test_activities.py
```

## API Endpoints Overview

### 📊 Activities
- `GET /api/v1/activities/raw` - Get raw activities
- `GET /api/v1/activities/processed` - Get processed activities

### 📈 Insights  
- `GET /api/v1/insights/overview` - Activity overview and stats
- `GET /api/v1/insights/time-distribution` - Time-based analytics

### 🏷️ Tags
- `GET /api/v1/tags` - List all tags
- `POST /api/v1/tags` - Create new tag
- `PUT /api/v1/tags/{id}` - Update tag
- `DELETE /api/v1/tags/{id}` - Delete tag

### ⚙️ Processing
- `POST /api/v1/process/daily` - Trigger activity processing
- `POST /api/v1/import/calendar` - Import calendar data
- `POST /api/v1/import/notion` - Import Notion data

### 🔧 System
- `GET /api/v1/system/health` - System health check
- `GET /api/v1/system/stats` - System statistics

## Example Usage

### Create a Tag
```bash
curl -X POST http://localhost:8000/api/v1/tags \
  -H "Content-Type: application/json" \
  -d '{
    "name": "work",
    "description": "Work-related activities", 
    "color": "#4285f4"
  }'
```

### Get Insights
```bash
curl "http://localhost:8000/api/v1/insights/overview?date_start=2025-08-30"
```

### Trigger Processing
```bash
curl -X POST http://localhost:8000/api/v1/process/daily \
  -H "Content-Type: application/json" \
  -d '{"use_database": true}'
```

## Development Workflow

1. **Start the API**: `python run_api.py --reload`
2. **Populate Database**: `python run_parsers.py`
3. **Process Activities**: `python run_agent.py --mode daily`
4. **Test Endpoints**: Visit http://localhost:8000/docs
5. **Run Tests**: `cd src/backend && python run_tests.py`

## Authentication

### Development Mode (Default)
No authentication required when `SMARTHISTORY_ENV=development`

### Production Mode  
```bash
# Set API key
export SMARTHISTORY_API_KEY="your-secure-api-key"

# Use in requests
curl -H "Authorization: Bearer your-secure-api-key" \
  http://localhost:8000/api/v1/activities/raw
```

## Troubleshooting

### Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=.
python run_api.py
```

### Database Issues
```bash
# Check database status
python -c "
from src.backend.database import get_db_manager
db = get_db_manager()
print('Database OK')
"
```

### Missing Dependencies
```bash
# Install missing packages
pip install -r requirements-api.txt
```

### Port Already in Use
```bash
# Use different port
python run_api.py --port 8080
```

## Next Steps

- **Frontend Integration**: Use the API endpoints in your frontend application
- **Production Deployment**: Configure proper authentication and HTTPS
- **Monitoring**: Add logging and metrics collection
- **Scaling**: Consider adding Redis caching and load balancing

## API Documentation

- **Full API Spec**: `/docs` endpoint (Swagger UI)
- **Alternative Docs**: `/redoc` endpoint  
- **Design Document**: `src/backend/api/API_DESIGN.md`
- **Module Documentation**: `src/backend/api/api_META.md`

## Support

- **Issues**: Check console logs and error messages
- **Testing**: Run `python run_tests.py` to verify functionality
- **Development**: Use `--reload` flag for auto-restart during development

---

🎉 **You're ready to use the SmartHistory API!**

Visit http://localhost:8000/docs to explore all available endpoints interactively.