"""Command-line interface: file/directory discovery and dispatch to the OCR engine."""

import argparse
from pathlib import Path

from .ocr import IMAGE_EXTS, ocr_image, ocr_pdf, parse_langs, supported_languages


def process_file(path: Path, target_dir: Path, dpi: int, langs=None) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    out_txt = target_dir / (path.stem + ".txt")
    if path.suffix.lower() == ".pdf":
        text = ocr_pdf(path, dpi=dpi, langs=langs)
    else:
        text = ocr_image(path, langs=langs)
    out_txt.write_text(text, encoding="utf-8")
    print(f"OCR {path.name} -> {out_txt}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OCR images/PDFs with macOS Vision.")
    parser.add_argument("input", nargs="?", help="File or folder containing images/PDFs.")
    parser.add_argument("-o", "--output-dir", help="Directory for .txt outputs (defaults to input location).")
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI for PDF pages (default: 200).")
    parser.add_argument(
        "--lang",
        help="Comma-separated Vision language codes, first is preferred "
        "(default: en-US,fr-FR). Example for Russian: --lang ru-RU,en-US",
    )
    parser.add_argument(
        "--list-langs",
        action="store_true",
        help="Print the recognition languages supported by this macOS and exit.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_langs:
        print("\n".join(supported_languages()))
        return 0
    if not args.input:
        parser.error("the following arguments are required: input")

    langs = None
    if args.lang:
        langs = parse_langs(args.lang)
        unsupported = [lang for lang in langs if lang not in supported_languages()]
        if not langs or unsupported:
            parser.error(
                f"unsupported language(s): {', '.join(unsupported) or args.lang!r}. "
                "Use --list-langs to see the supported codes."
            )

    in_path = Path(args.input)
    out_dir = Path(args.output_dir) if args.output_dir else None

    if in_path.is_dir():
        target_dir = out_dir if out_dir else in_path
        candidates = sorted(p for p in in_path.iterdir() if p.is_file())
        worked = False
        for candidate in candidates:
            ext = candidate.suffix.lower()
            if ext == ".pdf" or ext in IMAGE_EXTS:
                process_file(candidate, target_dir, args.dpi, langs)
                worked = True
        if not worked:
            print(f"No PDFs or images found in {in_path}")
    else:
        target_dir = out_dir if out_dir else in_path.parent
        process_file(in_path, target_dir, args.dpi, langs)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
