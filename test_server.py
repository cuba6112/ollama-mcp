#!/usr/bin/env python3
"""Test script for Ollama MCP Server"""
import asyncio
import logging
from ollama_mcp_server.client import ollama_client

logging.basicConfig(level=logging.DEBUG)

async def test_connection():
    """Test basic connection to Ollama"""
    print("Testing Ollama connection...")
    
    # Test connection
    await ollama_client.connect()
    is_healthy = await ollama_client.health_check()
    
    if is_healthy:
        print("✅ Successfully connected to Ollama!")
        
        # Test listing models
        try:
            response = await ollama_client.get("/api/tags")
            print(f"✅ Found {len(response.get('models', []))} models")
        except Exception as e:
            print(f"❌ Failed to list models: {e}")
    else:
        print("❌ Failed to connect to Ollama. Make sure it's running!")
    
    await ollama_client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection())