"""Command-line interface: file/directory discovery and dispatch to the OCR engine."""

import argparse
from pathlib import Path

from .ocr import IMAGE_EXTS, ocr_image, ocr_pdf


def process_file(path: Path, target_dir: Path, dpi: int) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    out_txt = target_dir / (path.stem + ".txt")
    if path.suffix.lower() == ".pdf":
        text = ocr_pdf(path, dpi=dpi)
    else:
        text = ocr_image(path)
    out_txt.write_text(text, encoding="utf-8")
    print(f"OCR {path.name} -> {out_txt}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OCR images/PDFs with macOS Vision.")
    parser.add_argument("input", help="File or folder containing images/PDFs.")
    parser.add_argument("-o", "--output-dir", help="Directory for .txt outputs (defaults to input location).")
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI for PDF pages (default: 200).")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    in_path = Path(args.input)
    out_dir = Path(args.output_dir) if args.output_dir else None

    if in_path.is_dir():
        target_dir = out_dir if out_dir else in_path
        candidates = sorted(p for p in in_path.iterdir() if p.is_file())
        worked = False
        for candidate in candidates:
            ext = candidate.suffix.lower()
            if ext == ".pdf" or ext in IMAGE_EXTS:
                process_file(candidate, target_dir, args.dpi)
                worked = True
        if not worked:
            print(f"No PDFs or images found in {in_path}")
    else:
        target_dir = out_dir if out_dir else in_path.parent
        process_file(in_path, target_dir, args.dpi)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
