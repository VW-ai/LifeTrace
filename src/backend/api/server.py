"""
FastAPI Server Implementation

Main FastAPI application with all endpoints for the SmartHistory API.
Provides REST interface for frontend consumption of activity processing capabilities.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from .models import *
from .services import ActivityService, TagService, InsightsService, ProcessingService, SystemService
from .dependencies import get_activity_service, get_tag_service, get_insights_service, get_processing_service, get_system_service
from .auth import get_api_key, get_optional_api_key, check_rate_limit


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="SmartHistory API",
        description="REST API for SmartHistory activity processing and analytics",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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

    # API v1 prefix
    API_V1_PREFIX = "/api/v1"

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

    return app


# Global app instance for external access
_app_instance = None

def get_api_app() -> FastAPI:
    """Get the FastAPI app instance (singleton)."""
    global _app_instance
    if _app_instance is None:
        _app_instance = create_app()
    return _app_instance