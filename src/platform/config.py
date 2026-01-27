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
    
    # LLM (Gemini)
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
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
    RATE_LIMIT_PER_MINUTE: int = 30
    
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
