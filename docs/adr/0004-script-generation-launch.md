# ADR-004: Script Generation for Launch

**Date**: 2024-01-15
**Status**: Accepted
**Deciders**: Project owner

## Context

Claude Code requires environment variables to be set for proper operation with on-premise LLM servers:
- `ANTHROPIC_BASE_URL` - The LLM server URL
- `ANTHROPIC_AUTH_TOKEN` or `ANTHROPIC_API_KEY` - Authentication
- Model-specific variables for each Claude role

The application must launch Claude Code in a way that:
- Preserves environment configuration
- Works across platforms (macOS, Linux, Windows)
- Allows users to see what will be executed
- Enables debugging of configuration issues

## Decision

Generate a bash script that exports environment variables and launches Claude Code, then launch it in a new terminal window.

## Alternatives Considered

### Alternative 1: Direct subprocess launch with environment
- **Pros**: Simple, no intermediate file
- **Cons**: Claude exits when GUI closes, no visible output, hard to debug
- **Why rejected**: User cannot see Claude's output or interact with it

### Alternative 2: Python virtual environment activation
- **Pros**: Isolated environment
- **Cons**: Does not solve the main problem, still no visible terminal
- **Why rejected**: Not applicable to this use case

### Alternative 3: App bundle / executable
- **Pros**: Single file distribution
- **Cons**: Platform-specific, requires build tools
- **Why rejected**: Overly complex for this tool

### Alternative 4: Browser-based UI
- **Pros**: Cross-platform, easy deployment
- **Cons**: Not a desktop experience, requires web server
- **Why rejected**: Would not provide native desktop feel

## Consequences

### Positive
- Users can see exactly what will be executed
- Environment variables clearly visible and debuggable
- Works with any shell environment
- Easy to modify and re-run manually
- Platform-specific terminal launching for native feel

### Negative
- Temporary script file created in user's home directory
- Requires terminal application to be available
- Script must be cleaned up after use (not done for debugging)

### Neutral
- Script format is platform-specific (bash on Unix, batch on Windows)
- Users may want to save/reuse scripts

## Implementation

### Script Generation
```python
def generate(config: Dict) -> str:
    lines = [
        "#!/bin/bash",
        f'export ANTHROPIC_BASE_URL="{base_url}"',
        f'export ANTHROPIC_AUTH_TOKEN="ollama"',
        f'export ANTHROPIC_DEFAULT_HAIKU_MODEL="{model}"',
        f'cd "{workdir}"',
        "claude",
    ]
    return "\n".join(lines)
```

### Platform-Specific Launching
- **macOS**: AppleScript to open Terminal
- **Windows**: `cmd /c start` command
- **Linux**: gnome-terminal, konsole, xfce4-terminal, or xterm

## Security Considerations

1. No sensitive data is written to script (API keys used carefully)
2. Script has execute permissions only during launch
3. Script location is predictable (`~/.claude/launch_claude.sh`)

## Debugging

Users can:
1. View script in preview before launch
2. Edit script for manual testing
3. Re-run script directly in their own terminal
4. See exact environment variables set

## References

- [Bash Scripting Guide](https://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO.html)
- [AppleScript Terminal Documentation](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction.html)
