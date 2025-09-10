"""
Configuration management for SmartHistory API
Handles environment-based configuration for different deployment scenarios
"""

import os
from typing import List, Optional


class APIConfig:
    """API Configuration with environment variable support"""
    
    def __init__(self):
        # Server Configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.RELOAD = os.getenv("RELOAD", "false").lower() == "true"
        
        # CORS Configuration
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:8080")
        self.CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',')]
        self.CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "false").lower() == "true"
        self.CORS_METHODS = ["*"]
        self.CORS_HEADERS = ["*"]
        
        # Database Configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smarthistory.db")
        self.DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        
        # API Configuration
        self.API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
        self.TITLE = os.getenv("API_TITLE", "SmartHistory API")
        self.DESCRIPTION = os.getenv("API_DESCRIPTION", "REST API for SmartHistory activity processing and analytics")
        self.VERSION = os.getenv("API_VERSION", "1.0.0")
        
        # Security
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Notion configuration
        # HISTORY_PAGE_ID: optional page ID for historical backfill anchoring
        self.NOTION_HISTORY_PAGE_ID = os.getenv("HISTORY_PAGE_ID")
        
        # Rate Limiting
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Processing
        self.MAX_PROCESSING_TIMEOUT = int(os.getenv("MAX_PROCESSING_TIMEOUT", "300"))
        self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
        
        # Cloud deployment settings
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class DevelopmentConfig(APIConfig):
    """Development environment configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.RELOAD = True
        self.LOG_LEVEL = "DEBUG"
        self.DATABASE_ECHO = True
        self.ENVIRONMENT = "development"


class ProductionConfig(APIConfig):
    """Production environment configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.RELOAD = False
        self.LOG_LEVEL = "INFO"
        self.DATABASE_ECHO = False
        self.ENVIRONMENT = "production"
        self.CORS_CREDENTIALS = True


class StagingConfig(APIConfig):
    """Staging environment configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.RELOAD = True
        self.LOG_LEVEL = "INFO"
        self.DATABASE_ECHO = False
        self.ENVIRONMENT = "staging"


def get_config() -> APIConfig:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "staging":
        return StagingConfig()
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config()
