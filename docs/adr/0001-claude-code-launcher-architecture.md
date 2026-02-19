# Architecture Decision Record: Claude Code Launcher

## Status

Accepted

## Context

We needed to create a cross-platform launcher for Claude Code that:
1. Supports Windows, Linux, and macOS
2. Provides a TUI for easy interaction
3. Manages installation and uninstallation of Claude Code
4. Handles environment variable configuration
5. Uses a simple, maintainable architecture

## Decision

We chose to build a Python-based launcher with:
- A TUI interface using Python's curses library
- Command-line interface for automation
- JSON file-based settings storage in `~/.claude/settings.json`
- Cross-platform compatibility using Python's standard libraries
- Simple modular architecture

## Consequences

### Positive
- Cross-platform support out-of-the-box with Python
- Simple installation process
- Easy to extend with new features
- Minimal dependencies (only standard library)
- User-friendly TUI interface
- Persistent environment variable storage

### Negative
- TUI requires terminal support
- Limited to Python ecosystem for GUI features
- JSON storage format might be less efficient for very large configurations
- No built-in auto-update mechanism

## Tradeoffs

We traded complex GUI frameworks for simplicity and cross-platform compatibility. The curses-based TUI provides a good balance between functionality and portability, avoiding dependencies on external GUI libraries.

The decision to use JSON for settings storage was made to ensure:
- Easy human readability
- Simple file-based persistence
- Compatibility with various tools and scripts
- No external database dependencies