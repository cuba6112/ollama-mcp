"""Configuration management for Ollama MCP Server"""
import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server configuration settings"""
    
    # Ollama connection settings
    ollama_host: str = Field(
        default="http://localhost:11434",
        env="OLLAMA_HOST",
        description="Ollama API base URL"
    )
    
    # Request settings
    request_timeout: float = Field(
        default=30.0,
        env="OLLAMA_REQUEST_TIMEOUT",
        description="Request timeout in seconds"
    )
    
    connection_timeout: float = Field(
        default=5.0,
        env="OLLAMA_CONNECTION_TIMEOUT",
        description="Connection timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        env="OLLAMA_MAX_RETRIES",
        description="Maximum number of retry attempts"
    )
    
    retry_delay: float = Field(
        default=1.0,
        env="OLLAMA_RETRY_DELAY",
        description="Initial retry delay in seconds"
    )
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        env="OLLAMA_LOG_LEVEL",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    log_requests: bool = Field(
        default=False,
        env="OLLAMA_LOG_REQUESTS",
        description="Log all API requests and responses"
    )
    
    # Performance settings
    enable_cache: bool = Field(
        default=True,
        env="OLLAMA_ENABLE_CACHE",
        description="Enable caching of model lists"
    )
    
    cache_ttl: int = Field(
        default=300,
        env="OLLAMA_CACHE_TTL",
        description="Cache TTL in seconds"
    )
    
    @field_validator("ollama_host")
    @classmethod
    def validate_ollama_host(cls, v: str) -> str:
        """Ensure Ollama host URL is properly formatted"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Ollama host must start with http:// or https://")
        return v.rstrip("/")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()