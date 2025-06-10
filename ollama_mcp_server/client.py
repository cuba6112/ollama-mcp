"""HTTP client for Ollama API with connection pooling and retry logic"""
import asyncio
import logging
from typing import Dict, Any, Optional, TypeVar, Type
from contextlib import asynccontextmanager

import httpx
from pydantic import BaseModel

from .config import settings
from .models import ErrorResponse

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OllamaClient:
    """HTTP client for Ollama API with connection pooling"""
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._is_connected = False
        
    async def connect(self):
        """Initialize the HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=settings.ollama_host,
                timeout=httpx.Timeout(
                    connect=settings.connection_timeout,
                    read=settings.request_timeout,
                    write=settings.request_timeout,
                    pool=settings.connection_timeout
                ),
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                    keepalive_expiry=30
                )
            )
            logger.info(f"Connected to Ollama at {settings.ollama_host}")
            
    async def disconnect(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._is_connected = False
            logger.info("Disconnected from Ollama")
            
    async def health_check(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            if not self._client:
                await self.connect()
            response = await self._client.get("/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
            
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
        stream: bool = False
    ) -> Any:
        """Make HTTP request with retry logic"""
        if not self._client:
            await self.connect()
            
        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        retries = 0
        
        while retries <= settings.max_retries:
            try:
                if settings.log_requests:
                    logger.debug(f"{method} {url} - Data: {json_data}")
                
                if stream:
                    # Return the stream directly for streaming responses
                    return await self._client.stream(method, url, json=json_data)
                
                response = await self._client.request(method, url, json=json_data)
                
                if settings.log_requests:
                    logger.debug(f"Response {response.status_code}: {response.text[:200]}...")
                
                if response.status_code >= 400:
                    error_data = response.json()
                    error = ErrorResponse(**error_data) if isinstance(error_data, dict) else None
                    raise OllamaAPIError(
                        f"API error {response.status_code}",
                        status_code=response.status_code,
                        error_response=error
                    )
                
                data = response.json()
                
                if response_model:
                    return response_model(**data)
                return data
                
            except httpx.ConnectError as e:
                logger.error(f"Connection error: {e}")
                raise OllamaConnectionError(
                    "Cannot connect to Ollama. Is it running? "
                    f"Check: {settings.ollama_host}"
                )
                
            except httpx.TimeoutException as e:
                logger.error(f"Request timeout: {e}")
                if retries < settings.max_retries:
                    wait_time = settings.retry_delay * (2 ** retries)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    retries += 1
                else:
                    raise OllamaTimeoutError(f"Request timeout after {settings.max_retries} retries")
                    
            except Exception as e:
                if retries < settings.max_retries and not isinstance(e, (OllamaAPIError, OllamaConnectionError)):
                    wait_time = settings.retry_delay * (2 ** retries)
                    logger.warning(f"Request failed: {e}. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    retries += 1
                else:
                    raise
                    
    async def get(self, endpoint: str, response_model: Optional[Type[T]] = None) -> Any:
        """Make GET request"""
        return await self._request("GET", endpoint, response_model=response_model)
        
    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        response_model: Optional[Type[T]] = None,
        stream: bool = False
    ) -> Any:
        """Make POST request"""
        return await self._request("POST", endpoint, json_data, response_model, stream)
        
    async def delete(self, endpoint: str, json_data: Dict[str, Any]) -> Any:
        """Make DELETE request"""
        return await self._request("DELETE", endpoint, json_data)


# Global client instance
ollama_client = OllamaClient()


@asynccontextmanager
async def get_ollama_client():
    """Context manager for Ollama client"""
    try:
        await ollama_client.connect()
        yield ollama_client
    finally:
        # Don't disconnect here to maintain connection pooling
        pass


# Custom exceptions
class OllamaError(Exception):
    """Base exception for Ollama errors"""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when cannot connect to Ollama"""
    pass


class OllamaTimeoutError(OllamaError):
    """Raised when request times out"""
    pass


class OllamaAPIError(OllamaError):
    """Raised when API returns an error"""
    def __init__(self, message: str, status_code: int, error_response: Optional[ErrorResponse] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_response = error_response