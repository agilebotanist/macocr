# macocr

Offline OCR for PDFs and images on macOS, using the native Vision framework
(`VNRecognizeTextRequest`) — no cloud API, no network calls, no extra OCR
engine to install. Recognizes mixed English/French text out of the box.

## Requirements

- macOS (Vision framework is not available on other platforms)
- Python 3.9+

## Install

```
pip install .
```

This installs the `macocr` console command along with its dependencies
(PyMuPDF for PDF rendering; `pyobjc-framework-Vision`/`-Quartz`/`-Cocoa` for
the Vision framework bindings).

## Usage

```
macocr <file-or-directory> [-o OUTPUT_DIR] [--dpi N]
```

- Point it at a single PDF or image to OCR just that file.
- Point it at a directory to batch-OCR every PDF/image directly inside it.
- `-o/--output-dir` sets where `.txt` output goes (defaults to next to the
  input).
- `--dpi` controls PDF page render resolution before OCR (default `200`).

Each input produces one `<stem>.txt` file. PDF output keeps page boundaries
with `<!-- Page N -->` markers and `---` separators between pages.

```
macocr "Scanned Report.pdf" --dpi 300 -o ./out
# -> ./out/Scanned Report.txt
```

## Finder Quick Action (right-click → OCR)

See [automation/README.md](automation/README.md) — `automation/install.sh`
adds an "OCR with macocr" entry to Finder's right-click menu for PDFs and
images.

## Claude Code skill

This repo ships a bundled skill at
[.claude/skills/macocr/SKILL.md](.claude/skills/macocr/SKILL.md), so Claude
Code sessions opened in a checkout of this repo can drive the CLI directly
when asked to OCR a file.

## Documentation

- [docs/requirements.md](docs/requirements.md) — functional/non-functional requirements
- [docs/architecture.md](docs/architecture.md) — component overview and key design decisions
- [docs/design.md](docs/design.md) — module-level API and extension points
- [docs/testing.md](docs/testing.md) — test strategy and how to run the suite

## Development

```
pip install -e ".[dev]"
pytest                 # unit tests (fast, no real OCR calls)
pytest -m integration  # opt-in test that makes a real Vision call
```

## License

MIT — see [LICENSE](LICENSE).
