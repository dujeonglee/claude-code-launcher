# Contributing to Claude Code Launcher

Thank you for your interest in contributing to the Claude Code Launcher! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please report any inappropriate behavior to the project maintainers.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check the following:

1. The issue hasn't already been reported
2. You're using the latest version of the project
3. You can reproduce the issue in the current version

When creating a bug report, include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, Claude Code version)

### Suggesting Features

Feature requests are welcome! Please include:

- A clear description of the feature
- The problem it solves
- Any alternative solutions you've considered
- Any additional context

### Pull Requests

1. Fork the repository
2. Create a branch from `main` (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m py_compile claude_launcher.py`)
5. Update documentation if needed
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.9+
- pip
- Qt6 (for PySide6)
- Node.js/npm (for Claude Code CLI)

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/claude_launcher.git
cd claude_launcher

# Install development dependencies
pip install -r requirements-dev.txt

# Install Claude Code CLI (for testing)
npm install -g @anthropic-ai/claude-code
```

### Running Tests

```bash
# Syntax check
python -m py_compile claude_launcher.py

# Linting
pylint claude_launcher.py

# Type checking
mypy claude_launcher.py

# Run unit tests
pytest tests/
```

## Coding Standards

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

### Commit Messages

Use conventional commit format:

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `chore`: Routine tasks, dependency updates
- `refactor`: Code refactoring

## Adding New Features

### Adding a New LLM Runtime

1. Add runtime config to `SUPPORTED_RUNTIMES`
2. Add to UI combo box
3. Test with running server
4. Update documentation

### Adding a New Platform

1. Update `OS_ARCH_MAP` in `OSChecker.get_download_info()`
2. Update terminal launching in `ScriptGenerator.launch_in_terminal()`
3. Add tests for the platform

## Documentation

All code changes should be accompanied by documentation changes:

- Update `README.md` for user-facing changes
- Update `CHANGELOG.md` with the change
- Update `API.md` for API changes
- Update `DEVELOPMENT.md` for developer-facing changes

## Questions?

Feel free to open an issue or reach out to the maintainers with any questions!

## Acknowledgments

Contributors are recognized in the project's README and changelog.
