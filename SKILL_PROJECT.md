# Project-Specific Documentation Skill

This document extends the base `document` skill with project-specific guidelines for the Claude Code Launcher.

## Project Overview

**Project**: Claude Code Launcher
**Language**: Python (PySide6)
**Type**: Desktop GUI Application
**License**: Proprietary (for internal/personal use)

## Documentation Standards

### README Files

All READMEs should follow this structure (from `.claude/skills/document/SKILL.md`):

```markdown
# Project/Module Name

One-sentence summary of what this does and why it exists.

## Quick Start

Minimal example to get from zero to working in < 2 minutes.

## Installation

Prerequisites, dependencies, and setup steps.

## Usage

### Basic Usage
Most common use case with a working code example.

### Advanced Usage
Less common patterns, configuration options.

## API Reference

Key functions/classes with signatures (or link to generated docs).

## Architecture

Brief description of how this is structured and why.
Link to ADRs for significant decisions.

## Configuration

Environment variables, config files, and their options.

## Development

How to set up for development, run tests, and contribute.

## Troubleshooting

Common issues and their solutions.
```

### Documentation Files for This Project

| File | Location | Purpose |
|------|----------|---------|
| README.md | Project root | User-facing overview |
| API.md | Project root | API reference |
| DEVELOPMENT.md | Project root | Development setup guide |
| CHANGELOG.md | Project root | Version history |
| docs/architecture.md | docs/ | Architecture decisions |
| .claude/README.md | .claude/ | Agent/skill framework docs |

### API Documentation Style

For Python classes and functions:

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """Brief description of what this does.

    Extended description if needed. Explain the 'why', not the 'how'.

    Args:
        param1: Description of first parameter.
        param2: Description of second parameter.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When this exception is raised.

    Example:
        >>> result = function_name("value1", "value2")
        >>> print(result)
    """
```

## Changelog Format

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [Unreleased]

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Features that will be removed

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Security fixes
```

## Architecture Decision Records

Store ADRs in `docs/adr/NNNN-description.md`:

```markdown
# ADR-XXXX: Title

**Status**: Proposed | Accepted | Deprecated | Superseded

**Context**: What is the issue we're facing?

**Decision**: What did we decide?

**Consequences**: What are the tradeoffs?

**References**: Links to related documents or issues.
```

## Documentation Checklist

Before marking a task as complete:

- [ ] README updated for any user-facing changes
- [ ] API reference updated for new/changed public functions
- [ ] Architecture decisions documented (if significant)
- [ ] Configuration options documented
- [ ] Example code in docstrings works
- [ ] Changelog entry added
- [ ] No broken links in documentation

## Tools and Commands

### Documentation Generation

```bash
# Check for missing docstrings (requires pydocstyle)
pydocstyle claude_launcher.py

# Generate HTML docs (requires pdoc)
pdoc --html claude_launcher.py
```

### Documentation Linting

```bash
# Check markdown links
markdown-link-check README.md
```

## Related Documentation

- Base document skill: `.claude/skills/document/SKILL.md`
- Agent framework: `.claude/README.md`
- Implementation patterns: `.claude/skills/implement/SKILL.md`
- Verification methodology: `.claude/skills/verify/SKILL.md`
- Audit methodology: `.claude/skills/audit/SKILL.md`
