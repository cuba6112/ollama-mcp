"""Configuration management for Ollama MCP Server"""
import os
import socket
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


def get_default_ollama_host() -> str:
    """
    Get default Ollama host based on environment.
    Uses localhost for local development, but tries to detect host IP for external access.
    """
    # If explicitly set via environment, use that
    if "OLLAMA_HOST" in os.environ:
        return os.environ["OLLAMA_HOST"]
    
    # Check if we can connect to localhost:11434 first (standard Ollama setup)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 11434))
        sock.close()
        if result == 0:
            return "http://localhost:11434"
    except:
        pass
    
    # If localhost doesn't work, try to find the local IP
    try:
        # Connect to a remote address to determine local IP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return f"http://{local_ip}:11434"
    except:
        # Fallback to localhost if all else fails
        return "http://localhost:11434"


class Settings(BaseSettings):
    """Server configuration settings"""
    
    # Ollama connection settings
    ollama_host: str = Field(
        default_factory=get_default_ollama_host,
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