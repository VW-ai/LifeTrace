# SmartHistory Backend Tests

Comprehensive test suite for the SmartHistory backend API and services.

## Running Tests

### Run All Tests
```bash
cd src/backend
pytest
```

### Run Specific Test Categories
```bash
# API endpoint tests
pytest tests/api/ -m api

# Service layer tests
pytest tests/services/ -m service

# Database tests
pytest tests/database/ -m database

# Integration tests
pytest tests/integration/ -m integration
```

### Run Specific Test Files
```bash
# Tag API comprehensive tests
pytest tests/api/test_tags_comprehensive.py -v

# Activity service tests
pytest tests/services/test_activity_service.py -v

# Insights service tests
pytest tests/services/test_insights_service.py -v
```

### Coverage Reports
```bash
# Run with coverage (already configured in pytest.ini)
pytest

# View HTML coverage report
open htmlcov/index.html
```

## Test Structure

### API Tests (`tests/api/`)
- **test_activities.py**: Raw and processed activity endpoints
- **test_tags.py**: Basic tag CRUD operations
- **test_tags_comprehensive.py**: Advanced tag analysis endpoints
- **test_insights.py**: Activity insights and analytics
- **test_processing.py**: Data processing endpoints
- **test_system.py**: System health and statistics

### Service Tests (`tests/services/`)
- **test_activity_service.py**: Activity service business logic
- **test_tag_service.py**: Tag service including analysis methods
- **test_insights_service.py**: Insights service calculations and analytics

### Key Features Tested

#### Tag Analysis Endpoints
- ✅ Tag summary with usage statistics
- ✅ Tag co-occurrence analysis
- ✅ Tag transition patterns
- ✅ Tag time series data
- ✅ Tag relationships and correlations

#### Activity Management
- ✅ Raw activity retrieval with filtering
- ✅ Processed activity aggregation
- ✅ Pagination and sorting
- ✅ Date range filtering
- ✅ Source filtering

#### Insights & Analytics
- ✅ Activity overview calculations
- ✅ Time distribution analysis
- ✅ Performance metrics
- ✅ Data consistency validation

#### CRUD Operations
- ✅ Create, read, update, delete for tags
- ✅ Data validation and error handling
- ✅ Duplicate prevention
- ✅ Constraint validation

## Test Data

Tests use isolated test databases with predefined data:
- Sample activities from multiple sources (Google Calendar, Notion)
- Test tags with various relationships
- Processed activities with tag associations
- Date ranges covering multiple scenarios

## Performance Benchmarks

Service methods include performance tests:
- Query response times < 2 seconds
- Memory usage optimization
- Large dataset handling
- Pagination efficiency

## CI/CD Integration

Tests are designed for automated pipelines:
- Fast execution (< 30 seconds total)
- No external dependencies
- Comprehensive coverage (>80% target)
- Clear pass/fail indicators
- Detailed error reporting

## Markers

Use pytest markers to run specific test categories:

```bash
pytest -m "api and not slow"     # Fast API tests only
pytest -m "service"              # Service layer tests
pytest -m "integration"          # Integration tests
pytest -m "slow"                 # Performance/slow tests
```

## Debugging Tests

### Verbose Output
```bash
pytest -v -s
```

### Run Single Test
```bash
pytest tests/api/test_tags_comprehensive.py::TestTagAnalysisEndpoints::test_get_tag_summary_basic -v
```

### Debug with PDB
```bash
pytest --pdb
```

## Test Configuration

Configuration is in `pytest.ini`:
- Test discovery patterns
- Coverage settings
- Warning filters
- Default arguments