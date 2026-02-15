# ADR-002: YAML for Configuration Format

**Date**: 2024-01-15
**Status**: Accepted
**Deciders**: Project owner

## Context

The Claude Code Launcher needs to store user configuration that:
- Supports nested structures (server, models, claude_code sections)
- Is human-editable for manual customization
- Can be easily loaded and saved
- Uses default values when keys are missing

## Decision

Use YAML (via PyYAML) for configuration storage.

## Alternatives Considered

### Alternative 1: JSON
- **Pros**: Standard format, built-in support
- **Cons**: No comments, stricter syntax, less readable
- **Why rejected**: Users cannot add comments to explain config options

### Alternative 2: INI/ConfigParser
- **Pros**: Simple, built into Python
- **Cons**: Limited nesting support, no lists/dictionaries
- **Why rejected**: Cannot represent the nested configuration structure needed

### Alternative 3: TOML
- **Pros**: Human-readable, supports nested tables
- **Cons**: Slightly more complex parsing
- **Why rejected**: Good alternative, but YAML is more familiar to users

### Alternative 4: Custom format
- **Pros**: Full control over syntax
- **Cons**: Requires writing and maintaining parser
- **Why rejected**: Unnecessary complexity, error-prone

## Consequences

### Positive
- Simple, human-readable format that users can edit
- Naturally supports nested structures
- Comments are supported (though stripped on write)
- Python PyYAML is well-maintained and stable

### Negative
- White space sensitivity can cause parsing errors
- Type coercion can be surprising (strings vs numbers)
- YAML injection risks if loading untrusted content

### Neutral
- Must ensure consistent formatting in saves
- May need to handle edge cases in type conversion

## Configuration File Location

```
~/.claude/launcher_config.yaml
```

## Configuration Schema

```yaml
server:
  runtime: ollama              # LLM provider runtime
  base_url: http://localhost   # Server URL
  api_key: ""                  # Optional API key

models:
  haiku: model-name            # Model for Haiku role
  sonnet: model-name           # Model for Sonnet role
  opus: model-name             # Model for Opus role

claude_code:
  path: claude                 # Claude CLI path
  permission_mode: default     # Permission handling mode
  max_turns: 0                 # Max conversation turns (0=unlimited)

working_directory: /path       # Default working directory
```

## Implementation

- `ConfigManager` class handles loading and saving
- Deep merge ensures defaults are preserved
- Explicit type checking for configuration values

## References

- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [YAML Specification](https://yaml.org/spec/)
