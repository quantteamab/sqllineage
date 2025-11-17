"""Application configuration using Pydantic Settings."""

import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service configuration
    service_name: str = "sqllineage-api"
    service_version: str = "1.0.0"
    service_port: int = 8000
    service_host: str = "0.0.0.0"

    # Logging configuration
    log_level: str = "INFO"
    log_file: str = "/app/logs/sqllineage-api.log"
    log_format: str = "json"  # json or text

    # OpenMetadata configuration
    openmetadata_url: Optional[str] = None
    openmetadata_api_key: Optional[str] = None
    openmetadata_timeout: int = 10  # seconds
    openmetadata_cache_ttl: int = 300  # 5 minutes cache

    # Request limits
    max_request_size_mb: int = 50
    rate_limit_rpm: int = 100  # requests per minute
    request_timeout_sec: int = 30

    # Default SQL dialect
    default_dialect: str = "ansi"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def openmetadata_configured(self) -> bool:
        """Check if OpenMetadata is properly configured."""
        return bool(self.openmetadata_url and self.openmetadata_api_key)

    @property
    def max_request_size_bytes(self) -> int:
        """Get max request size in bytes."""
        return self.max_request_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()
