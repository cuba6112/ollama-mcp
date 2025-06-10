# Ollama MCP Server

An enhanced MCP server for interacting with the Ollama API, providing a robust bridge between Claude Desktop and locally-running LLMs via Ollama.

## Features

- ✅ **Complete Ollama API Coverage**: All major Ollama endpoints implemented
- 🔄 **Connection Pooling**: Efficient HTTP client with connection reuse
- 🚦 **Smart Retry Logic**: Automatic retries with exponential backoff
- 📝 **Comprehensive Logging**: Configurable logging for debugging
- ⚡ **Response Caching**: Intelligent caching for improved performance
- 🛡️ **Error Handling**: Graceful error handling with helpful messages
- ⚙️ **Flexible Configuration**: Environment variables and .env file support
- 🔍 **Type Safety**: Full Pydantic validation for requests/responses
- 📊 **Advanced Options**: Support for temperature, top_p, seed, and more
- 🌊 **Streaming Support**: Real-time token streaming for long responses

## Prerequisites

- Python 3.9+ installed.
- Ollama is installed and running on your local machine. You can download it from [ollama.com](https://ollama.com/).
- `uv` or `pip` is installed for package management.

## Installation

1.  **Navigate to the project directory:**

    ```bash
    cd /Users/mac_orion/mcp_server/ollama_mcp_server
    ```

2.  **Create a virtual environment:**

    Using `venv`:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**

    Using `pip`:
    ```bash
    pip install -e . 
    ```
    Or using `uv`:
    ```bash
    uv pip install -e .
    ```

## Running the Server

Once the dependencies are installed, you can run the server directly:

```bash
python -m ollama_mcp_server.main
```

Or use the mcp dev tool for development:

```bash
mcp dev ollama_mcp_server/main.py
```

## Claude Desktop Configuration

To use this server with the Claude Desktop app, you need to add it to your configuration file.

On macOS, edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ollama": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "ollama_mcp_server.main"],
      "cwd": "/Users/mac_orion/mcp_server/ollama_mcp_server"
    }
  }
}
```

Replace `/path/to/your/venv/bin/python` with the actual path to your Python executable.

## Available Tools

### Core Tools
- **`list_models`**: List all available Ollama models with size and modification info
- **`show_model`**: Get detailed information about a specific model
- **`check_model_exists`**: Check if a model exists locally

### Generation Tools
- **`generate_completion`**: Generate text completions with advanced options
  - Supports temperature, top_p, top_k, seed, num_predict, stop sequences
  - Streaming support for real-time responses
- **`generate_chat_completion`**: Generate chat responses with conversation history
  - Full message history support (system, user, assistant roles)
  - Same advanced options as completion
- **`generate_embeddings`**: Create embeddings for text (supports both single strings and lists)

### Model Management
- **`pull_model`**: Download models from the Ollama library
- **`copy_model`**: Duplicate a model with a new name
- **`delete_model`**: Remove models from local storage
- **`list_running_models`**: Show currently loaded models in memory

## Configuration

The server can be configured using environment variables or a `.env` file:

```bash
# Connection settings
OLLAMA_HOST=http://localhost:11434      # Ollama API URL
OLLAMA_REQUEST_TIMEOUT=30.0             # Request timeout in seconds
OLLAMA_CONNECTION_TIMEOUT=5.0           # Connection timeout in seconds
OLLAMA_MAX_RETRIES=3                    # Max retry attempts
OLLAMA_RETRY_DELAY=1.0                  # Initial retry delay

# Logging
OLLAMA_LOG_LEVEL=INFO                   # Log level (DEBUG, INFO, WARNING, ERROR)
OLLAMA_LOG_REQUESTS=false               # Log all API requests/responses

# Performance
OLLAMA_ENABLE_CACHE=true                # Enable response caching
OLLAMA_CACHE_TTL=300                    # Cache TTL in seconds
```

Copy `.env.example` to `.env` and customize as needed.

## Troubleshooting

### MCP Server Not Connecting
If Claude Desktop shows connection errors:

1. **Restart Claude Desktop** after making configuration changes
2. **Check Ollama is running**: `ollama ps` should show running models
3. **Verify Python path** in your Claude Desktop config is correct
4. **Check logs** by setting `OLLAMA_LOG_LEVEL=DEBUG` in your `.env` file

### Schema Mismatch Errors
If you see parameter-related errors:
1. Restart the MCP server completely
2. Restart Claude Desktop
3. Check that all dependencies are installed: `pip install -r requirements.txt`

### Connection to Ollama Fails
If the server can't connect to Ollama:
1. Ensure Ollama is running: `ollama serve`
2. Check the Ollama URL in your configuration
3. Try accessing Ollama directly: `curl http://localhost:11434/api/tags`

### Performance Issues
For better performance:
1. Enable caching: `OLLAMA_ENABLE_CACHE=true`
2. Adjust cache TTL: `OLLAMA_CACHE_TTL=600`
3. Increase timeout for large models: `OLLAMA_REQUEST_TIMEOUT=60`

## Testing

Test the server directly:
```bash
python test_tools.py
```

This will verify that all core functions work correctly with your Ollama installation.
