# Claude Code Launcher - Getting Started

This guide will help you get started with the Claude Code Launcher, a cross-platform tool for managing Claude Code installation and environment variables.

## Prerequisites

- Python 3.6 or higher
- pip package manager

## Installation

### From PyPI (Recommended)

```bash
pip install claude-code-launcher
```

### From Source

```bash
git clone <repository-url>
cd claude_launcher
pip install .
```

## Quick Start

### Running the Launcher

The launcher defaults to TUI mode:

```bash
claude-launcher
```

### Command Line Usage

```bash
# Install Claude Code
claude-launcher --install

# Uninstall Claude Code
claude-launcher --uninstall

# Set environment variable
claude-launcher --set-env ANTHROPIC_API_KEY "your-api-key-here"

# List environment variables
claude-launcher --list-env
```

## First-Time Setup

1. **Run the launcher**:
   ```bash
   claude-launcher
   ```

2. **Configure your API key**:
   - Navigate to "Set Environment Variables" in the TUI
   - Find `ANTHROPIC_API_KEY`
   - Enter your Claude API key

3. **Configure additional settings** as needed for your use case

## Configuration File Location

Environment variables are stored in:
```
~/.claude/settings.json
```

Example configuration:
```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-apikey-1234567890",
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "ANTHROPIC_MODEL": "claude-3-5-sonnet-20240620"
  }
}
```

## TUI Interface Overview

The TUI provides the following options:

1. **Install Claude Code** - Install Claude Code via pip
2. **Uninstall Claude Code** - Remove Claude Code via pip
3. **Set Environment Variables** - Configure Claude Code settings
4. **List Environment Variables** - View current configuration
5. **System Information** - Display platform details
6. **Exit** - Quit the launcher

## Troubleshooting

### Common Issues

**Permission Denied During Installation**
```bash
# Try with sudo if needed
sudo claude-launcher --install
```

**TUI Not Working**
```bash
# Use CLI mode instead
claude-launcher --install
```

**Settings File Not Found**
The launcher automatically creates the settings file at `~/.claude/settings.json` if it doesn't exist.

### Environment Variable Validation

The launcher doesn't validate environment variable values. Ensure you provide valid values for the Claude Code integration to work properly.

## Next Steps

1. Configure your Claude API key
2. Set up any additional integration options (Bedrock, Vertex, Foundry)
3. Test Claude Code functionality
4. Adjust environment variables as needed for your workflow