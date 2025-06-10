# Ollama MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.4+-green.svg)](https://modelcontextprotocol.io/)

An enhanced MCP (Model Context Protocol) server for interacting with the Ollama API, providing a robust bridge between Claude Desktop and locally-running LLMs via Ollama.

## Features

- ✅ **Complete Ollama API Coverage**: All major Ollama endpoints implemented
- 🔄 **Connection Pooling**: Efficient HTTP client with connection reuse
- 🚦 **Smart Retry Logic**: Automatic retries with exponential backoff
- 📝 **Comprehensive Logging**: Configurable logging for debugging
- ⚡ **Response Caching**: Intelligent caching for improved performance
- 🛡️ **Error Handling**: Graceful error handling with helpful messages
- ⚙️ **Flexible Configuration**: Environment variables and .env file support
- 🌐 **Smart Host Detection**: Automatically detects localhost vs external network access
- 🔍 **Type Safety**: Full Pydantic validation for requests/responses
- 📊 **Advanced Options**: Support for temperature, top_p, seed, and more
- 🌊 **Streaming Support**: Real-time token streaming for long responses

## Quick Start

<details>
<summary><strong>macOS Instructions</strong></summary>

1.  **Install Ollama** and ensure it's running:
    ```bash
    # Download from https://ollama.com or use:
    curl -fsSL https://ollama.com/install.sh | sh
    ollama serve
    ```

2.  **Install the MCP server**:
    ```bash
    git clone https://github.com/cuba6112/ollama-mcp.git
    cd ollama-mcp
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Claude Desktop** by adding to your config file:
    ```json
    {
      "mcpServers": {
        "ollama": {
          "command": "/Users/mac_orion/mcp_server/ollama_mcp_server/venv/bin/python",
          "args": ["-m", "ollama_mcp_server.main"],
          "cwd": "/Users/mac_orion/mcp_server/ollama_mcp_server"
        }
      }
    }
    ```

4.  **Restart Claude Desktop** and start using Ollama models!

</details>

## Smithery Integration

<details>
<summary><strong>Using with Smithery</strong></summary>

[Smithery](https://smithery.ai/) provides a convenient way to install and manage MCP servers. The Ollama MCP server includes automatic network detection to work seamlessly with external tools like Smithery.

### Installation via Smithery

```bash
npx -y @smithery/cli@latest install @cuba6112/ollama-mcp --client windsurf --key YOUR_KEY
```

### Network Configuration

The server automatically detects the appropriate Ollama host:

1. **Local Development**: Uses `http://localhost:11434` when Ollama is accessible locally
2. **External Access**: Automatically detects your local network IP (e.g., `http://192.168.1.100:11434`) when localhost is not accessible
3. **Manual Override**: Set `OLLAMA_HOST` environment variable for custom configurations

### Ensuring Ollama External Access

For Smithery and other external tools to connect to your local Ollama instance:

1. **Start Ollama with external binding**:
   ```bash
   ollama serve --host 0.0.0.0
   ```

2. **Or set environment variable**:
   ```bash
   export OLLAMA_HOST=0.0.0.0
   ollama serve
   ```

3. **Verify connectivity**:
   ```bash
   # Test from another machine or tool
   curl http://YOUR_LOCAL_IP:11434/api/tags
   ```

### Troubleshooting Smithery Connection

If Smithery cannot connect to your Ollama instance:

1. **Check Ollama is accepting external connections**: `ollama serve --host 0.0.0.0`
2. **Verify firewall settings**: Ensure port 11434 is not blocked
3. **Test network connectivity**: Try accessing `http://YOUR_LOCAL_IP:11434` from another device
4. **Check server logs**: Set `OLLAMA_LOG_LEVEL=DEBUG` for detailed connection information

</details>

<details>
<summary><strong>Linux Instructions</strong></summary>

1.  **Install Ollama** and ensure it's running:
    ```bash
    # Download from https://ollama.com or use:
    curl -fsSL https://ollama.com/install.sh | sh
    ollama serve
    ```

2.  **Install the MCP server**:
    ```bash
    git clone https://github.com/cuba6112/ollama-mcp.git
    cd ollama-mcp
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Claude Desktop** by adding to your config file:
    ```json
    {
      "mcpServers": {
        "ollama": {
          "command": "/path/to/your/venv/bin/python",
          "args": ["-m", "ollama_mcp_server.main"],
          "cwd": "/path/to/ollama-mcp"
        }
      }
    }
    ```

4.  **Restart Claude Desktop** and start using Ollama models!

</details>

<details>
<summary><strong>Windows Instructions</strong></summary>

1.  **Install Ollama**: Download and install from the [official Ollama website](https://ollama.com).

2.  **Install the MCP server**:
    ```bash
    git clone https://github.com/cuba6112/ollama-mcp.git
    cd ollama-mcp
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Claude Desktop** by adding to your config file:
    ```json
    {
      "mcpServers": {
        "ollama": {
          "command": "C:\\path\\to\\your\\venv\\Scripts\\python.exe",
          "args": ["-m", "ollama_mcp_server.main"],
          "cwd": "C:\\path\\to\\ollama-mcp"
        }
      }
    }
    ```

4.  **Restart Claude Desktop** and start using Ollama models!

</details>

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

### Connection Settings
```bash
# Ollama host - automatically detected by default
OLLAMA_HOST=http://localhost:11434      # Manual override for Ollama API URL
OLLAMA_REQUEST_TIMEOUT=30.0             # Request timeout in seconds
OLLAMA_CONNECTION_TIMEOUT=5.0           # Connection timeout in seconds
OLLAMA_MAX_RETRIES=3                    # Max retry attempts
OLLAMA_RETRY_DELAY=1.0                  # Initial retry delay
```

### Host Auto-Detection

The server automatically detects the appropriate Ollama host:

1. **Environment Variable**: If `OLLAMA_HOST` is set, uses that value
2. **Localhost Test**: Tries to connect to `http://localhost:11434`
3. **Network Detection**: If localhost fails, automatically detects local network IP
4. **Fallback**: Uses localhost as final fallback

This ensures seamless operation in both local development and external access scenarios (like Smithery).

### Other Settings
```bash
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

Test the server directly using the MCP dev tool:
```bash
mcp dev ollama_mcp_server/main.py
```

Or run the server and test individual tools:
```bash
# Start the server
python -m ollama_mcp_server.main

# In another terminal, test with Claude Desktop or other MCP clients
# You can also check the example usage:
python examples/usage_example.py
```

This will verify that all core functions work correctly with your Ollama installation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Anthropic](https://www.anthropic.com/) for the Model Context Protocol specification
- [Ollama](https://ollama.com/) for the excellent local LLM platform
- The MCP community for tools and documentation

## Support

If you encounter any issues or have questions:
- Check the [troubleshooting section](#troubleshooting) above
- Look through existing [GitHub issues](https://github.com/your-username/ollama-mcp-server/issues)
- Create a new issue with detailed information about your problem
