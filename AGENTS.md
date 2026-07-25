# Agent Instructions for PlaylistForge

PlaylistForge is a modular desktop utility for extracting, cleaning, transforming, and exporting YouTube playlist metadata. This document helps AI agents be immediately productive.

## Quick Start

**Entry point**: `playlistforge.app:main` (bootstrap in [app.py](playlistforge/app.py#L10))

**Run the app**:
```bash
python -m playlistforge
```

**Run tests**:
```bash
pytest
```

**Linting & type checking**:
```bash
ruff check playlistforge tests
mypy playlistforge
```

## Architecture

PlaylistForge is intentionally modular: the GUI never calls yt-dlp directly, exporters are plugin-style classes, and the cleaning system is a typed rule pipeline.

### Core Modules

| Module | Purpose | Key Pattern |
|--------|---------|------------|
| [`core/`](playlistforge/core/) | Immutable dataclasses, enums, typed errors, result objects | Frozen dataclasses with slots; user-friendly error messages |
| [`extraction/`](playlistforge/extraction/) | URL validation, yt-dlp wrapper, Qt worker, background service | Qt Signal/Slot with fallback imports for non-GUI tests |
| [`cleaning/`](playlistforge/cleaning/) | Rule engine, presets, undo/redo history | Typed rule pipeline; immutable transformations |
| [`export/`](playlistforge/export/) | Exporter plugin interface, registry, formatters | ABC base class; runtime registry |
| [`settings/`](playlistforge/settings/) | JSON persistence, platform-specific paths | Atomic writes; cross-platform XDG/AppData/Library support |
| [`ui/`](playlistforge/ui/) | PySide6 main window, dialogs, widgets, table models | Qt patterns; proxy models for filtering/sorting |
| [`logging/`](playlistforge/logging/) | Rotating file logs, Qt signal handler | Configured on app startup |

### Data Flow

1. **Extraction**: URL → validation → yt-dlp worker (background thread) → Playlist dataclass
2. **Cleaning**: Playlist + CleaningRules → CleaningEngine → cleaned titles (immutable)
3. **Export**: Playlist + ExportOptions → Exporter (plugin lookup) → file/clipboard

## Key Conventions

### Frozen Dataclasses with Slots

All domain models use `@dataclass(slots=True, frozen=True)`:
- [Video](playlistforge/core/models.py#L22)
- [Playlist](playlistforge/core/models.py#L44)
- [ApplicationSettings](playlistforge/core/models.py) (search for it in the file)

**Do**: Use immutable dataclasses for models and return new instances on change.
**Don't**: Mutate model fields; use `dataclasses.replace()` instead.

```python
# Correct
cleaned_video = replace(video, title_cleaned=new_title)

# Avoid
video.title_cleaned = new_title  # frozen=True prevents this anyway
```

### Qt Signals with Fallback Imports

Qt imports have fallback implementations for non-GUI environments (tests):

```python
try:
    from PySide6.QtCore import QObject, Signal
except ImportError:
    class QObject:  # Fallback
        pass
    class Signal:
        def __init__(self, *args):
            pass
        def emit(self, *args):
            return None
```

**Do**: Follow this pattern when introducing new Qt dependencies.
**Don't**: Assume PySide6 is available outside the UI layer.

### User-Friendly Error Messages

[PlaylistForgeError](playlistforge/core/errors.py#L7) separates display messages from technical details:

```python
class RateLimitedError(ExtractionError):
    user_message = "YouTube is rate limiting requests. Please wait a while and try again."
```

**Do**: Set `user_message` for exceptions shown to end users.
**Don't**: Include raw exception names or stack traces in user-facing UI.

### Plugin Pattern for Exporters

Exporters are registered at runtime in a [registry](playlistforge/export/registry.py):

```python
class Exporter(ABC):
    format: ExportFormat
    @abstractmethod
    def export(self, playlists, options, destination):
        pass

# In registry.py:
registry.register(JsonExporter())
registry.register(CsvExporter())
# ...
```

**Do**: Add new exporters by subclassing [Exporter](playlistforge/export/base.py) and registering them in `default_exporter_registry()`.
**Don't**: Hardcode exporter references in the UI; always look them up via the registry.

### Type Hints & Imports

- Use `from __future__ import annotations` in all modules.
- Type all function signatures; ruff enforces `ANN` rules.
- Target Python 3.12+ (ruff `target-version = "py312"`).

**Do**: `def extract(url: str) -> Playlist:`
**Don't**: `def extract(url): # returns a Playlist`

### Settings Persistence

Settings are loaded/saved via [SettingsRepository](playlistforge/settings/repository.py) with platform-appropriate paths:
- **Windows**: `%APPDATA%\PlaylistForge\settings.json`
- **macOS**: `~/Library/Application Support/PlaylistForge/settings.json`
- **Linux**: `$XDG_CONFIG_HOME/PlaylistForge/settings.json` (or `~/.config/PlaylistForge/`)

**Do**: Use `SettingsRepository` to persist user preferences.
**Don't**: Write settings to arbitrary paths or hard-code `~/.playlistforge`.

## Common Patterns

### Background Extraction

Never block the Qt event loop. Use [ExtractionService](playlistforge/extraction/service.py):

```python
self.extraction_service.start(request)
self.extraction_service.progress.connect(self.on_progress)
self.extraction_service.finished.connect(self.on_finished)
```

### Immutable Transformations

Use `dataclasses.replace()` to transform models:

```python
from dataclasses import replace
cleaned = CleaningEngine().apply_playlist(playlist, rules)  # Returns new Playlist
```

### Table Models

Use [VideoTableModel](playlistforge/ui/models/video_table_model.py) + [VideoFilterProxyModel](playlistforge/ui/models/proxy_models.py) for sorting/filtering without mutating data.

## Development Notes

### Python 3.12+

- Target Python 3.12 (PySide6, yt-dlp, openpyxl all support it).
- Use modern type hints; no `List`, `Dict` from `typing` (use `list`, `dict` instead).

### Testing

- **Test runner**: `pytest` (configured in [pyproject.toml](pyproject.toml#L61)).
- **Coverage**: Run `pytest --cov=playlistforge` to measure coverage.
- **Mocking Qt**: Import fallbacks allow tests to run without a display server.

### Packaging

- **PyInstaller specs**: [packaging/pyinstaller/](packaging/pyinstaller/)
- **Linux (AppImage/deb)**: [packaging/linux/](packaging/linux/)
- **macOS (DMG)**: [packaging/macos/](packaging/macos/)
- **Windows (exe/installer)**: [packaging/windows/](packaging/windows/)

Build with `bash packaging/build-all.sh` (or target-specific scripts).

### Common Pitfalls

1. **Calling yt-dlp from the GUI thread** → Use `ExtractionService` instead.
2. **Mutating frozen dataclasses** → Use `replace()` for transformations.
3. **Hardcoding export formats** → Use the registry; add to `default_exporter_registry()`.
4. **Missing PySide6 check in core modules** → Always use try/except fallbacks for Qt imports outside `ui/`.
5. **Settings not persisting** → Must call `settings_repository.save()` explicitly after changes.

## File Organization

- **Models**: [playlistforge/core/models.py](playlistforge/core/models.py)
- **Errors**: [playlistforge/core/errors.py](playlistforge/core/errors.py)
- **Enums**: [playlistforge/core/enums.py](playlistforge/core/enums.py)
- **Default rules**: [playlistforge/settings/defaults.py](playlistforge/settings/defaults.py)
- **UI icons/themes**: [playlistforge/resources/](playlistforge/resources/)

---

For more details, see [README.md](README.md) and the module docstrings.
