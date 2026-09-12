# Finder Quick Action: "OCR with macocr"

Adds an "OCR with macocr" entry to Finder's right-click → Quick Actions menu
for PDFs and images. Selecting one or more files runs the installed `macocr`
CLI on each and posts a notification when a file is done (or failed).

It's a thin wrapper: all it does is find the `macocr` binary and run it per
selected file. All real logic lives in the Python package, so this can't
drift from what the CLI does on the command line.

## Prerequisites

`macocr` must be installed and on `PATH` (or in one of the common install
locations the wrapper script checks: `/usr/local/bin`, `/opt/homebrew/bin`,
`~/.local/bin`). From a checkout of this repo:

```
pip install .
```

## Install

```
automation/install.sh
```

This copies `OCR with macocr.workflow` into `~/Library/Services/` and asks
macOS to re-scan its Services registry. The entry should appear under
Finder → right-click a PDF/image → Quick Actions → "OCR with macocr".

If it doesn't show up right away, the Services menu cache can lag — log out
and back in, or relaunch Finder (`killall Finder`).

## Uninstall

```
automation/uninstall.sh
```

## How it's verified

The `.workflow` bundle is plain XML (`Contents/Info.plist` +
`Contents/document.wflow`), which is easy to get subtly wrong by hand. Two
checks back it:

1. `plutil -lint` on both files, confirming they're structurally valid
   property lists.
2. `/System/Library/CoreServices/pbs -dump` (macOS's own Services registry
   tool), confirming the OS itself parses `Info.plist` and registers the
   "OCR with macocr" service for `public.pdf`/`public.image` file types.

If macOS ever changes this format and the Quick Action stops appearing, the
most reliable fix is to open `OCR with macocr.workflow` in Automator.app
directly (double-click it, or `open`), which will show any parse error
immediately, and re-save it from there — Automator always writes a format
its own OS version understands.

## What the wrapper script does

`Contents/document.wflow` embeds a single "Run Shell Script" action
(input passed "as arguments") that, for each selected file:

1. Looks for `macocr` in a few common install locations, then falls back to
   `PATH`.
2. Runs `macocr <file>`, writing `<file-stem>.txt` next to the input (same
   default behavior as running the CLI directly).
3. Posts a macOS notification reporting success or failure for that file.
