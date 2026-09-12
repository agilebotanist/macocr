# Design

## `src/macocr/ocr.py` — engine

```python
LANGS: list[str]        # ["en-US", "fr-FR"] — Vision recognition languages
IMAGE_EXTS: set[str]    # extensions treated as images by the CLI's discovery step

def ocr_image(path) -> str
def ocr_pdf(pdf_path, dpi: int = 200) -> str
def _run_vision(handler) -> str   # internal
```

- `ocr_image` builds a `VNImageRequestHandler` directly from a file URL — no
  intermediate copy or decode step.
- `ocr_pdf` opens the document with PyMuPDF, and for each page renders a
  pixmap at `dpi`, encodes it to PNG bytes in memory (`pix.tobytes("png")`),
  and hands those bytes to a `VNImageRequestHandler`. Nothing is written to
  disk during rendering.
- `_run_vision` is the only place that talks to Vision: it builds one
  `VNRecognizeTextRequest` per call, sets `RecognitionLanguages` and
  `RecognitionLevel` (`.accurate`, not `.fast` — favors quality over speed
  since this is a batch/offline tool, not interactive), runs it synchronously
  via `performRequests_error_`, and takes only the top candidate string per
  observed text region. A non-zero/failed request raises `RuntimeError`
  rather than returning partial results silently.
- Progress for multi-page PDFs is reported with a plain `print()` per page
  (`OCR <name>: page i/n`) — deliberately simple, no progress-bar dependency.

## `src/macocr/cli.py` — argument parsing and discovery

```python
def build_parser() -> argparse.ArgumentParser
def process_file(path: Path, target_dir: Path, dpi: int) -> None
def main(argv=None) -> int
```

- `main()` takes an optional `argv` (defaults to `sys.argv` via argparse) so
  it's directly callable from tests without subprocessing.
- Dispatch logic: if `input` is a directory, iterate its immediate children
  (not recursive), keep only `.pdf` and members of `IMAGE_EXTS`, sort them for
  deterministic ordering, and OCR each; if nothing matched, print a "no
  PDFs or images found" message instead of silently doing nothing. If
  `input` is a single file, OCR just that file regardless of extension
  filtering (the user pointed at it directly).
- Output directory resolution: explicit `-o/--output-dir` always wins;
  otherwise a directory input writes alongside itself, a single-file input
  writes into its parent directory.
- `process_file` is the single place that decides PDF vs. image (by suffix)
  and writes the `<stem>.txt` output — both the single-file and
  directory-batch code paths call through it, so there's one source of
  truth for output naming.

## Extension points

- **More languages:** extend `LANGS` in `ocr.py`. Vision's supported
  language list is queryable via
  `VNRecognizeTextRequest.supportedRecognitionLanguagesAndReturnError_`.
- **More image formats:** extend `IMAGE_EXTS`; anything Vision/Core Graphics
  can decode from a file URL works, since `ocr_image` doesn't special-case
  by extension.
- **Different output format** (e.g. JSON with bounding boxes): Vision's
  `VNRecognizedTextObservation` already exposes `boundingBox` and per-word
  data; `_run_vision` currently discards that and keeps only the joined
  top-candidate strings. A structured-output mode would branch inside
  `_run_vision` (or add a sibling function) rather than reshaping the
  plain-text return type in place, to avoid breaking the existing
  string-returning API that `cli.py` and the test suite depend on.
