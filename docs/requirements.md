# Requirements

## Functional

| ID | Requirement |
|----|-------------|
| FR1 | OCR a single image file (PNG, JPG, TIFF, BMP, GIF, HEIC, WebP) and produce plain text. |
| FR2 | OCR a multi-page PDF, preserving page boundaries in the output (`<!-- Page N -->` markers, `---` separators between pages). |
| FR3 | Batch-process every PDF/image in a directory in one invocation. |
| FR4 | Recognize mixed English/French text on the same page without per-file language configuration. |
| FR5 | Provide a CLI with a configurable render DPI (for PDF rasterization) and a configurable output directory. |
| FR6 | Provide a macOS Finder right-click ("Quick Action") entry point so a user can OCR a file without opening a terminal. |

## Non-functional

| ID | Requirement |
|----|-------------|
| NFR1 | Runs entirely offline/on-device — no network calls, no cloud OCR API, no data leaves the machine. |
| NFR2 | macOS-only by design (depends on the Vision framework via PyObjC); no Linux/Windows support is attempted. |
| NFR3 | Installable as a normal Python package (`pip install .`) exposing a `macocr` console command. |
| NFR4 | Redistributable: MIT-licensed, no personal data or sample documents committed to the repository. |
| NFR5 | Output format is plain UTF-8 text, one `.txt` file per input, named after the input's stem. |
