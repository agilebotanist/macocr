"""OCR for PDFs and images using the native macOS Vision framework."""

from .ocr import ocr_image, ocr_pdf

__version__ = "0.1.0"

__all__ = ["ocr_image", "ocr_pdf", "__version__"]
