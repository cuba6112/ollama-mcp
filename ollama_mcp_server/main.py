#!/usr/bin/env python3
"""
Ollama MCP Server - Enhanced Bridge between MCP and Ollama API
"""
import logging
import sys
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from .config import settings
from .client import ollama_client, OllamaError, OllamaConnectionError, OllamaAPIError
from .cache import cache, cached
from .models import (
    GenerateOptions, Message, ModelInfo, ModelListResponse,
    GenerateResponse, ChatResponse, EmbeddingsResponse,
    ProcessListResponse, ModelDetails
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(server):
    """Lifecycle management for the server"""
    logger.info("Starting Ollama MCP Server...")
    
    # Initialize HTTP client
    await ollama_client.connect()
    
    # Check Ollama connectivity
    if not await ollama_client.health_check():
        logger.warning(
            f"Cannot connect to Ollama at {settings.ollama_host}. "
            "Server will start but some operations may fail."
        )
    else:
        logger.info(f"Successfully connected to Ollama at {settings.ollama_host}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Ollama MCP Server...")
    await cache.clear()
    await ollama_client.disconnect()


# Create the MCP server with lifespan
mcp = FastMCP("ollama-mcp-server", lifespan=lifespan)


@mcp.tool()
async def list_models() -> Dict[str, Any]:
    """List all available Ollama models"""
    try:
        logger.debug("Listing models")
        # Try to get from cache first
        if settings.enable_cache:
            cache_key = "models:list_models"
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
        
        response = await ollama_client.get("/api/tags", response_model=ModelListResponse)
        
        # Convert to dict for JSON serialization
        result = {
            "models": [
                {
                    "name": model.name,
                    "size": model.size,
                    "modified_at": model.modified_at.isoformat() if model.modified_at else None,
                    "digest": model.digest
                }
                for model in response.models
            ]
        }
        
        # Cache the result
        if settings.enable_cache:
            await cache.set(cache_key, result, 300)
            logger.debug(f"Cached result for {cache_key}")
        
        return result
    except OllamaConnectionError as e:
        logger.error(f"Connection error in list_models: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except Exception as e:
        logger.exception("Unexpected error in list_models")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def show_model(name: str) -> Dict[str, Any]:
    """Show detailed information about a specific model"""
    try:
        logger.debug(f"Showing model info for: {name}")
        response = await ollama_client.post("/api/show", {"name": name})
        return response
    except OllamaConnectionError as e:
        logger.error(f"Connection error in show_model: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except OllamaAPIError as e:
        logger.error(f"API error in show_model: {e}")
        return {
            "error": "Ollama API error",
            "details": str(e),
            "status_code": e.status_code
        }
    except Exception as e:
        logger.exception("Unexpected error in show_model")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def generate_completion(
    model: str,
    prompt: str,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    seed: Optional[int] = None,
    num_predict: Optional[int] = None,
    stop: Optional[List[str]] = None,
    stream: bool = False
) -> Dict[str, Any]:
    """Generate a completion from a model with advanced options"""
    try:
        logger.debug(f"Generating completion with model: {model}")
        
        # Build options
        options = GenerateOptions(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            seed=seed,
            num_predict=num_predict,
            stop=stop
        ).dict(exclude_none=True)
        
        request_data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if options:
            request_data["options"] = options
        
        if stream:
            # For streaming, we'll collect all chunks and return the complete response
            # In a real implementation, you might want to yield chunks
            logger.info("Streaming response requested, collecting chunks...")
            full_response = ""
            
            async with await ollama_client.post("/api/generate", request_data, stream=True) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        chunk = json.loads(line)
                        if "response" in chunk:
                            full_response += chunk["response"]
                        if chunk.get("done", False):
                            # Return the final chunk with accumulated response
                            chunk["response"] = full_response
                            return chunk
        else:
            response = await ollama_client.post(
                "/api/generate",
                request_data,
                response_model=GenerateResponse
            )
            return response.dict()
    except OllamaConnectionError as e:
        logger.error(f"Connection error in generate_completion: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except OllamaAPIError as e:
        logger.error(f"API error in generate_completion: {e}")
        return {
            "error": "Ollama API error",
            "details": str(e),
            "status_code": e.status_code
        }
    except ValidationError as e:
        logger.error(f"Validation error in generate_completion: {e}")
        return {
            "error": "Invalid parameters",
            "details": e.errors()
        }
    except Exception as e:
        logger.exception("Unexpected error in generate_completion")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def generate_chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    seed: Optional[int] = None,
    num_predict: Optional[int] = None,
    stop: Optional[List[str]] = None,
    stream: bool = False
) -> Dict[str, Any]:
    """Generate a chat completion from a model with conversation history"""
    try:
        logger.debug(f"Generating chat completion with model: {model}")
        
        # Validate messages
        validated_messages = []
        for msg in messages:
            validated_messages.append(Message(**msg))
        
        # Build options
        options = GenerateOptions(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            seed=seed,
            num_predict=num_predict,
            stop=stop
        ).dict(exclude_none=True)
        
        request_data = {
            "model": model,
            "messages": [msg.dict() for msg in validated_messages],
            "stream": stream
        }
        
        if options:
            request_data["options"] = options
        
        if stream:
            logger.info("Streaming chat response requested, collecting chunks...")
            full_response = ""
            role = None
            
            async with await ollama_client.post("/api/chat", request_data, stream=True) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            full_response += chunk["message"]["content"]
                            role = chunk["message"].get("role", "assistant")
                        if chunk.get("done", False):
                            # Return the final chunk with accumulated message
                            chunk["message"] = {"role": role, "content": full_response}
                            return chunk
        else:
            response = await ollama_client.post(
                "/api/chat",
                request_data,
                response_model=ChatResponse
            )
            return response.dict()
    except OllamaConnectionError as e:
        logger.error(f"Connection error in generate_chat_completion: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except OllamaAPIError as e:
        logger.error(f"API error in generate_chat_completion: {e}")
        return {
            "error": "Ollama API error",
            "details": str(e),
            "status_code": e.status_code
        }
    except ValidationError as e:
        logger.error(f"Validation error in generate_chat_completion: {e}")
        return {
            "error": "Invalid parameters",
            "details": e.errors()
        }
    except Exception as e:
        logger.exception("Unexpected error in generate_chat_completion")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def generate_embeddings(
    model: str,
    prompt: Union[str, List[str]]
) -> Dict[str, Any]:
    """Generate embeddings for text using a model. Supports both single strings and lists of strings."""
    try:
        logger.debug(f"Generating embeddings with model: {model}")
        
        # Handle both single strings and lists of strings
        if isinstance(prompt, list):
            # Process each prompt separately since Ollama doesn't support batch requests
            all_embeddings = []
            for single_prompt in prompt:
                request_data = {
                    "model": model,
                    "prompt": single_prompt
                }
                
                response = await ollama_client.post(
                    "/api/embeddings",
                    request_data,
                    response_model=EmbeddingsResponse
                )
                
                embeddings = response.get_embeddings()
                all_embeddings.extend(embeddings)
            
            result = {
                "model": model,
                "embeddings": all_embeddings
            }
        else:
            # Single string prompt
            request_data = {
                "model": model,
                "prompt": prompt
            }
            
            response = await ollama_client.post(
                "/api/embeddings",
                request_data,
                response_model=EmbeddingsResponse
            )
            
            result = {
                "model": response.model or model,
                "embeddings": response.get_embeddings()
            }
        
        return result
    except OllamaConnectionError as e:
        logger.error(f"Connection error in generate_embeddings: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except OllamaAPIError as e:
        logger.error(f"API error in generate_embeddings: {e}")
        return {
            "error": "Ollama API error",
            "details": str(e),
            "status_code": e.status_code
        }
    except Exception as e:
        logger.exception("Unexpected error in generate_embeddings")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def pull_model(name: str, insecure: bool = False) -> Dict[str, Any]:
    """Pull a model from the Ollama library"""
    try:
        logger.info(f"Pulling model: {name}")
        
        # Clear model cache since we're adding a new model
        await cache.delete("models:list_models")
        
        request_data = {
            "name": name,
            "insecure": insecure
        }
        
        # This is a long-running operation
        response = await ollama_client.post("/api/pull", request_data)
        return response
    except OllamaConnectionError as e:
        logger.error(f"Connection error in pull_model: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except Exception as e:
        logger.exception("Unexpected error in pull_model")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def copy_model(source: str, destination: str) -> Dict[str, Any]:
    """Copy a model to a new name"""
    try:
        logger.info(f"Copying model from {source} to {destination}")
        
        # Clear model cache since we're modifying models
        await cache.delete("models:list_models")
        
        request_data = {
            "source": source,
            "destination": destination
        }
        
        response = await ollama_client.post("/api/copy", request_data)
        return {"success": True, "message": f"Model copied from {source} to {destination}"}
    except OllamaConnectionError as e:
        logger.error(f"Connection error in copy_model: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except OllamaAPIError as e:
        logger.error(f"API error in copy_model: {e}")
        return {
            "error": "Ollama API error",
            "details": str(e),
            "status_code": e.status_code
        }
    except Exception as e:
        logger.exception("Unexpected error in copy_model")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def delete_model(name: str) -> Dict[str, Any]:
    """Delete a model from local storage"""
    try:
        logger.warning(f"Deleting model: {name}")
        
        # Clear model cache since we're removing a model
        await cache.delete("models:list_models")
        
        response = await ollama_client.delete("/api/delete", {"name": name})
        return {"success": True, "message": f"Model {name} deleted successfully"}
    except OllamaConnectionError as e:
        logger.error(f"Connection error in delete_model: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except OllamaAPIError as e:
        logger.error(f"API error in delete_model: {e}")
        return {
            "error": "Ollama API error",
            "details": str(e),
            "status_code": e.status_code
        }
    except Exception as e:
        logger.exception("Unexpected error in delete_model")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def list_running_models() -> Dict[str, Any]:
    """List currently running/loaded models"""
    try:
        logger.debug("Listing running models")
        
        # Try to get from cache first
        if settings.enable_cache:
            cache_key = "running_models:list_running_models"
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
        
        response = await ollama_client.get("/api/ps", response_model=ProcessListResponse)
        
        result = {
            "models": [
                {
                    "name": model.name,
                    "model": model.model,
                    "size": model.size,
                    "digest": model.digest,
                    "expires_at": model.expires_at.isoformat()
                }
                for model in response.models
            ]
        }
        
        # Cache the result with shorter TTL
        if settings.enable_cache:
            await cache.set(cache_key, result, 30)
            logger.debug(f"Cached result for {cache_key}")
        
        return result
    except OllamaConnectionError as e:
        logger.error(f"Connection error in list_running_models: {e}")
        return {
            "error": "Cannot connect to Ollama",
            "details": str(e),
            "suggestion": f"Ensure Ollama is running at {settings.ollama_host}"
        }
    except Exception as e:
        logger.exception("Unexpected error in list_running_models")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


@mcp.tool()
async def check_model_exists(name: str) -> Dict[str, Any]:
    """Check if a model exists locally"""
    try:
        models_response = await list_models()
        
        if "error" in models_response:
            return models_response
        
        model_names = [m["name"] for m in models_response["models"]]
        exists = name in model_names
        
        return {
            "exists": exists,
            "model": name,
            "message": f"Model '{name}' {'exists' if exists else 'does not exist'} locally"
        }
    except Exception as e:
        logger.exception("Unexpected error in check_model_exists")
        return {
            "error": "Internal server error",
            "details": str(e)
        }


if __name__ == "__main__":
    # Run the MCP server
    logger.info(f"Starting Ollama MCP Server with log level: {settings.log_level}")
    logger.info(f"Ollama host: {settings.ollama_host}")
    mcp.run()