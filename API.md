# API Reference

This document describes the public classes and functions in `claude_launcher.py`.

## Constants

### CLAUDE_DOWNLOAD_BASE
```python
CLAUDE_DOWNLOAD_BASE = "https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases"
```
Base URL for Claude Code downloads.

### CHANGELOG_URL
```python
CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
```
URL to fetch Claude Code CHANGELOG for version checking.

### OS_ARCH_MAP
```python
OS_ARCH_MAP = {
    ("darwin", "x86_64"): "darwin-amd64",
    ("darwin", "arm64"): "darwin-arm64",
    ("linux", "x86_64"): "linux-amd64",
    ("linux", "arm64"): "linux-arm64",
    ("win32", "x86_64"): "windows-amd64",
    ("win32", "arm64"): "windows-arm64",
}
```
Mapping of (platform, architecture) tuples to download platform names.

### SUPPORTED_RUNTIMES
```python
SUPPORTED_RUNTIMES = {
    "ollama": {
        "name": "Ollama",
        "default_port": 11434,
        "api_path": "/api/tags",
        "models_key": "models",
        "model_name_key": "name",
        "health_path": "/api/tags",
        "env_base_url": "http://localhost:11434",
    },
    "vllm": {...},
    "mlx": {...},
    "llama_cpp": {...},
    "lm_studio": {...},
    "tgi": {...},
}
```
Configuration for supported LLM runtimes.

### DEFAULT_CONFIG
```python
DEFAULT_CONFIG = {
    "server": {
        "runtime": "ollama",
        "base_url": "http://localhost:11434",
    },
    "models": {
        "haiku": "",
        "sonnet": "",
        "opus": "",
    },
    "claude_code": {
        "path": "claude",
        "permission_mode": "default",
        "max_turns": 0,
    },
    "working_directory": str(Path.home()),
}
```
Default configuration values.

## Classes

### OSChecker

Handles OS and architecture detection for Claude Code downloads.

#### Methods

##### OSChecker.get_os_platform() -> str
Returns the OS platform name.

Returns:
- `"darwin"` for macOS
- `"linux"` for Linux
- `"windows"` for Windows
- `"unknown"` otherwise

##### OSChecker.get_architecture() -> str
Returns the CPU architecture.

Returns:
- `"x86_64"` for Intel/AMD 64-bit
- `"arm64"` for ARM 64-bit
- Original arch name otherwise

##### OSChecker.get_download_info() -> Tuple[str, Optional[str]]
Returns (platform_name, arch_name) for download URL.

Returns:
- `(os_name, arch_identifier)` for supported platforms
- `(None, None)` for unsupported platforms

##### OSChecker.is_supported_platform() -> bool
Returns True if the current platform supports automatic Claude Code download.

---

### VersionManager

Manages Claude Code version checking and fetching from CHANGELOG.

#### Constructor

##### VersionManager.__init__(timeout: int = 10)
Initializes the version manager.

Parameters:
- `timeout`: HTTP request timeout in seconds (default: 10)

#### Methods

##### VersionManager.get_latest_version() -> Optional[str]
Fetches the latest stable version from the Claude Code CHANGELOG.

Returns:
- Version string (e.g., `"2.1.42"`) if successful
- `None` if fetch or parsing fails

##### VersionManager.get_installed_version(claude_path: str) -> Tuple[Optional[str], str]
Gets the installed Claude version.

Parameters:
- `claude_path`: Path to the Claude CLI binary

Returns:
- Tuple of `(version, status_message)`
- `version`: Parsed version string or `None`
- `status_message`: Description of result

##### VersionManager.check_update_needed(claude_path: str) -> Dict[str, Any]
Checks if Claude needs update.

Parameters:
- `claude_path`: Path to the Claude CLI binary

Returns:
```python
{
    "needs_update": bool,
    "installed": Optional[str],
    "latest": Optional[str],
    "can_check": bool,
    "status": str,  # one of: not_installed, up_to_date, update_available, version_check_failed, latest_check_failed
    "status_message": str,
}
```

---

### ConfigManager

Manages application configuration stored in YAML format.

#### Constructor

##### ConfigManager.__init__(config_path: Path = DEFAULT_CONFIG_FILE)
Initializes the config manager.

Parameters:
- `config_path`: Path to the configuration file (default: `~/.claude/launcher_config.yaml`)

#### Methods

##### ConfigManager.load() -> Dict[str, Any]
Loads configuration from file, merging with defaults.

Returns:
- Combined configuration dictionary

##### ConfigManager.save(config: Optional[Dict] = None) -> bool
Saves configuration to file.

Parameters:
- `config`: Configuration dict to save (default: uses current config)

Returns:
- `True` if successful, `False` otherwise

##### ConfigManager.exists() -> bool
Returns `True` if the configuration file exists.

---

