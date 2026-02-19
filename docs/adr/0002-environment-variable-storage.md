# Architecture Decision Record: Environment Variable Storage

## Status

Accepted

## Context

We needed to decide how to store environment variables for the Claude Code Launcher. The storage solution should:
1. Persist configuration between launcher sessions
2. Be easily readable and editable by users
3. Support cross-platform compatibility
4. Handle potential file corruption gracefully
5. Be secure for sensitive data like API keys

## Decision

We chose to store environment variables in a JSON file at `~/.claude/settings.json` with the following structure:

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "your-api-key",
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "ANTHROPIC_MODEL": "claude-3-5-sonnet-20240620"
  }
}
```

## Consequences

### Positive
- Human-readable and editable configuration file
- Simple file-based persistence
- Compatible with various tools and scripts
- No external database dependencies
- Easy to backup and transfer settings
- Cross-platform compatibility
- Graceful handling of missing files

### Negative
- JSON parsing overhead for each operation
- No built-in encryption for sensitive data
- Potential for file corruption
- Not suitable for very large configurations
- No version control of settings

## Tradeoffs

We traded the complexity and overhead of a database system for simplicity and ease of use. The JSON approach provides:

1. **Simplicity**: Standard file-based storage using Python's built-in JSON module
2. **Portability**: Works across all platforms without additional dependencies
3. **Readability**: Users can easily view and modify settings
4. **Reliability**: Standard library modules with well-tested error handling
5. **Performance**: Acceptable for typical use cases with reasonable configuration sizes

## Security Considerations

The decision to store environment variables in plain text JSON was made with the following security considerations:
- Environment variables are stored in user's home directory, which should be protected by OS permissions
- API keys and sensitive information are stored in standard locations with appropriate permissions
- The launcher does not include any encryption or obfuscation mechanisms
- Users are responsible for securing their system and permissions
- This approach aligns with standard practices for development tool configuration

## Alternatives Considered

### 1. Database Storage
- **Pros**: Better for large configurations, atomic operations
- **Cons**: Additional dependency, complexity, platform-specific considerations
- **Decision**: Too complex for this simple tool

### 2. INI/Config File Format
- **Pros**: Well-established, human-readable
- **Cons**: Less structured than JSON, limited nesting capabilities
- **Decision**: JSON provides better structure for complex configurations

### 3. Encrypted Storage
- **Pros**: Better security for sensitive data
- **Cons**: Additional complexity, encryption key management, usability issues
- **Decision**: Not required for this development tool use case

### 4. Environment Variables Only
- **Pros**: No persistence, no storage required
- **Cons**: No persistent configuration, requires re-entry each session
- **Decision**: Users need persistent configuration

The JSON file approach provides the best balance of simplicity, readability, and functionality for this tool's requirements.