"""OCR engine backed by the macOS Vision framework.

Renders PDF pages with PyMuPDF and recognizes text in both images and
rendered pages with ``VNRecognizeTextRequest``.
"""

from pathlib import Path

from Foundation import NSData, NSDictionary, NSURL
import Vision
import pymupdf

# Default: allow mixed English/French pages. Override per call (``langs=``)
# or on the command line (``--lang``) for other scripts, e.g. ``ru-RU``.
DEFAULT_LANGS = ["en-US", "fr-FR"]
LANGS = DEFAULT_LANGS  # backward-compatible alias
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".heic", ".webp"}


def parse_langs(value) -> list:
    """Split a comma-separated language string (``"ru-RU,en-US"``) into a list."""
    return [part.strip() for part in str(value).split(",") if part.strip()]


def supported_languages() -> list:
    """Languages the installed Vision framework can recognize (accurate level)."""
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    langs, error = req.supportedRecognitionLanguagesAndReturnError_(None)
    if error is not None or langs is None:
        raise RuntimeError(f"Could not list supported languages: {error}")
    return [str(lang) for lang in langs]


def _run_vision(handler, langs=None) -> str:
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLanguages_(list(langs) if langs else LANGS)
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)

    success, error = handler.performRequests_error_([req], None)
    if not success:
        raise RuntimeError(f"OCR failed: {error}")

    texts = []
    for obs in req.results():
        candidate = obs.topCandidates_(1).firstObject()
        if candidate is None:
            continue
        texts.append(candidate.string())
    return "\n".join(texts)


def ocr_image(path, langs=None) -> str:
    """Recognize text in a single image file.

    ``langs`` is a list of Vision language codes (default: ``DEFAULT_LANGS``).
    """
    url = NSURL.fileURLWithPath_(str(path))
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(url, NSDictionary.dictionary())
    return _run_vision(handler, langs)


def ocr_pdf(pdf_path, dpi: int = 200, langs=None) -> str:
    """Rasterize each page of a PDF and recognize text on it.

    Pages are joined with ``---`` separators and each page is preceded by
    an HTML comment marker (``<!-- Page N -->``) so page boundaries survive
    in the plain-text output.
    """
    pdf_path = Path(pdf_path)
    parts = []
    with pymupdf.open(str(pdf_path)) as doc:
        total = len(doc)
        for idx, page in enumerate(doc, start=1):
            print(f"OCR {pdf_path.name}: page {idx}/{total}")
            pix = page.get_pixmap(dpi=dpi)
            data = pix.tobytes("png")
            nsdata = NSData.dataWithBytes_length_(data, len(data))
            handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(nsdata, NSDictionary.dictionary())
            page_text = _run_vision(handler, langs)
            parts.append(f"<!-- Page {idx} -->\n{page_text}")
    return "\n\n---\n\n".join(parts)
