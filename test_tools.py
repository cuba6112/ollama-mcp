#!/usr/bin/env python3
"""Test individual tool functions"""
import asyncio
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ollama_mcp_server.main import list_models, check_model_exists, show_model

async def test_tools():
    """Test some of the MCP tools directly"""
    print("Testing MCP tool functions...")
    
    # Test list_models
    print("\n1. Testing list_models:")
    models = await list_models()
    if "error" in models:
        print(f"❌ Error: {models['error']}")
    else:
        print(f"✅ Found {len(models['models'])} models")
        
    # Test check_model_exists
    print("\n2. Testing check_model_exists:")
    if "models" in models and models["models"]:
        test_model = models["models"][0]["name"]
        exists = await check_model_exists(test_model)
        if "error" in exists:
            print(f"❌ Error: {exists['error']}")
        else:
            print(f"✅ Model '{test_model}' exists: {exists['exists']}")
    
    # Test show_model
    print("\n3. Testing show_model:")
    if "models" in models and models["models"]:
        test_model = models["models"][0]["name"]
        info = await show_model(test_model)
        if "error" in info:
            print(f"❌ Error: {info['error']}")
        else:
            print(f"✅ Retrieved info for model '{test_model}'")

if __name__ == "__main__":
    asyncio.run(test_tools())