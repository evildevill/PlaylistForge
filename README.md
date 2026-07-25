# PlaylistForge

**Extract • Clean • Transform • Export**

PlaylistForge is a modern desktop utility for extracting YouTube playlist metadata, cleaning video titles, previewing videos, and exporting structured data in formats that work well for documents, spreadsheets, applications, and databases.

It is built with Python 3.12+, PySide6, and yt-dlp. The project is intentionally modular: the GUI does not call yt-dlp directly, exporters are plugin-style classes, and the cleaning system is a typed rule pipeline.

> Screenshots will be added as the visual polish pass matures: main window, cleaning panel, export panel, settings dialog, and large playlist preview.

## Current Status

PlaylistForge currently includes a working application foundation:

- PySide6 desktop shell.
- Background extraction service architecture.
- yt-dlp wrapper.
- Typed playlist/video/settings/export/cleaning models.
- Title cleaning rules.
- JSON, TXT, CSV, Markdown, HTML, Excel, and clipboard export helpers.
- Settings persistence.
- Rotating logs.
- Unit tests for core behavior.
- PyInstaller packaging scaffold.

Some advanced UI polish features are intentionally staged for later hardening, including thumbnail caching, richer column visibility controls, and polished cleaning preset editing.

## Features

- Paste one or many YouTube playlist URLs.
- Validate and normalize playlist URLs.
- Extract metadata without downloading videos.
- Run extraction in a background worker so the UI stays responsive.
- Cancel extraction.
- Preview playlist metadata:
  - playlist title
  - channel
  - playlist ID
  - video count
  - total duration
  - extraction time
- Preview videos in a sortable, searchable table.
- Copy selected table rows.
- Clean titles using ordered rules:
  - remove literal phrases
  - regex replacement support
  - collapse repeated spaces
  - trim whitespace
  - preserve original titles
  - undo/reset cleaning
- Export selected fields to:
  - JSON
  - TXT
  - CSV
  - Markdown
  - HTML
  - Excel
  - clipboard text
- Remember:
  - theme
  - window size
  - recent playlist URLs
  - favorites
  - last export directory
  - export preferences
  - cleaning rules

## Requirements

- Python 3.12 or newer
- pip
- Internet access for installing dependencies
- A desktop environment capable of running Qt applications

Runtime dependencies:

- `PySide6`
- `yt-dlp`
- `openpyxl`

Development dependencies:

- `pytest`
- `pytest-cov`
- `ruff`
- `mypy`
- `pyinstaller`

## Project Layout

```text
playlistforge/
  app.py                     Application bootstrap
  __main__.py                python -m playlistforge entry point

  core/                      Dataclasses, enums, errors, shared results
  extraction/                URL validation, yt-dlp client, parser, Qt worker
  cleaning/                  Cleaning rule engine, presets, undo stack
  export/                    Export plugin interface and exporters
  settings/                  JSON settings repository
  history/                   Recent/favorite playlist helpers
  logging/                   Rotating logging setup
  ui/                        PySide6 windows, widgets, table models, dialogs

tests/                       Unit tests
packaging/pyinstaller/       PyInstaller spec
```

## Run Locally

Clone or open the repository, then run these commands from the project root.

