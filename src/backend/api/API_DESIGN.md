# SmartHistory REST API Design

## Overview

REST API for SmartHistory frontend consumption, providing access to processed activity data, insights, and system management functionality. Built on database-first architecture with FastAPI.

## Base URL
```
http://localhost:8000/api/v1
```

## API Endpoints

### 1. Activities Endpoints

#### Get Raw Activities
```http
GET /activities/raw
```
**Query Parameters:**
- `source` (optional): Filter by source (`notion`, `google_calendar`)
- `date_start` (optional): Start date (YYYY-MM-DD)
- `date_end` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Max results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "activities": [
    {
      "id": 1,
      "date": "2025-08-31",
      "time": "09:00",
      "duration_minutes": 60,
      "details": "Team standup meeting",
      "source": "google_calendar",
      "orig_link": "https://calendar.google.com/...",
      "raw_data": {...}
    }
  ],
  "total_count": 150,
  "page_info": {
    "limit": 100,
    "offset": 0,
    "has_more": true
  }
}
```

#### Get Processed Activities
```http
GET /activities/processed
```
**Query Parameters:**
- `date_start`, `date_end`, `limit`, `offset` (same as raw)
- `tags` (optional): Comma-separated tag filter

**Response:**
```json
{
  "activities": [
    {
      "id": 1,
      "date": "2025-08-31",
      "time": "09:00",
      "total_duration_minutes": 60,
      "combined_details": "Team standup and project planning",
      "sources": ["google_calendar", "notion"],
      "tags": [
        {
          "name": "meetings",
          "confidence": 0.95,
          "color": "#4285f4"
        }
      ],
      "raw_activity_ids": [1, 2, 5]
    }
  ],
  "total_count": 75,
  "page_info": {
    "limit": 100,
    "offset": 0,
    "has_more": false
  }
}
```

### 2. Insights Endpoints

#### Get Activity Insights
```http
GET /insights/overview
```
**Query Parameters:**
- `date_start`, `date_end` (optional): Date range for analysis

**Response:**
```json
{
  "total_tracked_hours": 42.5,
  "activity_count": 156,
  "unique_tags": 12,
  "tag_time_distribution": {
    "work": 1800,
    "meetings": 720,
    "development": 960
  },
  "tag_percentages": {
    "work": 42.1,
    "meetings": 16.8,
    "development": 22.4
  },
  "top_5_activities": [
    {
      "tag": "development",
      "hours": 16.0
    }
  ],
  "date_range": {
    "start": "2025-08-24",
    "end": "2025-08-31"
  }
}
```

#### Get Time Distribution
```http
GET /insights/time-distribution
```
**Query Parameters:**
- `date_start`, `date_end` (optional)
- `group_by`: `day`, `week`, `month` (default: `day`)

**Response:**
```json
{
  "time_series": [
    {
      "date": "2025-08-31",
      "total_minutes": 480,
      "tag_breakdown": {
        "work": 360,
        "meetings": 120
      }
    }
  ],
  "summary": {
    "total_period_hours": 42.5,
    "average_daily_hours": 6.1,
    "most_productive_day": "2025-08-29"
  }
}
```

### 3. Tags Endpoints

#### Get All Tags
```http
GET /tags
```
**Query Parameters:**
- `sort_by`: `name`, `usage_count`, `created_at` (default: `usage_count`)
- `limit`, `offset` (pagination)

**Response:**
```json
{
  "tags": [
    {
      "id": 1,
      "name": "development",
      "description": "Software development activities",
      "color": "#34a853",
      "usage_count": 45,
      "created_at": "2025-08-31T10:00:00Z",
      "updated_at": "2025-08-31T15:30:00Z"
    }
  ],
  "total_count": 12
}
```

#### Create/Update Tag
```http
POST /tags
PUT /tags/{tag_id}
```
**Request Body:**
```json
{
  "name": "new-tag",
  "description": "Description of the tag",
  "color": "#ff6d01"
}
```

#### Delete Tag
```http
DELETE /tags/{tag_id}
```

### 4. Processing Endpoints

#### Trigger Data Processing
```http
POST /process/daily
```
**Request Body:**
```json
{
  "use_database": true,
  "regenerate_system_tags": false
}
```

**Response:**
```json
{
  "status": "success",
  "job_id": "proc_20250831_001",
  "processed_counts": {
    "raw_activities": 200,
    "processed_activities": 75
  },
  "tag_analysis": {
    "total_unique_tags": 12,
    "average_tags_per_activity": 2.3
  }
}
```

#### Get Processing Status
```http
GET /process/status/{job_id}
```

#### Get Processing History
```http
GET /process/history
```

### 5. Data Import Endpoints

#### Import from Parsers
```http
POST /import/calendar
POST /import/notion
```
**Request Body:**
```json
{
  "hours_since_last_update": 168
}
```

#### Get Import Status
```http
GET /import/status
```

### 6. System Endpoints

#### Get System Health
```http
GET /system/health
```
**Response:**
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "total_activities": 350,
    "last_updated": "2025-08-31T15:30:00Z"
  },
  "services": {
    "tag_generator": "operational",
    "activity_matcher": "operational"
  }
}
```

#### Get System Statistics
```http
GET /system/stats
```

## Data Models

### Activity Model
```python
class RawActivityResponse(BaseModel):
    id: int
    date: str
    time: Optional[str]
    duration_minutes: int
    details: str
    source: str
    orig_link: Optional[str]
    raw_data: Dict[str, Any]
    created_at: datetime
```

### Processed Activity Model
```python
class ProcessedActivityResponse(BaseModel):
    id: int
    date: str
    time: Optional[str]
    total_duration_minutes: int
    combined_details: str
    sources: List[str]
    tags: List[TagResponse]
    raw_activity_ids: List[int]
    created_at: datetime
```

### Tag Model
```python
class TagResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    usage_count: int
    confidence: Optional[float]  # Only for activity-tag relationships
    created_at: datetime
    updated_at: datetime
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid date format",
    "details": {
      "field": "date_start",
      "received": "2025-13-01",
      "expected": "YYYY-MM-DD format"
    }
  }
}
```

### Error Codes
- `VALIDATION_ERROR`: Invalid request parameters
- `NOT_FOUND`: Resource not found
- `DATABASE_ERROR`: Database operation failed
- `PROCESSING_ERROR`: Activity processing failed
- `IMPORT_ERROR`: Data import failed

## Authentication & Security

### API Key Authentication (Phase 1)
```http
Authorization: Bearer your-api-key
```

### Future: JWT Authentication (Phase 2)
```http
Authorization: Bearer jwt-token
```

## Rate Limiting

- **Standard endpoints**: 100 requests/minute
- **Processing endpoints**: 5 requests/minute
- **Import endpoints**: 2 requests/minute

## Versioning

API versioned through URL path: `/api/v1/`
- Backward compatibility maintained within major versions
- Breaking changes require new major version