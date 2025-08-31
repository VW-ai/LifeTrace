# SmartHistory API Module

## Purpose

FastAPI-based REST API providing comprehensive access to SmartHistory's activity processing and analytics capabilities for frontend consumption.

## Architecture

### Database-First Design
- Direct integration with SQLite database layer
- No JSON intermediate files
- Real-time data access and processing

### Service Layer Pattern
- **Models**: Pydantic data models for request/response serialization
- **Services**: Business logic layer handling database operations and data transformation
- **Dependencies**: Dependency injection for service instances and database connections
- **Auth**: API key authentication with rate limiting

## Files & Responsibilities

### Core Components
- `server.py`: Main FastAPI application with all endpoint definitions
- `models.py`: Pydantic models for API contracts and data validation
- `services.py`: Business logic layer with database operations
- `dependencies.py`: Dependency injection for services and database connections
- `auth.py`: Authentication, authorization, and rate limiting

### Entry Points
- `__init__.py`: Module exports and factory functions
- `run_api.py`: Server runner script (project root level)

### Testing & Documentation
- `test_api.py`: Comprehensive API test suite
- `API_DESIGN.md`: Detailed API specification and documentation
- `api_META.md`: This file - module overview and architecture

## API Endpoints

### Activity Data
- `GET /api/v1/activities/raw` - Raw activities with filtering and pagination
- `GET /api/v1/activities/processed` - Processed activities with tag information

### Analytics & Insights
- `GET /api/v1/insights/overview` - Activity overview and statistics
- `GET /api/v1/insights/time-distribution` - Time-based analytics

### Tag Management
- `GET /api/v1/tags` - List all tags with sorting and pagination
- `POST /api/v1/tags` - Create new tags
- `PUT /api/v1/tags/{id}` - Update existing tags
- `DELETE /api/v1/tags/{id}` - Delete tags

### Processing & Imports
- `POST /api/v1/process/daily` - Trigger activity processing
- `GET /api/v1/process/status/{job_id}` - Check processing status
- `POST /api/v1/import/{source}` - Import data from parsers

### System Management
- `GET /api/v1/system/health` - System health check
- `GET /api/v1/system/stats` - System statistics

## Authentication

### Development Mode
- No authentication required when `SMARTHISTORY_ENV=development`
- Allows rapid frontend development and testing

### Production Mode
- API key authentication via `Authorization: Bearer <api-key>` header
- Rate limiting by endpoint type:
  - Standard endpoints: 100 requests/minute
  - Processing endpoints: 5 requests/minute  
  - Import endpoints: 2 requests/minute

### Configuration
- `SMARTHISTORY_API_KEY`: Primary API key
- `SMARTHISTORY_API_KEYS`: Comma-separated additional keys
- `SMARTHISTORY_ENV`: Environment mode (development/production)

## Data Flow

```
Frontend Request → FastAPI Router → Service Layer → Database Layer → Response
                     ↓
                 Authentication & Rate Limiting
                     ↓
                 Pydantic Validation
                     ↓
                 Business Logic Processing
```

## Testing

### Test Coverage
- All endpoint functionality
- Error handling and validation
- Authentication and rate limiting
- Database integration
- Response structure validation

### Running Tests
```bash
python src/backend/api/test_api.py
# or
pytest src/backend/api/test_api.py -v
```

## Performance Considerations

### Database Optimization
- Connection pooling via database layer
- Efficient queries with proper indexing
- Pagination to prevent large result sets

### Response Caching
- Service layer caching for expensive operations
- ETags for conditional requests (future enhancement)

### Async Operations
- FastAPI async/await pattern for I/O operations
- Non-blocking database queries and processing

## Error Handling

### Standard Error Format
```json
{
  "error": "ERROR_CODE",
  "message": "Human readable message",
  "status_code": 400
}
```

### Error Categories
- `VALIDATION_ERROR`: Invalid request parameters
- `NOT_FOUND`: Resource not found
- `DATABASE_ERROR`: Database operation failed
- `PROCESSING_ERROR`: Activity processing failed
- `RATE_LIMIT_EXCEEDED`: Too many requests

## Future Enhancements

### Security
- JWT-based authentication
- Role-based access control (RBAC)
- OAuth2 integration

### Features
- WebSocket endpoints for real-time updates
- GraphQL API alternative
- Bulk operations support
- Export capabilities (PDF, CSV)

### Performance
- Redis caching layer
- Background job processing with Celery
- API response compression
- CDN integration for static content

## Dependencies

### Core Requirements
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation and serialization

### Testing
- `pytest`: Test framework
- `httpx`: HTTP client for testing

### Security
- `python-jose`: JWT handling (future)
- `passlib`: Password hashing (future)

### Integration
- Direct integration with existing database and agent layers
- No additional external dependencies beyond Python ecosystem