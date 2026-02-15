# Development Guide

## Project Structure

```
/Users/idujeong/workspace/claude_launcher/
├── claude_launcher.py          # Main application (1416 lines)
├── README.md                   # User documentation
├── API.md                      # API reference
├── CHANGELOG.md                # Version history
├── DEVELOPMENT.md              # This file
├── docs/
│   └── architecture.md         # Architecture documentation
└── .claude/
    ├── agents/
    │   ├── auditor.md          # Security audit agent
    │   ├── implementer.md      # Implementation agent
    │   ├── sdlc-orchestrator.md # SDLC orchestration
    │   ├── documenter.md       # Documentation agent
    │   └── verifier.md         # Testing/verification agent
    └── skills/
        ├── audit/              # Audit methodology
        │   ├── SKILL.md
        │   ├── SECURITY_CHECKLIST.md
        │   └── ARCHITECTURE_REVIEW.md
        ├── document/           # Documentation methodology
        │   └── SKILL.md
        ├── implement/          # Implementation patterns
        │   └── SKILL.md
        └── verify/             # Verification methodology
            └── SKILL.md
```

## Development Setup

### Prerequisites

- Python 3.9+
- pip
- Qt6 (for PySide6)
- Node.js/npm (for Claude Code CLI)

### Installation

```bash
# Clone or navigate to the project directory
cd /Users/idujeong/workspace/claude_launcher

# Install Python dependencies
pip install PySide6 requests PyYAML

# Install Claude Code CLI (for testing)
npm install -g @anthropic-ai/claude-code
```

### Running Locally

```bash
# Run the application
python claude_launcher.py

# Or with Python module syntax
python -m claude_launcher
```

## Testing

### Manual Testing Checklist

Run the following manual tests:

1. **GUI Launch**
   ```bash
   python claude_launcher.py
   ```
   Verify window opens with correct title and dimensions.

2. **Runtime Switching**
   - Switch between runtimes (Ollama, vLLM, etc.)
   - Verify Base URL updates to default
   - Verify API key field visibility changes

3. **Server Validation**
   - Enter valid URL and click "Validate"
   - Verify status changes to green "Server OK"
   - Test with invalid URL - should show red error

4. **Model Fetching**
   - With running Ollama server, click "Refresh Models"
   - Verify models appear in dropdowns
   - Test with no server - should show warning

5. **Claude Detection**
   - Click "Detect" to find Claude CLI
   - Verify path updates if found
   - Test with missing Claude - should show status message

6. **Installation**
   - Click "Install / Update Claude"
   - Verify download progress shows
   - Test cancellation mid-download
   - Verify binary found after install

7. **Launch**
   - Fill in required fields
   - Click "Let's Roll"
   - Verify new terminal opens
   - Check script was saved to `~/.claude/launch_claude.sh`

### Automated Testing

To run syntax and type checking:

```bash
# Syntax check
python -m py_compile claude_launcher.py

# Linting (if pylint installed)
python -m pylint claude_launcher.py

# Type checking (requires mypy configuration)
mypy claude_launcher.py
```

## Code Style

### Python Conventions

- Follow PEP 8 style guide
- Use type hints on all functions
- Use docstrings (Google style) for public methods
- Imports grouped: stdlib, third-party, local

### Qt Conventions

- Use QThread for background operations
- Communicate via signals/slots (not direct calls)
- Use QStatusBar for status messages
- Use QGroupBox to organize related controls

### Naming Conventions

- Classes: `PascalCase` (e.g., `ConfigManager`)
- Functions: `snake_case` (e.g., `get_latest_version`)
- Private methods: `_leading_underscore`
- Constants: `UPPER_CASE`

## Adding New Features

### Adding a New LLM Runtime

1. Add runtime config to `SUPPORTED_RUNTIMES`:
   ```python
   "new_runtime": {
       "name": "New Runtime",
       "default_port": 1234,
       "api_path": "/v1/models",
       "models_key": "models",
       "model_name_key": "id",
       "health_path": "/health",
       "env_base_url": "http://localhost:1234",
   }
   ```

2. Add to UI combo box in `_build_ui` or dynamically in `_on_runtime_changed`

3. Test with running server

### Adding a New Platform

1. Update `OS_ARCH_MAP` in `OSChecker.get_download_info()`

2. Update `_extract_tarball` in `ClaudeInstaller` if special handling needed

3. Update terminal launching in `ScriptGenerator.launch_in_terminal()`

## Troubleshooting

### Common Issues

1. **Window not appearing on Linux**
   - Check `gnome-terminal` is installed
   - Or set `GNOME_TERMINAL_SERVICE` env var

2. **Download fails with SSL error**
   - Ensure system certificates are up to date
   - On macOS, run "Install Certificates.command"

3. **Binary not executable after install**
   - Manual fix: `chmod +x ~/.claude/claude-downloads/claude`

## Submitting Changes

1. Test all manual scenarios
2. Run linters
3. Update CHANGELOG.md with new version
4. Update README.md if user-facing changes
