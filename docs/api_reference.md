# Claude Code Launcher - API Reference

## ClaudeLauncher Class

Main class for managing Claude Code launcher functionality.

### Methods

#### `__init__(self)`
Initialize the ClaudeLauncher instance.

#### `_load_settings(self)` → `Dict[str, Any]`
Load settings from JSON file.

#### `_save_settings(self)` → `None`
Save settings to JSON file.

#### `install_claude(self)` → `None`
Install Claude Code using pip.

#### `uninstall_claude(self)` → `None`
Uninstall Claude Code using pip.

#### `get_env_var(self, var_name: str)` → `Optional[str]`
Get environment variable value.

#### `set_env_var(self, var_name: str, value: str)` → `None`
Set environment variable value.

#### `list_env_vars(self)` → `Dict[str, str]`
List all environment variables.

#### `get_system_info(self)` → `Dict[str, str]`
Get system information.

## Environment Variables

The launcher supports all Claude Code environment variables as defined in the requirements document.

### Supported Variables

- `ANTHROPIC_API_KEY`: Anthropic API key (X-Api-Key header)
- `ANTHROPIC_AUTH_TOKEN`: Custom auth token for Authorization header
- `ANTHROPIC_CUSTOM_HEADERS`: Custom headers for requests (Name: Value format)
- `CLAUDE_CODE_CLIENT_CERT`: mTLS client certificate file path
- `CLAUDE_CODE_CLIENT_KEY`: mTLS client key file path
- `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE`: Passphrase for encrypted client key
- `ANTHROPIC_MODEL`: Specify model name to use
- `ANTHROPIC_DEFAULT_SONNET_MODEL`: Sonnet model alias override
- `ANTHROPIC_DEFAULT_OPUS_MODEL`: Opus model alias override
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`: Haiku model alias override
- `CLAUDE_CODE_SUBAGENT_MODEL`: Subagent model to use
- `ANTHROPIC_SMALL_FAST_MODEL`: *(Deprecated)* Background work Haiku class model
- `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION`: AWS region override for Haiku on Bedrock
- `MAX_THINKING_TOKENS`: Enable extended thinking and set token budget
- `CLAUDE_CODE_USE_BEDROCK`: Enable AWS Bedrock usage
- `CLAUDE_CODE_USE_VERTEX`: Enable Google Vertex AI usage
- `CLAUDE_CODE_USE_FOUNDRY`: Enable Microsoft Foundry usage
- `AWS_BEARER_TOKEN_BEDROCK`: Bedrock API key authentication
- `ANTHROPIC_FOUNDRY_API_KEY`: Microsoft Foundry authentication API key
- `CLAUDE_CODE_SKIP_BEDROCK_AUTH`: Skip Bedrock AWS authentication
- `CLAUDE_CODE_SKIP_VERTEX_AUTH`: Skip Vertex Google authentication
- `CLAUDE_CODE_SKIP_FOUNDRY_AUTH`: Skip Foundry Azure authentication
- `VERTEX_REGION_CLAUDE_3_5_HAIKU`: Vertex AI region override for Claude 3.5 Haiku
- `VERTEX_REGION_CLAUDE_3_7_SONNET`: Vertex AI region override for Claude 3.7 Sonnet
- `VERTEX_REGION_CLAUDE_4_0_SONNET`: Vertex AI region override for Claude 4.0 Sonnet
- `VERTEX_REGION_CLAUDE_4_0_OPUS`: Vertex AI region override for Claude 4.0 Opus
- `VERTEX_REGION_CLAUDE_4_1_OPUS`: Vertex AI region override for Claude 4.1 Opus
- `BASH_DEFAULT_TIMEOUT_MS`: Default timeout for long-running bash commands
- `BASH_MAX_TIMEOUT_MS`: Maximum timeout model can set
- `BASH_MAX_OUTPUT_LENGTH`: Maximum characters for bash output (truncated in middle)
- `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR`: Return to project root after bash commands
- `CLAUDE_ENV_FILE`: Shell script path to source before bash command execution
- `CLAUDE_CODE_SHELL_PREFIX`: Prefix command for all bash commands (logging/auditing)
- `MCP_TIMEOUT`: MCP server start timeout (ms)
- `MCP_TOOL_TIMEOUT`: MCP tool execution timeout (ms)
- `MAX_MCP_OUTPUT_TOKENS`: Maximum tokens for MCP tool responses (default: 25,000)
- `CLAUDE_CODE_MAX_OUTPUT_TOKENS`: Maximum output tokens for most requests
- `DISABLE_COST_WARNINGS`: Set to `1` to disable cost warning messages
- `DISABLE_PROMPT_CACHING`: Set to `1` to disable all model prompt caching
- `DISABLE_PROMPT_CACHING_SONNET`: Disable Sonnet model prompt caching
- `DISABLE_PROMPT_CACHING_OPUS`: Disable Opus model prompt caching
- `DISABLE_PROMPT_CACHING_HAIKU`: Disable Haiku model prompt caching
- `SLASH_COMMAND_TOOL_CHAR_BUDGET`: Maximum characters for slash command metadata (default: 15,000)
- `DISABLE_TELEMETRY`: Set to `1` to disable Statsig telemetry
- `DISABLE_ERROR_REPORTING`: Set to `1` to disable Sentry error reporting
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`: Set to `1` to disable all non-essential traffic (disables auto-updater, bug command, error reporting, telemetry)
- `CLAUDE_CODE_ENABLE_TELEMETRY`: Set to `1` to enable OpenTelemetry
- `CLAUDE_CONFIG_DIR`: Custom path for Claude Code settings and data files
- `DISABLE_AUTOUPDATER`: Set to `1` to disable auto-updates
- `DISABLE_BUG_COMMAND`: Set to `1` to disable `/bug` command
- `DISABLE_NON_ESSENTIAL_MODEL_CALLS`: Set to `1` to disable non-essential model calls (flavor text)
- `CLAUDE_CODE_DISABLE_TERMINAL_TITLE`: Set to `1` to disable automatic terminal title updates
- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`: Set to `1` to disable `anthropic-beta` header (useful for LLM gateway integration)
- `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL`: Skip IDE extension auto-installation
- `CLAUDE_CODE_API_KEY_HELPER_TTL_MS`: Credential refresh interval for apiKeyHelper (ms)
- `USE_BUILTIN_RIPGREP`: Set to `0` to use system `rg` instead of built-in `rg`
- `HTTP_PROXY`: HTTP proxy server specification
- `HTTPS_PROXY`: HTTPS proxy server specification
- `NO_PROXY`: Domain/IP list to bypass proxy

## Command Line Interface

### Arguments

- `--tui`: Run in TUI mode (default)
- `--install`: Install Claude Code
- `--uninstall`: Uninstall Claude Code
- `--set-env`: Set environment variable (requires two arguments: VAR VALUE)
- `--list-env`: List all environment variables