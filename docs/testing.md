# Testing

## Test pyramid

- **Unit tests** (`tests/test_ocr.py`, `tests/test_cli.py`) — run by default,
  fast, no real Vision calls. They monkeypatch the Vision/Foundation
  boundary (or `ocr_image`/`ocr_pdf` themselves for CLI tests) so behavior is
  verified deterministically without depending on OCR accuracy or timing.
- **One integration test** (`tests/test_integration.py`, marked
  `@pytest.mark.integration`) — makes a real call into the Vision framework.
  It generates a small PDF with known text using PyMuPDF (`page.insert_text`,
  then rasterized the same way `ocr_pdf` does), runs the real `ocr_pdf`, and
  asserts the recognized text contains the expected words. This is an
  opt-in, not-in-default-run check that the actual OS integration still
  works after a macOS/PyObjC/Vision update — it does not assert exact
  character-for-character accuracy, only that the known words show up
  somewhere in the output, since OCR output can vary slightly by OS version.

## Running

```
pytest                 # unit tests only (default; see addopts in pyproject.toml)
pytest -m integration  # the real-Vision test, run manually or in a macOS CI job
pytest -m ""           # everything
```

## What's mocked vs. real

| Test file | Vision calls | PyMuPDF calls |
|---|---|---|
| `test_ocr.py` | mocked (`Vision.VNRecognizeTextRequest`/`VNImageRequestHandler` monkeypatched with fakes) | real, against a tiny PDF generated on the fly |
| `test_cli.py` | not reached — `ocr_image`/`ocr_pdf` themselves are monkeypatched | not reached |
| `test_integration.py` | real | real |

`tests/conftest.py` skips the `integration` marker automatically when not
running on Darwin (Vision isn't importable elsewhere), independent of the
`pyproject.toml` default that already excludes it from a plain `pytest` run.

## Known limitations

- No exact-accuracy assertions against Vision's output — OCR results can
  shift slightly across macOS versions, and pinning exact strings would make
  the suite brittle for no real benefit.
- The integration test only covers the PDF path (`ocr_pdf`); it doesn't
  separately re-verify `ocr_image`, since both funnel through the same
  `_run_vision` — the thing being checked is "Vision is reachable and
  returns sane text," not per-entry-point behavior (that's what the unit
  tests already cover with mocks).
