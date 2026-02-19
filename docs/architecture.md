# Claude Code Launcher - Architecture

## Overview

The Claude Code Launcher is a cross-platform Python application designed to manage Claude Code installation and environment variable configuration. It provides both a text-based user interface (TUI) and command-line interface (CLI) for ease of use across different environments.

## System Components

### 1. Main Application Class (`ClaudeLauncher`)

The core of the application is the `ClaudeLauncher` class which encapsulates all functionality:

- **Settings Management**: Handles loading, saving, and manipulation of environment variables
- **Installation Management**: Provides install/uninstall functionality for Claude Code
- **System Information**: Retrieves and displays system details
- **Environment Variable Interface**: Provides methods for getting and setting environment variables

### 2. User Interface

#### TUI Interface
- Built using Python's `curses` library
- Menu-driven navigation system
- Interactive variable setting with input validation
- Color-coded display for better user experience

#### Command Line Interface
- Uses `argparse` for argument parsing
- Supports direct operations without TUI interaction
- Compatible with automation scripts and CI/CD pipelines

### 3. Configuration Storage

Environment variables are persisted using a JSON file format:

- **Location**: `~/.claude/settings.json`
- **Structure**:
```json
{
  "env": {
    "ANTHROPIC_API_KEY": "your-api-key",
    "CLAUDE_CODE_USE_BEDROCK": "1"
  }
}
```
- **Error Handling**: Gracefully handles missing files and JSON parsing errors

### 4. Cross-platform Compatibility

The application handles platform differences through:

- `platform` module for OS detection
- `subprocess` module for executing platform-appropriate commands
- Path handling using `pathlib.Path` for cross-platform compatibility

## Data Flow

1. **Initialization**:
   - Application starts and loads settings from `~/.claude/settings.json`
   - Creates settings directory if it doesn't exist

2. **User Interaction**:
   - TUI mode: User selects options from menu, which triggers corresponding methods
   - CLI mode: Command-line arguments are parsed and processed directly

3. **Operation Execution**:
   - For installation/uninstallation: Executes pip commands using `subprocess`
   - For environment variables: Updates JSON file and handles persistence

4. **Output**:
   - TUI mode: Direct screen updates via curses library
   - CLI mode: Standard output to console

## External Dependencies

The application uses only Python standard library modules:

- `os`, `sys`, `json`, `platform`, `subprocess` - Core system operations
- `pathlib` - Path handling
- `argparse` - Command-line argument parsing
- `curses` - TUI interface
- `getpass` - Secure input handling

## Security Considerations

- Environment variables are stored in user's home directory with appropriate permissions
- No hard-coded secrets in the source code
- Subprocess calls are parameterized to prevent injection attacks
- No use of `eval()` or `exec()` functions
- Sensitive data (API keys) are handled through environment variables, not stored in logs

## Design Patterns

### Modular Design
The application follows a modular approach where each responsibility is separated:
- Settings management
- Installation logic
- User interface
- Platform handling

### Single Responsibility Principle
Each class and method has a single, well-defined purpose:
- `ClaudeLauncher` class manages settings and core operations
- TUI functions handle display and user input
- CLI parsing handles command-line arguments

### Error Handling
- Graceful handling of missing files and invalid JSON
- User-friendly error messages
- Proper exception propagation

## File Structure

```
claude_launcher/
├── claude_launcher.py          # Main application code
├── test_claude_launcher.py     # Test suite
├── README.md                   # Documentation
├── CHANGELOG.md                # Version history
└── docs/
    ├── architecture.md         # Architecture documentation
    ├── api_reference.md        # API documentation
    ├── getting_started.md      # Getting started guide
    └── adr/
        ├── 0001-claude-code-launcher-architecture.md
        └── 0002-environment-variable-storage.md
```

## Deployment Considerations

### Installation
- Can be installed via pip for easy distribution
- No external dependencies required
- Works across Windows, Linux, and macOS

### Configuration
- Settings are persisted in user home directory
- Default behavior when no settings exist
- Error recovery for corrupted configuration files

### Maintenance
- Simple update process via pip
- No complex dependencies to manage
- Standard Python application lifecycle