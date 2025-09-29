"""
SmartHistory REST API package

Note: Avoid importing the FastAPI app at package import time to prevent
heavy dependencies from loading in contexts that only need service-layer
utilities. Use lazy imports in the accessors below.
"""

from typing import Any

__all__ = ['create_app', 'get_api_app']


def create_app() -> Any:
    from .server import create_app as _create
    return _create()


def get_api_app() -> Any:
    from .server import get_api_app as _get
    return _get()
