# Claude Code Launcher

A cross-platform Python application for managing Claude Code installation and environment variables.

## Features

- Cross-platform support (Windows, Linux, macOS)
- Command-line interface using Typer
- Installation and uninstallation functionality
- Environment variable management
- Settings stored in `~/.claude/settings.json`

## Versions

This project provides two implementations:

1. **Original curses-based TUI version** (`claude_launcher.py`)
2. **Typer-based CLI version** (`claude_launcher_typer.py`)

## Installation

### Using Original Version (curses-based TUI)
```bash
# Clone the repository
git clone <repository-url>
cd claude_launcher

# Make executable
chmod +x claude_launcher.py

# Run in TUI mode
python3 claude_launcher.py --tui
```

### Using Typer Version
```bash
# Clone the repository
git clone <repository-url>
cd claude_launcher

# Make executable
chmod +x claude_launcher_typer.py

# Run the Typer version
python3 claude_launcher_typer.py
```

## Installation Method

The Claude Code launcher uses the official installation method from [Claude Code setup documentation](https://code.claude.com/docs/en/setup). It automatically detects your platform and uses:

- **macOS, Linux, WSL**: `curl -fsSL https://claude.ai/install.sh | bash`
- **Windows**: PowerShell `irm https://claude.ai/install.ps1 | iex` or CMD fallback

This ensures you get the latest version with all proper dependencies and security updates.

## Usage

### Command Line Interface

```bash
# Run in TUI mode (default)
python3 claude_launcher.py --tui

# Install Claude Code
python3 claude_launcher.py --install

# Uninstall Claude Code
python3 claude_launcher.py --uninstall

# Set environment variable
python3 claude_launcher.py --set-env ANTHROPIC_API_KEY your-api-key

# List environment variables
python3 claude_launcher.py --list-env
```

### TUI Interface

When run in TUI mode, users can:

1. Install Claude Code
2. Uninstall Claude Code
3. Set environment variables
4. List all environment variables
5. View system information

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
3. **TUI Interface** - Provides interactive terminal interface
4. **Command Line Interface** - Supports CLI operations

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
- Standard library modules only (no external dependencies required)