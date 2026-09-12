# Architecture (ARD)

## Component overview

```
                 ┌─────────────┐
 Finder (right-  │ Quick Action │  shells out to the installed
 click) ────────>│  .workflow   │  `macocr` console script
                 └─────────────┘
                        │
                        v
┌────────────┐   ┌────────────┐   ┌─────────────┐   ┌──────────────────┐
│   argv     │──>│  cli.py    │──>│   ocr.py    │──>│ Vision.framework │
│ (terminal  │   │ (parse,    │   │ (rasterize  │   │ (VNRecognizeText │
│  or Quick  │   │  discover  │   │  PDF pages  │   │  Request, on-    │
│  Action)   │   │  files)    │   │  via PyMuPDF│   │  device, offline)│
└────────────┘   └────────────┘   └─────────────┘   └──────────────────┘
                                          │
                                          v
                                  <stem>.txt output
```

- **`cli.py`** owns argument parsing and file/directory discovery (single file vs. batch directory), and decides the output path. It has no OCR logic of its own.
- **`ocr.py`** is the engine: `ocr_image()` hands an image straight to Vision; `ocr_pdf()` rasterizes each page with PyMuPDF to a PNG in memory, then hands that to Vision. Both funnel through `_run_vision()`, which configures a single `VNRecognizeTextRequest` and joins the top text candidate per observation.
- **Automator Quick Action** is a thin shell wrapper with no logic of its own — it exists only to put the `macocr` command on the Finder right-click menu. All actual behavior lives in the Python package, so the automation layer can't drift from the CLI.

## Key decisions

- **macOS Vision framework, not Tesseract or a cloud OCR API.** Vision ships with the OS, requires no extra binary/model download, runs fully offline, and its accuracy on printed text is comparable to or better than Tesseract for this use case. The cost is platform lock-in: this tool only runs on macOS. That trade-off is accepted deliberately (see NFR2 in [requirements.md](requirements.md)).
- **PyMuPDF (`fitz`) for PDF rasterization.** Vision only recognizes text in images, not PDF page content directly, so pages are rendered to PNG bytes in memory (no temp files) at a configurable DPI before being handed to Vision. PyMuPDF was already in use in the original script and is a lightweight, fast, dependency-light renderer.
- **Automator Quick Action over a droplet `.app`.** A Quick Action (Service) appears directly in Finder's top-level right-click menu under "Quick Actions," which is the most discoverable placement for "right-click → OCR this." A droplet application (built with `osacompile`) would only be reachable via "Open With," one menu level deeper, and semantically implies "opening" the file rather than processing it. The trade-off is that the Quick Action's `.workflow` bundle is plain XML that's easy to get subtly wrong; see [automation/README.md](../automation/README.md) for how it's validated and how to fall back to editing it in Automator directly.
- **Plain-text output with HTML-comment page markers**, not a structured format (JSON, Markdown headers, etc.). This keeps output trivially readable/greppable while still letting page boundaries be recovered by a downstream tool if needed.

## Constraints

- Requires macOS (PyObjC + Vision.framework are not available on Linux/Windows).
- Requires the Automator Services subsystem for the Quick Action; there is no equivalent shell integration shipped for other platforms.
- Vision's on-device recognition quality depends on the `RecognitionLanguages` list (`en-US`, `fr-FR` today); recognizing additional languages requires extending `LANGS` in [`src/macocr/ocr.py`](../src/macocr/ocr.py).
