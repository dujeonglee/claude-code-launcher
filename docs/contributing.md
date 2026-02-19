# Contributing to Claude Code Launcher

We welcome contributions to the Claude Code Launcher! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you encounter a bug or have a feature request, please:

1. Check existing issues to avoid duplicates
2. Provide detailed information including:
   - Environment details (OS, Python version)
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Screenshots if applicable

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.6 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd claude_launcher

# Install in development mode
pip install -e .
```

### Running Tests

```bash
python test_claude_launcher.py
```

## Code Style

### Python Standards

- Follow PEP 8 style guide
- Use descriptive variable and function names
- Include docstrings for all public functions
- Maintain consistent indentation (4 spaces)

### Documentation

- Update README.md for user-facing changes
- Add API documentation for new functions
- Update CHANGELOG.md for each release
- Create ADRs for significant architectural decisions

## Testing

### Test Structure

The project includes a test suite in `test_claude_launcher.py` that covers:

- Settings loading and saving
- Environment variable management
- Installation/uninstallation functionality
- Error handling scenarios

### Running Tests

```bash
python test_claude_launcher.py
```

### Adding New Tests

When adding new features, please include corresponding tests in `test_claude_launcher.py` that verify:

- Basic functionality
- Edge cases
- Error conditions
- Integration with existing features

## Pull Request Process

1. Ensure all tests pass
2. Update documentation as needed
3. Add entries to CHANGELOG.md
4. Make sure your code follows the project's style guidelines
5. Be prepared for code review and feedback

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct, which promotes a welcoming and inclusive environment.

## License

By contributing to the Claude Code Launcher, you agree that your contributions will be licensed under the same license as the project.