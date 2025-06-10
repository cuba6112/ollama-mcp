#!/usr/bin/env python3
"""
Example usage of the Ollama MCP Server tools

This shows how the tools would be called from Claude Desktop
"""

# Example 1: List available models
list_models_example = {
    "tool": "list_models",
    "arguments": {}
}

# Example 2: Check if a model exists
check_model_example = {
    "tool": "check_model_exists",
    "arguments": {
        "name": "llama3.2:latest"
    }
}

# Example 3: Generate a simple completion
generate_completion_example = {
    "tool": "generate_completion",
    "arguments": {
        "model": "llama3.2:latest",
        "prompt": "Write a haiku about programming",
        "temperature": 0.7,
        "num_predict": 50
    }
}

# Example 4: Chat completion with history
chat_completion_example = {
    "tool": "generate_chat_completion",
    "arguments": {
        "model": "llama3.2:latest",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"},
            {"role": "assistant", "content": "Python is a high-level, interpreted programming language known for its simplicity and readability."},
            {"role": "user", "content": "Can you give me a simple example?"}
        ],
        "temperature": 0.5
    }
}

# Example 5: Generate embeddings
embeddings_example = {
    "tool": "generate_embeddings",
    "arguments": {
        "model": "nomic-embed-text",
        "prompt": ["Hello world", "How are you?"]
    }
}

# Example 6: Show model information
show_model_example = {
    "tool": "show_model",
    "arguments": {
        "name": "llama3.2:latest"
    }
}

# Example 7: List running models
list_running_example = {
    "tool": "list_running_models",
    "arguments": {}
}

# Example 8: Advanced generation with streaming
streaming_example = {
    "tool": "generate_completion",
    "arguments": {
        "model": "llama3.2:latest",
        "prompt": "Tell me a story about a robot",
        "temperature": 0.8,
        "top_p": 0.9,
        "seed": 42,
        "num_predict": 200,
        "stream": True,
        "stop": ["The end", "THE END"]
    }
}