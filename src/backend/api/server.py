"""
FastAPI Server Implementation

Main FastAPI application with all endpoints for the SmartHistory API.
Provides REST interface for frontend consumption of activity processing capabilities.
Industry-ready with dynamic configuration and deployment support.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from .models import *
from .services import ActivityService, TagService, InsightsService, ProcessingService, SystemService
from .dependencies import get_activity_service, get_tag_service, get_insights_service, get_processing_service, get_system_service
from .auth import get_api_key, get_optional_api_key, check_rate_limit
from config import get_config

# Get configuration
config = get_config()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting SmartHistory API in {config.ENVIRONMENT} mode")
    
    app = FastAPI(
        title=config.TITLE,
        description=config.DESCRIPTION,
        version=config.VERSION,
        docs_url="/docs" if config.DEBUG else None,
        redoc_url="/redoc" if config.DEBUG else None,
        debug=config.DEBUG
    )

    # Add security middleware for production
    if config.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=["*"]  # Configure this based on your domain
        )

    # Add CORS middleware with dynamic configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=config.CORS_CREDENTIALS,
        allow_methods=config.CORS_METHODS,
        allow_headers=config.CORS_HEADERS,
    )

    # Add error handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An internal server error occurred",
                "status_code": 500
            }
        )

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "SmartHistory API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs"
        }

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    # API v1 prefix from configuration
    API_V1_PREFIX = config.API_V1_PREFIX

    # Activities Endpoints
    @app.get(f"{API_V1_PREFIX}/activities/raw", response_model=PaginatedActivitiesResponse)
    async def get_raw_activities(
        source: Optional[str] = Query(None, pattern=r'^(notion|google_calendar)$'),
        date_start: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        date_end: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
        activity_service: ActivityService = Depends(get_activity_service)
    ):
        """Get raw activities with filtering and pagination."""
        return await activity_service.get_raw_activities(
            source=source,
            date_start=date_start,
            date_end=date_end,
            limit=limit,
            offset=offset
        )

    @app.get(f"{API_V1_PREFIX}/activities/processed", response_model=PaginatedProcessedActivitiesResponse)
    async def get_processed_activities(
        date_start: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        date_end: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        tags: Optional[str] = Query(None, description="Comma-separated tag names"),
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
        activity_service: ActivityService = Depends(get_activity_service)
    ):
        """Get processed activities with filtering and pagination."""
        tag_list = tags.split(',') if tags else None
        return await activity_service.get_processed_activities(
            date_start=date_start,
            date_end=date_end,
            tags=tag_list,
            limit=limit,
            offset=offset
        )

    # Insights Endpoints
    @app.get(f"{API_V1_PREFIX}/insights/overview", response_model=InsightsOverviewResponse)
    async def get_insights_overview(
        date_start: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        date_end: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        insights_service: InsightsService = Depends(get_insights_service)
    ):
        """Get activity insights overview."""
        return await insights_service.get_overview(date_start=date_start, date_end=date_end)

    @app.get(f"{API_V1_PREFIX}/insights/time-distribution", response_model=TimeDistributionResponse)
    async def get_time_distribution(
        date_start: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        date_end: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        group_by: str = Query(default='day', pattern=r'^(day|week|month)$'),
        insights_service: InsightsService = Depends(get_insights_service)
    ):
        """Get time distribution analysis."""
        return await insights_service.get_time_distribution(
            date_start=date_start,
            date_end=date_end,
            group_by=group_by
        )

    # Tags Endpoints
    @app.get(f"{API_V1_PREFIX}/tags", response_model=PaginatedTagsResponse)
    async def get_tags(
        sort_by: str = Query(default='usage_count', pattern=r'^(name|usage_count|created_at)$'),
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Get all tags with sorting and pagination."""
        return await tag_service.get_tags(sort_by=sort_by, limit=limit, offset=offset)

    @app.get(f"{API_V1_PREFIX}/tags/summary", response_model=TagSummaryResponse)
    async def get_tag_summary(
        start_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        end_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        limit: int = Query(default=20, ge=1, le=100),
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Get tag usage summary with counts."""
        return await tag_service.get_tag_summary(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

    @app.get(f"{API_V1_PREFIX}/tags/cooccurrence", response_model=TagCooccurrenceResponse)
    async def get_tag_cooccurrence(
        start_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        end_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        tags: Optional[str] = Query(None, description="Comma-separated tag names to analyze"),
        threshold: int = Query(default=2, ge=1, le=100),
        limit: int = Query(default=50, ge=1, le=200),
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Get tag co-occurrence analysis."""
        tag_list = tags.split(',') if tags else None
        return await tag_service.get_tag_cooccurrence(
            start_date=start_date,
            end_date=end_date,
            tags=tag_list,
            threshold=threshold,
            limit=limit
        )

    @app.get(f"{API_V1_PREFIX}/tags/transitions", response_model=TagTransitionResponse)
    async def get_tag_transitions(
        start_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        end_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        tags: Optional[str] = Query(None, description="Comma-separated tag names to analyze"),
        limit: int = Query(default=50, ge=1, le=200),
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Get tag transition patterns."""
        tag_list = tags.split(',') if tags else None
        return await tag_service.get_tag_transitions(
            start_date=start_date,
            end_date=end_date,
            tags=tag_list,
            limit=limit
        )

    @app.get(f"{API_V1_PREFIX}/tags/time-series", response_model=TagTimeSeriesResponse)
    async def get_tag_time_series(
        start_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        end_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$'),
        tags: Optional[str] = Query(None, description="Comma-separated tag names to analyze"),
        granularity: str = Query(default="day", pattern=r'^(hour|day)$'),
        mode: str = Query(default="absolute", pattern=r'^(absolute|normalized|share)$'),
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Get tag time series data."""
        tag_list = tags.split(',') if tags else None
        return await tag_service.get_tag_time_series(
            start_date=start_date,
            end_date=end_date,
            tags=tag_list,
            granularity=granularity,
            mode=mode
        )

    @app.get(f"{API_V1_PREFIX}/tags/relationships")
    async def get_top_tags_relationships(
        top_tags_limit: int = Query(default=5, ge=1, le=20),
        related_tags_limit: int = Query(default=5, ge=1, le=10),
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Get top tags with their co-occurring related tags."""
        return await tag_service.get_top_tags_with_relationships(
            top_tags_limit=top_tags_limit,
            related_tags_limit=related_tags_limit
        )

    @app.post(f"{API_V1_PREFIX}/tags", response_model=TagResponse)
    async def create_tag(
        tag_data: TagCreateRequest,
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Create a new tag."""
        return await tag_service.create_tag(tag_data)

    @app.get(f"{API_V1_PREFIX}/tags/{{tag_id}}", response_model=TagResponse)
    async def get_tag(
        tag_id: int,
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Get a specific tag by ID."""
        tag = await tag_service.get_tag_by_id(tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag

    @app.put(f"{API_V1_PREFIX}/tags/{{tag_id}}", response_model=TagResponse)
    async def update_tag(
        tag_id: int,
        tag_data: TagUpdateRequest,
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Update an existing tag."""
        tag = await tag_service.update_tag(tag_id, tag_data)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag

    @app.delete(f"{API_V1_PREFIX}/tags/{{tag_id}}")
    async def delete_tag(
        tag_id: int,
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Delete a tag."""
        success = await tag_service.delete_tag(tag_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tag not found")
        return {"message": "Tag deleted successfully"}

    # Processing Endpoints
    @app.post(f"{API_V1_PREFIX}/process/daily", response_model=ProcessingResponse)
    async def trigger_daily_processing(
        request: ProcessingRequest,
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Trigger daily activity processing."""
        return await processing_service.trigger_daily_processing(request)

    @app.get(f"{API_V1_PREFIX}/process/status/{{job_id}}", response_model=ProcessingStatus)
    async def get_processing_status(
        job_id: str,
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Get status of a processing job."""
        status = await processing_service.get_processing_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        return status

    @app.get(f"{API_V1_PREFIX}/process/history", response_model=List[ProcessingStatus])
    async def get_processing_history(
        limit: int = Query(default=50, ge=1, le=200),
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Get processing job history."""
        return await processing_service.get_processing_history(limit=limit)

    @app.get(f"{API_V1_PREFIX}/process/progress/{{job_id}}")
    async def get_processing_progress(
        job_id: str,
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Get real-time progress for a processing job."""
        return await processing_service.get_processing_progress(job_id)

    # Import Endpoints
    @app.post(f"{API_V1_PREFIX}/import/calendar")
    async def import_calendar_data(
        request: ImportRequest,
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Import data from Google Calendar parser."""
        return await processing_service.import_calendar_data(request)

    @app.post(f"{API_V1_PREFIX}/import/notion")
    async def import_notion_data(
        request: ImportRequest,
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Import data from Notion parser."""
        return await processing_service.import_notion_data(request)

    @app.get(f"{API_V1_PREFIX}/import/status")
    async def get_import_status(
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Get status of data imports."""
        return await processing_service.get_import_status()

    # Backfill endpoint
    @app.post(f"{API_V1_PREFIX}/management/backfill-calendar")
    async def backfill_calendar(
        months: int = Query(default=7, ge=1, le=24),
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Backfill last N months of calendar events."""
        return await processing_service.backfill_calendar(months=months)

    @app.post(f"{API_V1_PREFIX}/management/index-notion")
    async def index_notion(
        scope: str = Query(default='all', pattern=r'^(all|recent)$'),
        hours: int = Query(default=24, ge=1, le=2160),
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Generate abstracts + embeddings for Notion blocks (all or recent)."""
        return await processing_service.index_notion_blocks(scope=scope, hours=hours)

    @app.post(f"{API_V1_PREFIX}/management/reprocess-range")
    async def reprocess_range(
        date_start: str = Query(..., pattern=r'^\\d{4}-\\d{2}-\\d{2}$'),
        date_end: str = Query(..., pattern=r'^\\d{4}-\\d{2}-\\d{2}$'),
        regenerate_system_tags: bool = Query(default=False),
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Purge processed activities in date range and reprocess that window."""
        return await processing_service.reprocess_date_range(
            date_start=date_start, date_end=date_end, regenerate_system_tags=regenerate_system_tags
        )

    # Tag Management Endpoints
    @app.post(f"{API_V1_PREFIX}/tags/cleanup", response_model=TagCleanupResponse)
    async def cleanup_tags(
        request: TagCleanupRequest,
        tag_service: TagService = Depends(get_tag_service)
    ):
        """Clean up meaningless tags using AI analysis."""
        return await tag_service.cleanup_tags(request)

    @app.post(f"{API_V1_PREFIX}/taxonomy/build", response_model=TaxonomyBuildResponse)
    async def build_taxonomy(
        request: TaxonomyBuildRequest,
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Build AI-generated tag taxonomy and synonyms."""
        return await processing_service.build_taxonomy(request)

    @app.get(f"{API_V1_PREFIX}/processing/logs", response_model=ProcessingLogsResponse)
    async def get_processing_logs(
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
        level: Optional[str] = Query(None, pattern=r'^(DEBUG|INFO|WARN|ERROR)$'),
        source: Optional[str] = Query(None, description="Filter by log source"),
        processing_service: ProcessingService = Depends(get_processing_service)
    ):
        """Get processing logs with filtering and pagination."""
        return await processing_service.get_processing_logs(
            limit=limit, offset=offset, level=level, source=source
        )

    # System Endpoints
    @app.get(f"{API_V1_PREFIX}/system/health", response_model=SystemHealthResponse)
    async def get_system_health(
        system_service: SystemService = Depends(get_system_service)
    ):
        """Get system health status."""
        return await system_service.get_system_health()

    @app.get(f"{API_V1_PREFIX}/system/stats", response_model=SystemStatsResponse)
    async def get_system_stats(
        system_service: SystemService = Depends(get_system_service)
    ):
        """Get system statistics."""
        return await system_service.get_system_stats()

    # Retrieval endpoints
    @app.get(f"{API_V1_PREFIX}/retrieval/notion-context")
    async def retrieval_notion_context(
        query: str = Query(..., min_length=2),
        hours: int = Query(default=24, ge=1, le=2160),
        k: int = Query(default=5, ge=1, le=50),
        system_service: SystemService = Depends(get_system_service)
    ):
        """Retrieve top-K Notion contexts for a query within recent hours."""
        return await system_service.get_notion_context(query=query, hours=hours, k=k)

    @app.get(f"{API_V1_PREFIX}/retrieval/notion-context-by-date")
    async def retrieval_notion_context_by_date(
        query: str = Query(..., min_length=2),
        date: str = Query(..., pattern=r'^\\d{4}-\\d{2}-\\d{2}$'),
        windowDays: int = Query(default=1, ge=0, le=7),
        k: int = Query(default=5, ge=1, le=50),
        system_service: SystemService = Depends(get_system_service)
    ):
        """Retrieve top-K Notion contexts around the specified date."""
        return await system_service.get_notion_context_by_date(query=query, date=date, window_days=windowDays, k=k)

    # Configuration endpoints
    @app.post(f"{API_V1_PREFIX}/config/api", response_model=ApiConfigurationResponse)
    async def update_api_configuration(
        config_request: ApiConfigurationRequest,
        system_service: SystemService = Depends(get_system_service)
    ):
        """Update API configuration (API keys, models, etc.)."""
        return await system_service.update_api_configuration(config_request)

    @app.post(f"{API_V1_PREFIX}/config/test", response_model=TestApiConnectionResponse)
    async def test_api_connection(
        test_request: TestApiConnectionRequest,
        system_service: SystemService = Depends(get_system_service)
    ):
        """Test API connection with provided or configured credentials."""
        return await system_service.test_api_connection(test_request)

    return app


# Global app instance for external access
_app_instance = None

def get_api_app() -> FastAPI:
    """Get the FastAPI app instance (singleton)."""
    global _app_instance
    if _app_instance is None:
        _app_instance = create_app()
    return _app_instance


def run_server():
    """Run the server with configuration-based settings"""
    uvicorn.run(
        "api.server:get_api_app",
        factory=True,
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True,
    )


if __name__ == "__main__":
    run_server()
