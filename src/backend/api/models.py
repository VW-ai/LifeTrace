"""
API Data Models

Pydantic models for request/response serialization in the SmartHistory API.
Provides clean separation between internal database models and API contracts.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


# Response Models
class TagResponse(BaseModel):
    """Tag information for API responses."""
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    usage_count: int = 0
    confidence: Optional[float] = None  # Only for activity-tag relationships
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RawActivityResponse(BaseModel):
    """Raw activity data for API responses."""
    id: int
    date: str
    time: Optional[str] = None
    duration_minutes: int
    details: str
    source: str
    orig_link: Optional[str] = None
    raw_data: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessedActivityResponse(BaseModel):
    """Processed activity data for API responses."""
    id: int
    date: str
    time: Optional[str] = None
    total_duration_minutes: int
    combined_details: str
    sources: List[str]
    tags: List[TagResponse] = []
    raw_activity_ids: List[int] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Pagination Models
class PageInfo(BaseModel):
    """Pagination information."""
    limit: int
    offset: int
    has_more: bool


class PaginatedResponse(BaseModel):
    """Base paginated response."""
    total_count: int
    page_info: PageInfo


class PaginatedActivitiesResponse(PaginatedResponse):
    """Paginated raw activities response."""
    activities: List[RawActivityResponse]


class PaginatedProcessedActivitiesResponse(PaginatedResponse):
    """Paginated processed activities response."""
    activities: List[ProcessedActivityResponse]


class PaginatedTagsResponse(PaginatedResponse):
    """Paginated tags response."""
    tags: List[TagResponse]


# Insights Models
class DateRange(BaseModel):
    """Date range information."""
    start: str
    end: str


class TopActivity(BaseModel):
    """Top activity by time."""
    tag: str
    hours: float


class InsightsOverviewResponse(BaseModel):
    """Activity insights overview."""
    total_tracked_hours: float
    activity_count: int
    unique_tags: int
    tag_time_distribution: Dict[str, int]  # tag -> minutes
    tag_percentages: Dict[str, float]  # tag -> percentage
    top_5_activities: List[TopActivity]
    date_range: DateRange


class TimeSeriesPoint(BaseModel):
    """Single point in time series data."""
    date: str
    total_minutes: int
    tag_breakdown: Dict[str, int]


class TimeDistributionSummary(BaseModel):
    """Time distribution summary statistics."""
    total_period_hours: float
    average_daily_hours: float
    most_productive_day: str


class TimeDistributionResponse(BaseModel):
    """Time distribution analysis."""
    time_series: List[TimeSeriesPoint]
    summary: TimeDistributionSummary


# Request Models
class TagCreateRequest(BaseModel):
    """Request to create a new tag."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, regex=r'^#[0-9a-fA-F]{6}$')

    @validator('name')
    def validate_name(cls, v):
        # Ensure tag name is lowercase and alphanumeric with dashes/underscores
        if not v.replace('-', '').replace('_', '').replace(' ', '').isalnum():
            raise ValueError('Tag name must be alphanumeric with dashes, underscores, or spaces')
        return v.lower().strip()


class TagUpdateRequest(TagCreateRequest):
    """Request to update an existing tag."""
    pass


class ProcessingRequest(BaseModel):
    """Request to trigger activity processing."""
    use_database: bool = True
    regenerate_system_tags: bool = False


class ImportRequest(BaseModel):
    """Request to import data from parsers."""
    hours_since_last_update: int = Field(default=168, ge=1, le=8760)  # 1 hour to 1 year


# Processing Response Models
class ProcessingCounts(BaseModel):
    """Processing operation counts."""
    raw_activities: int
    processed_activities: int


class TagAnalysis(BaseModel):
    """Tag generation analysis."""
    total_unique_tags: int
    average_tags_per_activity: float


class ProcessingResponse(BaseModel):
    """Response from processing operation."""
    status: str
    job_id: str
    processed_counts: ProcessingCounts
    tag_analysis: TagAnalysis


class ProcessingStatus(BaseModel):
    """Status of a processing job."""
    job_id: str
    status: str  # 'running', 'completed', 'failed'
    progress: Optional[float] = None  # 0.0 to 1.0
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# System Response Models
class DatabaseHealth(BaseModel):
    """Database health information."""
    connected: bool
    total_activities: int
    last_updated: datetime


class ServiceHealth(BaseModel):
    """Service health status."""
    tag_generator: str
    activity_matcher: str


class SystemHealthResponse(BaseModel):
    """System health overview."""
    status: str  # 'healthy', 'degraded', 'down'
    database: DatabaseHealth
    services: ServiceHealth


class SystemStatsResponse(BaseModel):
    """System statistics."""
    total_raw_activities: int
    total_processed_activities: int
    total_tags: int
    total_sessions: int
    database_size_mb: float
    last_processing_run: Optional[datetime] = None
    uptime_seconds: int


# Error Models
class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    status_code: int


# Query Parameter Models (for documentation)
class ActivityQueryParams(BaseModel):
    """Query parameters for activity endpoints."""
    source: Optional[str] = Field(None, regex=r'^(notion|google_calendar)$')
    date_start: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$')
    date_end: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$')
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ProcessedActivityQueryParams(ActivityQueryParams):
    """Query parameters for processed activity endpoints."""
    tags: Optional[str] = None  # Comma-separated tag names


class TagQueryParams(BaseModel):
    """Query parameters for tag endpoints."""
    sort_by: str = Field(default='usage_count', regex=r'^(name|usage_count|created_at)$')
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class InsightsQueryParams(BaseModel):
    """Query parameters for insights endpoints."""
    date_start: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$')
    date_end: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$')


class TimeDistributionQueryParams(InsightsQueryParams):
    """Query parameters for time distribution endpoints."""
    group_by: str = Field(default='day', regex=r'^(day|week|month)$')