"""
API Authentication

Simple API key authentication for the SmartHistory API.
Future versions will implement JWT-based authentication.
"""

import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# API Key Authentication
class APIKeyAuth:
    """Simple API key authentication."""
    
    def __init__(self):
        # Load API keys from environment or use default for development
        self.api_keys = set()
        
        # Development API key (override with environment variable)
        dev_key = os.getenv('SMARTHISTORY_API_KEY', 'dev-key-12345')
        self.api_keys.add(dev_key)
        
        # Load additional keys from environment
        additional_keys = os.getenv('SMARTHISTORY_API_KEYS', '')
        if additional_keys:
            for key in additional_keys.split(','):
                key = key.strip()
                if key:
                    self.api_keys.add(key)
    
    def is_valid_key(self, api_key: str) -> bool:
        """Check if the API key is valid."""
        return api_key in self.api_keys
    
    def generate_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(32)


# Global instance
_api_key_auth = APIKeyAuth()

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


async def get_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> str:
    """
    Dependency to extract and validate API key from Authorization header.
    
    Usage in endpoints:
        @app.get("/protected")
        async def protected_endpoint(api_key: str = Depends(get_api_key)):
            return {"message": "Access granted"}
    """
    # For development, allow no authentication
    if os.getenv('SMARTHISTORY_ENV') == 'development':
        return 'dev-access'
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    
    if not _api_key_auth.is_valid_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key


async def get_optional_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> Optional[str]:
    """
    Optional API key dependency - doesn't raise error if missing.
    Useful for endpoints that have different behavior for authenticated vs anonymous users.
    """
    if not credentials:
        return None
    
    api_key = credentials.credentials
    
    if _api_key_auth.is_valid_key(api_key):
        return api_key
    
    return None


def require_api_key(func):
    """
    Decorator to require API key authentication for a function.
    
    Usage:
        @require_api_key
        async def my_function():
            return "Protected content"
    """
    async def wrapper(*args, **kwargs):
        # This is a simplified decorator - in practice, FastAPI dependencies are preferred
        return await func(*args, **kwargs)
    
    return wrapper


# Rate limiting helper (simple in-memory implementation)
class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}  # {api_key: [(timestamp, count), ...]}
        self.limits = {
            'default': (100, 60),      # 100 requests per 60 seconds
            'processing': (5, 60),     # 5 requests per 60 seconds
            'import': (2, 60)          # 2 requests per 60 seconds
        }
    
    def is_allowed(self, api_key: str, endpoint_type: str = 'default') -> bool:
        """Check if request is allowed under rate limits."""
        import time
        
        now = time.time()
        limit_requests, limit_seconds = self.limits.get(endpoint_type, self.limits['default'])
        
        # Clean old requests
        if api_key in self.requests:
            self.requests[api_key] = [
                (timestamp, count) for timestamp, count in self.requests[api_key]
                if now - timestamp < limit_seconds
            ]
        
        # Count recent requests
        if api_key not in self.requests:
            self.requests[api_key] = []
        
        recent_count = sum(count for _, count in self.requests[api_key])
        
        if recent_count >= limit_requests:
            return False
        
        # Add this request
        self.requests[api_key].append((now, 1))
        return True


# Global rate limiter
_rate_limiter = RateLimiter()


async def check_rate_limit(endpoint_type: str = 'default', api_key: str = Depends(get_api_key)) -> bool:
    """
    Dependency to check rate limits.
    
    Usage:
        @app.post("/process")
        async def process_data(
            rate_check: bool = Depends(lambda: check_rate_limit('processing')),
            api_key: str = Depends(get_api_key)
        ):
            return {"message": "Processing started"}
    """
    if not _rate_limiter.is_allowed(api_key, endpoint_type):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {endpoint_type} endpoints",
            headers={"Retry-After": "60"}
        )
    
    return True