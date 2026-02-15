# Architecture Documentation

## System Overview

The Claude Code Launcher is a desktop application that provides a graphical interface for configuring and launching Claude Code with on-premise LLM providers. It bridges the gap between local LLM servers and the Claude CLI, handling version management, configuration persistence, and script generation.

## Architecture Decision Records

### ADR-001: PySide6 for GUI Framework

**Context**: The application needs a cross-platform GUI that works on macOS, Linux, and Windows.

**Decision**: Use PySide6 (Qt for Python) because:
- Qt provides native look and feel on all platforms
- Excellent support for background tasks via QThread
- Mature and stable framework with long-term support
- Available in most Linux package managers

**Consequences**:
- Dependency on Qt6 (larger install footprint)
- Must handle platform-specific terminal launching
- Licensing: Qt under LGPL requires dynamic linking

**Status**: Accepted

### ADR-002: YAML for Configuration

**Context**: Need human-readable configuration that supports nested structures.

**Decision**: Use YAML with PyYAML for configuration storage.

**Consequences**:
- Simple user-editable config file
- Supports nested structures naturally
- White space sensitivity requires careful parsing

**Status**: Accepted

### ADR-003: Background Thread for Downloads

**Context**: Downloading Claude Code (~20-30MB) should not block the UI.

**Decision**: Use QThread with signals for progress reporting.

**Consequences**:
- Safe cross-thread communication via Qt signals
- UI remains responsive during downloads
- Requires careful resource cleanup on cancellation

**Status**: Accepted

### ADR-004: Script Generation for Launch

**Context**: Claude Code requires environment variables for LLM server configuration.

**Decision**: Generate a bash script that exports environment variables and launches Claude.

**Consequences**:
- Works with any shell environment
- Easy to debug (users can see exactly what runs)
- Requires platform-specific terminal launching logic

**Status**: Accepted

## Component Details

### OSChecker

Handles OS and architecture detection for determining the correct Claude Code download.

```python
OSChecker.get_os_platform() -> "darwin" | "linux" | "windows"
OSChecker.get_architecture() -> "x86_64" | "arm64" | other
OSChecker.get_download_info() -> (platform_name, arch_name) | (None, None)
```

### VersionManager

Fetches and caches Claude Code version information from GitHub.

- Fetches from `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md`
- Parses version headers from changelog
- Caches for 1 hour to avoid rate limiting
- Compares installed vs latest version

### ConfigManager

Manages application configuration stored in YAML format.

- Loads from `~/.claude/launcher_config.yaml`
- Saves with human-readable formatting
- Supports deep merging of config defaults
- Provides default values for all options

### ClaudeInstaller

Background thread for downloading and installing Claude Code.

```python
# Signals
progress(int, str)  # percentage, message
finished(bool, str)  # success, result_message
error(str)  # error_description
```

Workflow:
1. Create download directory
2. Download archive from Google Cloud
3. Extract archive (tar.gz or zip)
4. Locate claude binary
5. Make executable (Unix)
6. Report success/failure

### ServerProbe

Health checks and model listing for LLM servers.

```python
ServerProbe.validate_url(base_url, runtime) -> {"ok": bool, "message": str}
ServerProbe.fetch_models(base_url, runtime) -> List[str]
```

### ScriptGenerator

Generates bash launch scripts from configuration.

```python
ScriptGenerator.generate(config) -> str  # bash script content
ScriptGenerator.save_script(content, path) -> bool
ScriptGenerator.launch_in_terminal(path)  # platform-specific
```

## Data Flow

### Configuration Flow

```
User Input → GUI → ConfigCollector → YAML Save
                    ↓
              YAML Load → GUI Populate
```

### Installation Flow

```
Check Version → Fetch Latest → Confirm → Download → Extract → Locate Binary
                    ↓
              Update Config
```

### Launch Flow

```
Collect Config → Validate → Generate Script → Save Script → Launch Terminal
```

## Error Handling Strategy

| Scenario | Approach |
|----------|----------|
| Network errors | Retry with timeout, user notification |
| Binary not found | Suggest installation, show error dialog |
| Version check failure | Continue with installed version |
| Download failure | Clean up partial files, show error |
| Platform unsupported | Show manual install instructions |

## Security Considerations

1. **No hardcoded secrets**: API keys are stored in user config (not source)
2. **HTTPS for downloads**: Claude Code downloaded over HTTPS
3. **No shell injection**: Script generation uses proper quoting
4. **File permissions**: Binary permissions set correctly (executable)
5. **Config permissions**: User-only config file

## Limitations

1. **Platform support**: Only macOS, Linux, and Windows supported
2. **Architecture support**: x86_64 and ARM64 only
3. **Version checking**: Requires internet access
4. **Terminal launching**: Limited to common terminals (gnome-terminal, konsole, etc.)

## Future Enhancements

Potential improvements:

1. Support additional LLM runtimes (vLLM, etc.)
2. Multiple Claude Code versions with switching
3. Proxy support for downloads
4. Custom script templates
5. Session management
6. Advanced model selection UI
