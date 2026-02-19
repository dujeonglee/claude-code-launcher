# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Full TUI interface for interactive management of Claude Code installation and environment variables
- Command-line interface support for automation
- Cross-platform support for Windows, Linux, and macOS
- Environment variable management system
- Installation and uninstallation functionality for Claude Code
- System information display capability
- Comprehensive documentation including README, API reference, and architecture decisions

### Changed
- Updated installation process to use pip for cross-platform compatibility
- Improved error handling and user feedback in all modes
- Enhanced TUI interface with better navigation and user experience
- Refactored core functionality into modular ClaudeLauncher class

### Fixed
- Resolved issues with settings file handling and persistence
- Fixed cross-platform compatibility issues in installation/uninstallation
- Improved error handling for command-line arguments
- Fixed TUI rendering and input handling issues

## [0.1.0] - 2026-02-19

### Added
- Initial implementation of Claude Code Launcher
- Cross-platform support (Windows, Linux, macOS)
- TUI interface for user-friendly interaction
- Installation and uninstallation functionality
- Environment variable management system
- Settings stored in `~/.claude/settings.json`
- Full support for all Claude Code environment variables

### Changed
- Updated documentation to reflect new features
- Refactored code into modular structure with ClaudeLauncher class
- Improved settings management with proper error handling
- Enhanced TUI with better user feedback and error messages

### Fixed
- Fixed JSON file creation and loading issues
- Resolved platform-specific installation issues
- Improved input handling in TUI interface
- Fixed environment variable setting and retrieval