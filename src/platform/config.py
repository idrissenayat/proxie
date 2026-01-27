"""
Configuration management for Proxie.

Loads settings from environment variables.
"""

import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://proxie_user:proxie_password@localhost:5432/proxie_db"
    
    # LLM (Gemini Legacy - will be replaced by LiteLLM)
    GOOGLE_API_KEY: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_DB: int = 0
    REDIS_CACHE_DB: int = 1
    REDIS_QUEUE_DB: int = 2
    
    # LLM (Target 2.0)
    LLM_PRIMARY_PROVIDER: str = "gemini"
    LLM_PRIMARY_MODEL: str = "gemini-2.0-flash"
    LLM_FALLBACK_PROVIDER: str = "anthropic"
    LLM_FALLBACK_MODEL: str = "claude-3-5-sonnet"
    LLM_CACHE_ENABLED: bool = True
    LLM_CACHE_TTL: int = 3600
    
    # Sentry & Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Auto-generate if not set
    API_KEY_HEADER: str = "X-API-Key"
    
    # CORS - Configurable origins
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"  # Comma-separated
    
    # MCP
    MCP_SERVER_NAME: str = "proxie"
    MCP_SERVER_VERSION: str = "0.1.0"
    MCP_API_KEY: str = secrets.token_urlsafe(24)  # Auto-generate if not set
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Features
    FEATURE_WEBSOCKET_ENABLED: bool = True
    FEATURE_LLM_CACHING_ENABLED: bool = True
    
    # Chat API Key (optional - if set, requires auth for /chat endpoint)
    CHAT_API_KEY: str = ""  # Empty means no auth required (for pilot)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
