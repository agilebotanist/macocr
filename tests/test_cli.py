"""Unit tests for macocr.cli — the OCR engine itself is mocked out."""

from macocr import cli


def test_single_pdf_file_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ocr_pdf", lambda path, dpi=200: "PDFTEXT")
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"")

    assert cli.main([str(pdf)]) == 0

    out = tmp_path / "doc.txt"
    assert out.read_text() == "PDFTEXT"


def test_single_image_file_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ocr_image", lambda path: "IMGTEXT")
    img = tmp_path / "photo.png"
    img.write_bytes(b"")

    assert cli.main([str(img)]) == 0

    out = tmp_path / "photo.txt"
    assert out.read_text() == "IMGTEXT"


def test_directory_batch_dispatch_skips_unrelated_files(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ocr_pdf", lambda path, dpi=200: f"PDF:{path.name}")
    monkeypatch.setattr(cli, "ocr_image", lambda path: f"IMG:{path.name}")

    (tmp_path / "a.pdf").write_bytes(b"")
    (tmp_path / "b.png").write_bytes(b"")
    (tmp_path / "notes.txt").write_text("not an input")

    assert cli.main([str(tmp_path)]) == 0

    assert (tmp_path / "a.txt").read_text() == "PDF:a.pdf"
    assert (tmp_path / "b.txt").read_text() == "IMG:b.png"
    assert (tmp_path / "notes.txt").read_text() == "not an input"


def test_output_dir_override(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "ocr_image", lambda path: "IMGTEXT")
    img = tmp_path / "photo.jpg"
    img.write_bytes(b"")
    out_dir = tmp_path / "out"

    assert cli.main([str(img), "-o", str(out_dir)]) == 0

    assert (out_dir / "photo.txt").read_text() == "IMGTEXT"
    assert not (tmp_path / "photo.txt").exists()


def test_empty_directory_prints_message(tmp_path, capsys):
    (tmp_path / "notes.txt").write_text("nothing to OCR here")

    assert cli.main([str(tmp_path)]) == 0

    assert "No PDFs or images found" in capsys.readouterr().out


def test_dpi_argument_is_passed_through(tmp_path, monkeypatch):
    captured = {}

    def fake_ocr_pdf(path, dpi=200):
        captured["dpi"] = dpi
        return "PDFTEXT"

    monkeypatch.setattr(cli, "ocr_pdf", fake_ocr_pdf)
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"")

    cli.main([str(pdf), "--dpi", "350"])

    assert captured["dpi"] == 350
