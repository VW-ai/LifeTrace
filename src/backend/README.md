# SmartHistory Backend

This directory contains the backend components for the SmartHistory project, organized into a clean, modular architecture.

## Directory Structure

```
src/backend/
├── agent/                 # AI Agent for Activity Processing
│   ├── core/             # Core agent functionality
│   │   ├── models.py     # Data models and structures
│   │   ├── data_consumer.py     # Data loading and validation
│   │   ├── activity_matcher.py # Cross-source activity matching
│   │   ├── activity_processor.py # Main processing orchestrator
│   │   └── agent.py      # CLI entry point and utilities
│   ├── tools/            # Agent tools and utilities
│   │   └── tag_generator.py    # LLM-powered tag generation
│   ├── prompts/          # LLM prompts and templates
│   │   └── tag_prompts.py      # Tag generation prompts
│   └── __init__.py       # Main agent module exports
├── parsers/              # Data source parsers
│   ├── google_calendar/  # Google Calendar data parser
│   ├── notion/          # Notion data parser
│   └── __init__.py
└── test_features/        # Test scripts and utilities
    ├── agent_tests/      # Agent functionality tests
    ├── parser_tests/     # Parser functionality tests
    └── integration_tests/ # Full system integration tests
```

## Core Components

### AI Agent (`agent/`)

The AI Agent is the heart of SmartHistory's data processing pipeline. It operates on a **database-first architecture**, eliminating JSON intermediate files:

- **Matches activities** across different data sources (Notion, Google Calendar)
- **Generates intelligent tags** using LLM integration
- **Estimates durations** for untracked activities
- **Consolidates data** into structured activity records
- **Database-first**: All data flows through SQLite database for better performance and reliability

#### Key Features:
- 🔗 **Smart Matching**: Correlates activities using time and content similarity
- 🏷️ **AI Tagging**: Uses OpenAI GPT models for consistent categorization  
- ⏱️ **Duration Estimation**: Content-based duration estimation for Notion activities
- 🔄 **Tag Consistency**: System-wide tag regeneration to maintain vocabulary
- 📊 **Analytics**: Rich insights and statistics generation

### Parsers (`parsers/`)

Data source parsers extract and structure raw data directly into the database:

- **Google Calendar Parser**: Extracts calendar events with timing information and saves to database
- **Notion Parser**: Processes Notion blocks and hierarchical content and saves to database
- **Database-first**: No JSON intermediate files - data goes directly from source to SQLite database

### Test Features (`test_features/`)

Comprehensive testing utilities organized by component:

- **Agent Tests**: Functionality testing, debugging utilities, capability demonstrations
- **Parser Tests**: Data parsing validation and edge case testing  
- **Integration Tests**: End-to-end system workflow testing

## Quick Start

### 1. Set up environment
```bash
# Activate virtual environment
source src/backend/act.sh

# Install dependencies (if needed)
pip install openai python-dotenv
```

### 2. Configure API keys
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your-api-key-here
NOTION_API_KEY=your-notion-api-key
# ... other keys
```

### 3. Run Parsers (Database-First)
```bash
# Parse and save data directly to database
python run_parsers.py
```

### 4. Run the AI Agent
```bash
# Quick test with database data
python src/backend/test_features/agent_tests/test_agent_capabilities.py

# Process database data (daily mode)
python run_agent.py --mode daily

# Generate insights from processed data
python run_agent.py --mode insights
```

## Usage Examples

### Basic Agent Processing
```python
from src.backend.agent import ActivityProcessor, load_api_key

# Initialize with API key
api_key = load_api_key()
processor = ActivityProcessor(openai_api_key=api_key)

# Process daily activities (database-first approach)
report = processor.process_daily_activities(
    use_database=True  # Reads from database, saves to database
    # Optional legacy file parameters available for fallback
)
```

### Custom Tag Generation
```python
from src.backend.agent import TagGenerator, TagPrompts

# Create custom prompts
custom_prompts = TagPrompts()

# Generate tags with custom logic
generator = TagGenerator(api_key=api_key)
tags = generator.generate_tags_for_activity(activity)
```

### Activity Matching
```python
from src.backend.agent import ActivityMatcher, RawActivity

# Configure matching parameters
matcher = ActivityMatcher(time_window_minutes=120)

# Match activities across sources
matched_activities = matcher.match_activities(raw_activities)
```

## Architecture Principles

### 1. **Atomicity** (REGULATION.md compliance)
- Each file has a single, well-defined purpose
- Functions are small, focused, and reusable
- Clear separation of concerns

### 2. **Modularity**
- **Core**: Essential business logic
- **Tools**: Utilities and specialized functionality
- **Prompts**: Centralized LLM prompt management

### 3. **Testability**
- Comprehensive test coverage
- Isolated test utilities
- Easy debugging and validation

### 4. **Extensibility**
- Plugin-style architecture for new data sources
- Configurable processing parameters
- Easy prompt customization

## Development

### Running Tests
```bash
# All agent tests
python -m pytest tests/backend/agent/ -v

# Specific functionality test
python src/backend/test_features/agent_tests/test_agent_capabilities.py

# Parser tests  
python -m pytest tests/backend/google_calendar_parser/ -v
```

### Adding New Features

1. **New Data Source**: Add parser in `parsers/new_source/`
2. **New Tools**: Add utility in `agent/tools/`
3. **New Prompts**: Add templates in `agent/prompts/`
4. **Tests**: Add tests in appropriate `test_features/` subdirectory

### Code Style
- Follow Google Python Style Guide
- Add comprehensive docstrings
- Include type hints
- Write focused, atomic functions

## API Reference

See individual module documentation:
- [Agent Core API](agent/core/__init__.py)
- [Tools API](agent/tools/__init__.py) 
- [Prompts API](agent/prompts/__init__.py)

## Support

For issues and feature requests, see the project's main documentation and issue tracker.