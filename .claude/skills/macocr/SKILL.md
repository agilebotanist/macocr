---
name: macocr
description: OCR scanned/image-based PDFs and images on macOS using the native Vision framework, fully offline. Use when the user asks to OCR a file, extract text from a scanned document or photo, or when a PDF's text can't be extracted normally because it's just rendered page images (scanned book, screenshot-based PDF, photographed pages). macOS only.
allowed-tools:
  - Bash
  - Read
---

# macocr — offline OCR via the macOS Vision framework

This skill wraps the `macocr` CLI from this repo. It recognizes text in
images and PDFs entirely on-device (no network calls, no cloud OCR API) using
`VNRecognizeTextRequest`, with `en-US` and `fr-FR` enabled by default (mixed English/French pages work
without configuration). Use `--lang` for other languages, e.g. `--lang ru-RU,en-US`.

**macOS only.** Before using it, confirm the host is Darwin — if not, tell
the user this tool can't run here and stop.

## When to reach for this vs. normal PDF text extraction

Try a normal text-layer extraction first for any PDF (e.g. `pdftotext`, or a
library's text extraction). Only fall back to `macocr` when that comes back
empty or garbled — i.e. the PDF is actually scanned/rendered page images with
no real text layer, or the input is a plain image (screenshot, photo of a
document, PNG/JPG/TIFF/BMP/GIF/HEIC/WebP).

## Checking availability

```
which macocr
```

If missing, it's installable from this repo:

```
pip install /path/to/macocr        # or: pip install -e . from a checkout
```

It depends on `pymupdf` and the `pyobjc-framework-Vision`/`-Quartz`/`-Cocoa`
bundles (declared in `pyproject.toml`); pip resolves those automatically.

## Usage

```
macocr <file-or-directory> [-o OUTPUT_DIR] [--dpi N] [--lang CODES] [--list-langs]
```

- A single image or PDF path OCRs just that file.
- A directory path batch-processes every PDF/image directly inside it
  (non-recursive).
- `-o/--output-dir` controls where the `.txt` output lands; defaults to next
  to the input (or, for a directory input, inside that same directory).
- `--lang` takes comma-separated Vision codes (first preferred); `--list-langs`
  prints the codes supported by this macOS. Unsupported codes are rejected.
- `--dpi` controls the render resolution for PDF pages before OCR (default
  `200`). Raise it (e.g. `300`–`400`) for small/dense print if recognition
  quality looks poor; this costs more time per page.

Each input produces one `<stem>.txt` file. For PDFs, page boundaries are
preserved with `<!-- Page N -->` markers and `---` separators between pages,
so a downstream reader can still tell where each page starts.

## Example

```
macocr "Scanned Report.pdf" --dpi 300 -o ./out
# -> ./out/Scanned Report.txt
```

Read the resulting `.txt` file back (e.g. with the Read tool) to work with
the extracted text — don't re-run OCR on output that already exists unless
the user asks for a re-run (e.g. at a different DPI).
