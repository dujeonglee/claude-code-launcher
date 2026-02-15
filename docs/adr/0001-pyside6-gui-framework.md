# ADR-001: PySide6 for GUI Framework

**Date**: 2024-01-15
**Status**: Accepted
**Deciders**: Project owner

## Context

The Claude Code Launcher needs a cross-platform desktop GUI that works on macOS, Linux, and Windows. The application must provide:
- Configuration UI for LLM server settings
- Claude Code version management controls
- Background task progress reporting
- Terminal launching functionality

## Decision

Use PySide6 (Qt for Python) as the GUI framework.

## Alternatives Considered

### Alternative 1: Tkinter
- **Pros**: Built into Python standard library, no additional dependencies
- **Cons**: Outdated appearance, limited widget set, difficult to style
- **Why rejected**: Does not provide modern UI capabilities needed for good UX

### Alternative 2: PyQt6 (commercial license)
- **Pros**: Same features as PySide6
- **Cons**: Requires commercial license for proprietary software
- **Why rejected**: Licensing restrictions for this personal project

### Alternative 3: Electron/JavaScript
- **Pros**: Cross-platform, rich ecosystem
- **Cons**: Large runtime footprint, requires Node.js installation
- **Why rejected**: Overkill for this relatively simple configuration tool

### Alternative 4: Web-based (HTML/CSS/JS)
- **Pros**: Universal compatibility
- **Cons**: Requires web server, not a "desktop" experience
- **Why rejected**: Would not provide native desktop feel

### Alternative 5: Dear PyGui
- **Pros**: Modern, Pythonic API
- **Cons**: Less mature, smaller community
- **Why rejected**: PySide6 has better long-term stability and documentation

## Consequences

### Positive
- Qt provides native look and feel on all platforms
- Excellent support for background tasks via QThread
- Mature and stable framework with long-term support
- Available in most Linux package managers
- Excellent documentation and community support

### Negative
- Dependency on Qt6 (larger install footprint ~100MB)
- Must handle platform-specific terminal launching logic
- Licensing: Must ensure dynamic linking for LGPL compliance

### Neutral
- Learning curve for developers unfamiliar with Qt
- Signal/slot pattern requires different mental model than callbacks

## Implementation

The application uses:
- QMainWindow for main window
- QComboBox, QLineEdit, QPushButton for controls
- QThread for background downloads
- Signals/slots for cross-thread communication
- Platform-specific AppleScript and subprocess calls for terminal launching

## References

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Qt for Python Examples](https://doc.qt.io/qtforpython/examples/)
- [LGPL Compliance Guide](https://www.qt.io/blog/2020/06/08/pyqt-licensing-changes)
