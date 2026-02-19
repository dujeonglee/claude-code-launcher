# Claude Code Launcher

A cross-platform Python application for managing Claude Code installation and environment variables.

## Features

- Cross-platform support (Windows, Linux, macOS)
- Command-line interface using Typer
- Installation and uninstallation functionality
- Environment variable management
- Settings stored in `~/.claude/settings.json`

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd claude_launcher

# Make executable
chmod +x claude_launcher_typer.py

# Run the launcher
python3 claude_launcher_typer.py
```

## Usage

### Command Line Interface

```bash
# Install Claude Code
python3 claude_launcher_typer.py install

# Uninstall Claude Code
python3 claude_launcher_typer.py uninstall

# Set environment variable
python3 claude_launcher_typer.py set-env ANTHROPIC_API_KEY your-api-key

# List environment variables
python3 claude_launcher_typer.py list-env

# Show system information
python3 claude_launcher_typer.py info
```

## Environment Variables

The launcher supports all Claude Code environment variables as specified in the requirements. These include:

- API keys and authentication tokens
- Model selection and configuration
- Proxy settings
- Telemetry and error reporting options
- AWS/Vertex/Foundry integration settings
- And many more configuration options

## Settings File

Environment variables are stored in `~/.claude/settings.json` in the following format:

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "your-api-key",
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "ANTHROPIC_MODEL": "claude-3-5-sonnet-20240620"
  }
}
```

## Architecture

The application follows a modular design with:

1. **Main Application Class (`ClaudeLauncher`)** - Handles all core functionality
2. **Settings Management** - Manages environment variables in JSON format
3. **Command Line Interface** - Uses Typer for command-line operations
4. **Cross-platform Compatibility** - Uses Python's `platform` module to detect and handle different operating systems

## Security

- No hardcoded secrets
- Environment variables stored in user home directory
- Secure handling of subprocess calls with parameterized commands
- No eval/exec usage

## Cross-platform Compatibility

The launcher automatically detects the platform and uses appropriate installation commands for:

- Windows (using curl and PowerShell/ CMD)
- Linux (using curl bash script)
- macOS (using curl bash script)

## Dependencies

- Python 3.6+
- Typer library (`pip install typer`)
- Standard library modules only (no external dependencies required)