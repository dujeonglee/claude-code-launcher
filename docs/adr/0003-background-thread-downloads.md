# ADR-003: Background Thread for Downloads

**Date**: 2024-01-15
**Status**: Accepted
**Deciders**: Project owner

## Context

Downloading Claude Code (~20-30MB) can take significant time depending on network speed. This operation should not block the UI or cause the application to become unresponsive.

The application must:
- Keep the UI responsive during downloads
- Provide visual feedback on download progress
- Allow users to cancel downloads
- Handle network interruptions gracefully

## Decision

Use Qt's QThread with signals for background downloads and progress reporting.

## Alternatives Considered

### Alternative 1: Separate process
- **Pros**: Complete isolation from main process
- **Cons**: Higher overhead, more complex inter-process communication
- **Why rejected**: Overkill for this use case

### Alternative 2: asyncio with Qt event loop
- **Pros**: Modern async/await pattern
- **Cons**: PySide6 integration requires careful setup, less beginner-friendly
- **Why rejected**: QThread is simpler and well-integrated with Qt widgets

### Alternative 3: ThreadPoolExecutor
- **Pros**: Simple API, uses system threads
- **Cons**: Limited control, no direct Qt integration
- **Why rejected**: QThread provides better progress reporting through signals

### Alternative 4: synchronous download with periodic event processing
- **Pros**: Simple implementation
- **Cons**: Still blocks UI, harder to implement cancellation
- **Why rejected**: Poor user experience, not truly responsive

## Consequences

### Positive
- Qt signals provide thread-safe communication with UI
- Progress can be emitted at any granularity
- Clean separation of concerns (download logic in thread)
- User can interact with other UI elements during download
- Easy to implement cancellation flag

### Negative
- Must follow Qt thread safety rules
- Object lifetimes must be managed carefully (parenting)
- Signals/slots pattern may be unfamiliar to some developers

### Neutral
- Slightly more code to set up than synchronous approach
- Debugging multi-threaded code requires care

## Implementation

```python
class ClaudeInstaller(QThread):
    progress = Signal(int, str)  # percentage, message
    finished = Signal(bool, str)  # success, message
    error = Signal(str)  # error message

    def __init__(self, download_dir: Path, parent=None):
        super().__init__(parent)
        self.download_dir = download_dir
        self.cancelled = False

    def run(self):
        # Download logic in background thread
        # Emit progress updates via signals
        # Handle cancellation via flag
        pass
```

### Download Progress
```python
# Connect signals before starting thread
self.installer.progress.connect(self._on_install_progress)
self.installer.finished.connect(self._on_install_finished)
self.installer.error.connect(self._on_install_error)
```

## Cancellation Flow

1. User clicks "Cancel" button
2. Sets `self.cancelled = True` flag
3. Download loop checks flag between chunks
4. Thread exits early if cancelled
5. Finished signal emitted with success=False

## Error Handling

- Network errors emit `error` signal
- Partial downloads cleaned up on error
- User notified of failure with message

## References

- [Qt QThread Documentation](https://doc.qt.io/qt-6/qthread.html)
- [Qt Signals and Slots](https://doc.qt.io/qt-6/signalsandslots.html)
