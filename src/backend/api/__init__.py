"""
SmartHistory REST API

FastAPI-based REST API providing access to SmartHistory's activity processing
and analytics capabilities for frontend consumption.
"""

from .server import create_app, get_api_app

__all__ = ['create_app', 'get_api_app']