Linux and macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m playlistforge
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m playlistforge
```

You can also run the installed GUI script:

```bash
playlistforge
```

## How To Use

1. Launch PlaylistForge.
2. Paste one or more YouTube playlist URLs into the large input box.
3. Click **Extract**.
4. Watch extraction progress in the status panel.
5. Search, sort, select, and copy rows in the video table.
6. Use **Clean Titles** to remove unwanted words or normalize spacing.
7. Choose an export format from the **Export** panel.
8. Click **Export file** and choose a destination.
9. Use **Copy** when you want clipboard-ready tabular output.

Example playlist URL formats:

```text
https://www.youtube.com/playlist?list=PLxxxxxxxxxxxx
https://www.youtube.com/watch?v=VIDEO_ID&list=PLxxxxxxxxxxxx
```

## Exported JSON

The JSON exporter creates app/database-friendly camelCase keys:

```json
[
  {
    "lecture": 1,
    "title": "Introduction",
    "videoId": "j8QdcI71-S4",
    "watchUrl": "https://www.youtube.com/watch?v=j8QdcI71-S4",
    "embedUrl": "https://www.youtube.com/embed/j8QdcI71-S4",
    "thumbnail": "https://i.ytimg.com/vi/j8QdcI71-S4/hqdefault.jpg"
  }
]
```

The selected export fields are controlled by `ExportOptions` and can be exposed more deeply in the UI as the app matures.

## Settings And Logs

Settings are stored as JSON in the user config directory:

- Linux: `~/.config/PlaylistForge/settings.json`
- macOS: `~/Library/Application Support/PlaylistForge/settings.json`
- Windows: `%APPDATA%\PlaylistForge\settings.json`

Logs are stored in the user state/log directory:

- Linux: `~/.local/state/PlaylistForge/logs/`
- macOS: `~/Library/Logs/PlaylistForge/logs/`
- Windows: `%LOCALAPPDATA%\PlaylistForge\logs\`

PlaylistForge writes:

- `playlistforge.log`
- `playlistforge.error.log`

Tracebacks are written to logs, not shown directly in user dialogs.

## Development Checks

Run unit tests:

```bash
pytest -q
```

Run syntax compilation:

```bash
python -m compileall -q playlistforge tests
```

Run Ruff after installing development dependencies:

```bash
ruff check .
```

Run mypy:

```bash
mypy playlistforge
```

## Building Executables

Install development dependencies first:

```bash
python -m pip install -e ".[dev]"
```

Linux:

```bash
pyinstaller packaging/pyinstaller/playlistforge.spec --clean --noconfirm
```

Windows PowerShell:

```powershell
pyinstaller packaging\pyinstaller\playlistforge.spec --clean --noconfirm
```

macOS:

```bash
pyinstaller packaging/pyinstaller/playlistforge.spec --clean --noconfirm
```

Build artifacts are written to `dist/`.

## Architecture Notes

The main architecture rule is separation of concerns:

- UI code owns presentation and user interaction.
- Extraction code owns yt-dlp integration.
- Cleaning code owns title transformations.
- Export code owns output generation.
- Settings code owns persistence.
- Core models define the shared language of the application.

Important modules:

- `playlistforge/extraction/yt_dlp_client.py`: the only module that imports `yt_dlp`.
- `playlistforge/extraction/worker.py`: background extraction worker.
- `playlistforge/ui/main_window.py`: application composition and signal wiring.
- `playlistforge/export/base.py`: exporter plugin contract.
- `playlistforge/export/registry.py`: exporter registration.
- `playlistforge/cleaning/engine.py`: title-cleaning pipeline.
- `playlistforge/settings/repository.py`: cross-platform settings persistence.

## Troubleshooting

### PySide6 is missing

Install the project with runtime or development dependencies:

```bash
python -m pip install -e ".[dev]"
```

### Extraction fails with rate limiting

YouTube may return HTTP 429 when too many requests are made. Wait and try again later.

### yt-dlp warns about a missing JavaScript runtime

Recent yt-dlp versions may warn that no supported JavaScript runtime is installed. PlaylistForge suppresses repeated copies of the same warning, but the first warning is still logged because some YouTube extraction paths may need a runtime.

Install one supported by yt-dlp, such as Deno, then restart PlaylistForge:

```bash
deno --version
```

If `deno` is available on `PATH`, yt-dlp can use it automatically.

### Playlist is private

PlaylistForge cannot extract private playlists unless yt-dlp can access them. Public playlist URLs work best.

### Excel export fails

Install `openpyxl`:

```bash
python -m pip install openpyxl
```

### GUI does not start on Linux

Make sure Qt platform dependencies are available for your desktop environment. On headless servers, the GUI cannot run without a display server.

## FAQ

### Does PlaylistForge download videos?

No. It extracts metadata only.

### Is this just a yt-dlp wrapper?

No. yt-dlp is isolated inside the extraction service. PlaylistForge adds typed models, a GUI, cleaning, previews, settings, history, and exporter plugins.

### Can I add a new exporter?

Yes. Create a class implementing `Exporter`, then register it in `default_exporter_registry()`.

### Can I use the core without the GUI?

Yes. The cleaning, exporting, settings, validation, and parsing layers are independent from PySide6.

## Contributing

1. Keep changes focused.
2. Add tests for non-GUI behavior.
3. Keep GUI code out of extraction/export/cleaning modules.
4. Run:

```bash
python -m compileall -q playlistforge tests
pytest -q
ruff check .
```

5. Document user-facing behavior in this README.

## License

MIT