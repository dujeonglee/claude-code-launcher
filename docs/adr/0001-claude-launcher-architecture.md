# Claude Code Launcher - Architecture Decision Record

## Decision

We have implemented a Python-based cross-platform launcher for Claude Code with TUI support that manages installation and environment variables.

## Context

The requirements specified:
1. Python application supporting Windows, Linux, and macOS
2. TUI support for user-friendly interface
3. Installation and uninstallation functionality
4. Environment variable management
5. Settings stored in `~/.claude/settings.json`

## Decision

We chose to implement a single Python file application that:

1. Uses the standard library for cross-platform compatibility
2. Implements a TUI using curses for terminal interface
3. Stores environment variables in JSON format in `~/.claude/settings.json`
4. Supports command-line interface for automation
5. Uses subprocess for installation commands with parameterized arguments

## Consequences

### Positive
- Cross-platform compatibility without external dependencies
- User-friendly TUI interface
- Persistent environment variable storage
- Simple command-line interface for automation
- No external dependencies required

### Negative
- TUI is limited to terminal environments
- Subprocess calls require system permissions
- Single-file implementation may become complex over time

## Alternatives Considered

1. **GUI Application (PyQt/PySide)**: Would require additional dependencies and is not suitable for all environments
2. **Web-based Interface**: Overkill for this simple tool
3. **Separate installation/uninstallation scripts**: Would be more complex to maintain

## Status

This decision is implemented and working as designed.