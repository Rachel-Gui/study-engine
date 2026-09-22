#!/usr/bin/env bash
# Renders the narrated MP4 into dist/course.mp4.
# First run takes a while. After that, only changed scenes re-render.
cd "$(dirname "$0")"

echo
echo "  Folder: $(pwd)"
echo
echo "  Step 1 of 2 - checking what is installed"
echo "  ---------------------------------------"
if ! python3 engine/build.py --doctor; then
  echo
  echo "  =========================================================="
  echo "   NOT READY. Install everything marked MISSING above."
  echo
  echo "   ffmpeg is a PROGRAM, not a Python package:"
  echo "       Mac    brew install ffmpeg"
  echo "       Linux  sudo apt install ffmpeg"
  echo
  echo "   Nothing was rendered."
  echo "  =========================================================="
  exit 1
fi

echo
echo "  Step 2 of 2 - rendering at 4K. This takes a while."
echo "  (quick 1080p preview:  python3 engine/build.py --video --engine edge --quality 1080p)"
echo "  -------------------------------------------"
if ! python3 engine/build.py --video --engine edge "$@"; then
  echo
  echo "  RENDER FAILED. Read the message above - it says why."
  exit 1
fi

echo
echo "  =========================================================="
echo "   DONE. The video is at:  $(pwd)/dist/course.mp4"
echo "  =========================================================="
