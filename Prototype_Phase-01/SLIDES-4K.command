#!/bin/bash
# AI for Architecture - export 4K slides (PNG + PDF)
# Mac: double-click this file (the first time: right-click > Open).
# Linux: bash SLIDES-4K.command      Arguments: see tools/slides_4k.py
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
  echo
  echo "  Python 3 is not installed. Install it from python.org (Lesson 1.1), then run this again."
  echo
  read -r -p "  Press Return to close this window. " _
  exit 1
fi
"$PY" tools/slides_4k.py "$@"
status=$?
echo
read -r -p "  Press Return to close this window. " _
exit $status