### ClaudeInstaller

Background thread for downloading and installing Claude Code.

#### Constructor

##### ClaudeInstaller.__init__(download_dir: Path, parent: Optional[QObject] = None)
Initializes the installer.

Parameters:
- `download_dir`: Directory to download and extract files
- `parent`: Optional Qt parent object

#### Methods

##### ClaudeInstaller.set_version(version: str)
Sets the version to download.

##### ClaudeInstaller.cancel()
Cancels the ongoing download.

##### ClaudeInstaller.get_download_url() -> Optional[str]
Builds the download URL for the current platform.

Returns:
- Full download URL or `None` if platform not supported

#### Signals

- `progress(int, str)` - Emitted with download percentage and message
- `finished(bool, str)` - Emitted on completion with success status and message
- `error(str)` - Emitted if an error occurs

---

### ServerProbe

Provides server health checks and model listing.

#### Methods

##### ServerProbe.validate_url(base_url: str, runtime: str, timeout: float = 5.0) -> Dict
Checks server health endpoint.

Parameters:
- `base_url`: Base URL of the LLM server
- `runtime`: Runtime name (key in SUPPORTED_RUNTIMES)
- `timeout`: Request timeout in seconds

Returns:
```python
{
    "ok": bool,
    "message": str,
    "response_time_ms": float,
}
```

##### ServerProbe.fetch_models(base_url: str, runtime: str, timeout: float = 10.0) -> List[str]
Fetches available models from server.

Parameters:
- `base_url`: Base URL of the LLM server
- `runtime`: Runtime name
- `timeout`: Request timeout in seconds

Returns:
- List of model names

---

### ScriptGenerator

Generates bash launch scripts from configuration.

#### Methods

##### ScriptGenerator.generate(config: Dict) -> str
Generates a bash script from configuration.

Parameters:
- `config`: Configuration dictionary

Returns:
- Bash script content as string

##### ScriptGenerator.save_script(script_content: str, path: Path) -> bool
Saves script to file and makes it executable.

Parameters:
- `script_content`: Script content
- `path`: Path to save script

Returns:
- `True` if successful

##### ScriptGenerator.launch_in_terminal(script_path: Path)
Launches the script in a new terminal window.

Parameters:
- `script_path`: Path to the script file

This method uses platform-specific commands:
- macOS: `osascript` with Terminal
- Windows: `cmd /c start`
- Linux: gnome-terminal, konsole, xfce4-terminal, or xterm

---

### ClaudeLauncherWindow

Main GUI application window.

#### Constructor

##### ClaudeLauncherWindow.__init__()
Creates the main window and initializes all UI components.

#### Public Methods

##### ClaudeLauncherWindow._lets_roll()
Collects configuration, generates launch script, and launches Claude Code in a new terminal.

This is the primary user-facing action that launches Claude with the configured settings.

#### UI Components

The window contains the following sections:

| Section | Description |
|----------|--|
| Server | Runtime selection, Base URL, API key, validation |
| Model Mapping | Model selection for Haiku, Sonnet, Opus |
| Claude Code CLI | Path, permission mode, max turns |
| Installation | Status, install/update buttons |
| Working Directory | Browse and set working directory |
| Script Preview | Preview of generated launch script |

## Utility Functions

### main()

Entry point for the application.

```python
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    window = ClaudeLauncherWindow()
    window.show()
    sys.exit(app.exec())
```

## Configuration File Format

The configuration file uses YAML format:

```yaml
server:
  runtime: ollama              # Required: runtime name
  base_url: http://localhost   # Required: server URL
  api_key: ""                  # Optional: API key for non-Ollama runtimes

models:
  haiku: model-name            # Optional: model for Haiku role
  sonnet: model-name           # Optional: model for Sonnet role
  opus: model-name             # Optional: model for Opus role

claude_code:
  path: claude                 # Optional: Claude CLI path
  permission_mode: default     # Optional: permission mode
  max_turns: 0                 # Optional: max conversation turns

working_directory: /path       # Optional: default working directory
```

## Environment Variables

The generated launch script sets these environment variables:

| Variable | Description |
|--|--|
| `ANTHROPIC_BASE_URL` | Base URL of the LLM server |
| `ANTHROPIC_AUTH_TOKEN` | Auth token (set to "ollama" for Ollama) |
| `ANTHROPIC_API_KEY` | API key (for non-Ollama runtimes) |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Model for Haiku role |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Model for Sonnet role |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Model for Opus role |

## Error Codes

| Status | Description |
|--|--|
| `not_installed` | Claude Code is not installed |
| `up_to_date` | Claude Code is at latest version |
| `update_available` | New version is available |
| `version_check_failed` | Binary exists but version cannot be determined |
| `latest_check_failed` | Cannot fetch latest version from CHANGELOG |
| `install_outdated` | Need to install newer version |
