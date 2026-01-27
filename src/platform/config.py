"""
Configuration management for Proxie.

Loads settings from environment variables.
"""

import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Any, Dict, Optional
from pydantic import model_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    GCP_SECRETS_ENABLED: bool = False
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://proxie_user:proxie_password@localhost:5432/proxie_db"
    
    # LLM (Gemini Legacy - will be replaced by LiteLLM)
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_DB: int = 0
    REDIS_CACHE_DB: int = 1
    REDIS_QUEUE_DB: int = 2
    
    # Celery
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"{self.REDIS_URL.rsplit('/', 1)[0]}/{self.REDIS_QUEUE_DB}"
    
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"{self.REDIS_URL.rsplit('/', 1)[0]}/{self.REDIS_QUEUE_DB}"
    
    # LLM (Target 2.0)
    LLM_PRIMARY_PROVIDER: str = "gemini"
    LLM_PRIMARY_MODEL: str = "gemini-2.0-flash"
    LLM_FALLBACK_PROVIDER: str = "anthropic"
    LLM_FALLBACK_MODEL: str = "claude-3-5-sonnet"
    LLM_CACHE_ENABLED: bool = True
    LLM_CACHE_TTL: int = 3600
    
    # Worker
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
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
    
    # Clerk
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    
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
    
    @model_validator(mode='after')
    def load_gcp_secrets(self) -> 'Settings':
        """Fetch secrets from Google Cloud Secret Manager if enabled."""
        if not self.GCP_SECRETS_ENABLED:
            return self
            
        from src.platform.secrets import get_secret
        
        # List of keys that should be fetched from Secret Manager in production
        secret_keys = [
            "GOOGLE_API_KEY",
            "ANTHROPIC_API_KEY",
            "CLERK_SECRET_KEY",
            "CLERK_PUBLISHABLE_KEY",
            "DATABASE_URL",
            "SENTRY_DSN",
            "REDIS_URL"
        ]
        
        for key in secret_keys:
            val = get_secret(key)
            if val:
                setattr(self, key, val)
                
        return self

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
