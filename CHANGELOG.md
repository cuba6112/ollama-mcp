# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-06-10

### Added
- Complete rewrite with enhanced architecture
- Comprehensive error handling with custom exception classes
- Configuration management via environment variables and .env files
- Response caching with configurable TTL
- HTTP connection pooling for improved performance
- Retry logic with exponential backoff
- Structured logging with configurable levels
- Type safety with Pydantic models for all requests/responses
- Advanced generation options (temperature, top_p, top_k, seed, etc.)
- Streaming support for real-time responses
- Additional Ollama API endpoints:
  - `show_model`: Get detailed model information
  - `generate_embeddings`: Create text embeddings (single and batch)
  - `list_running_models`: Show currently loaded models
  - `copy_model`: Duplicate models
  - `check_model_exists`: Verify model availability
- Comprehensive documentation and examples
- Production-ready configuration options

### Changed
- Migrated from HTTP server to proper MCP stdio protocol
- Improved function signatures and parameter validation
- Enhanced error messages with helpful suggestions
- Better handling of embeddings API (fixed schema validation)
- Optimized performance with intelligent caching

### Fixed
- MCP schema mismatch issues with function decorators
- Embeddings function response format compatibility
- Connection pooling and resource management
- Proper lifecycle management for server startup/shutdown

## [0.1.0] - 2025-06-10

### Added
- Initial MCP server implementation
- Basic Ollama API integration
- Core tools: list_models, generate_completion, generate_chat_completion, pull_model, delete_model
- FastAPI-based HTTP server (later migrated to stdio)

### Issues
- Used HTTP instead of MCP stdio protocol
- Limited error handling
- No configuration management
- Basic functionality only