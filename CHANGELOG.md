# Changelog

## Unreleased

- `--lang` selects Vision recognition languages (comma-separated, validated
  against the languages the installed macOS supports); defaults unchanged
  (`en-US`, `fr-FR`).
- `--list-langs` prints the supported languages.
- Library API: `ocr_image(path, langs=None)`, `ocr_pdf(path, dpi=200, langs=None)`,
  `parse_langs`, `supported_languages`.

## 0.1.0

Initial release.

- `macocr` CLI: OCR a single image/PDF, or batch-process a directory.
- OCR engine backed by the macOS Vision framework (`en-US` + `fr-FR`), PDF
  pages rendered via PyMuPDF.
- Finder Quick Action ("OCR with macocr") for right-click OCR.
- Bundled Claude Code skill (`.claude/skills/macocr`).
- Unit test suite plus an opt-in real-Vision integration test.
