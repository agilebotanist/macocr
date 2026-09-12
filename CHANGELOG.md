# Changelog

## 0.1.0

Initial release.

- `macocr` CLI: OCR a single image/PDF, or batch-process a directory.
- OCR engine backed by the macOS Vision framework (`en-US` + `fr-FR`), PDF
  pages rendered via PyMuPDF.
- Finder Quick Action ("OCR with macocr") for right-click OCR.
- Bundled Claude Code skill (`.claude/skills/macocr`).
- Unit test suite plus an opt-in real-Vision integration test.
