"""Ollama MCP Server - Enhanced Bridge between MCP and Ollama API"""

__version__ = "0.2.0"

from .main import mcp
from .config import settings
from .client import OllamaClient, OllamaError, OllamaConnectionError, OllamaAPIError

__all__ = [
    "mcp",
    "settings",
    "OllamaClient",
    "OllamaError",
    "OllamaConnectionError",
    "OllamaAPIError",
]