"""Opt-in integration test that makes a real call into the Vision framework.

Run with: pytest -m integration
"""

import pymupdf
import pytest

from macocr.ocr import ocr_pdf

pytestmark = pytest.mark.integration


def test_ocr_pdf_recognizes_known_text(tmp_path):
    pdf_path = tmp_path / "known_text.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 144), "HELLO INTEGRATION TEST 12345", fontsize=24)
    doc.save(str(pdf_path))
    doc.close()

    result = ocr_pdf(pdf_path)

    upper = result.upper()
    for word in ("HELLO", "INTEGRATION", "TEST", "12345"):
        assert word in upper
