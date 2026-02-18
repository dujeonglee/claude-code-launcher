# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `ClaudeUninstaller` class for removing Claude Code installation
- `--permission-mode` option in generated launch script
- `--max-turns` option in generated launch script
- `claude.exe` extension for Windows platform support
- musl libc detection for Linux downloads
- SHA256 checksum verification for downloaded binaries
- Manifest.json support for versioned downloads

### Changed
- Updated download URL pattern to use GCS bucket structure
- Changed `OS_ARCH_MAP` to use `x64` instead of `x86_64` format
- Renamed `claude_launcher_window.py` to `claude_launcher.py`
- Improved terminal launching with platform-specific commands

### Deprecated

### Removed

### Fixed
- Fixed Windows binary name detection in auto-detection
- Fixed download URL construction for Windows platform
- Fixed platform variable in `get_download_url()`

### Security
- Added checksum verification for binary downloads
- No hardcoded secrets (API keys stored in user config only)

## [2.0.0] - 2024

### Added
- Full Claude Code installation management with GUI
- Automatic version checking from CHANGELOG
- Support for multiple LLM runtimes (Ollama, vLLM, MLX Serve, llama.cpp, LM Studio, TGI)
- Model mapping for Haiku, Sonnet, and Opus roles
- Background download thread with progress reporting
- Configurable working directory
- Script preview before launch
- Dark theme UI with styled components

### Changed

### Deprecated

### Removed

### Fixed

### Security
