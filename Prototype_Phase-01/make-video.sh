#!/usr/bin/env bash
# Renders one narrated, animated MP4 per lesson (42 videos, 4-8 minutes each)
# into dist/video/, and a narration script per video into dist/scripts/.
# Each video follows its storyboard: content/<module>/<lesson>.video.md.
# First run takes a while. After that, only changed scenes re-render.
# Add --modules to also join each module into one file, --course for one big file.
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
echo "  Step 2 of 2 - rendering one video per lesson at 4K. This takes a while."
echo "  (one lesson:           python3 engine/make_videos.py --engine edge --episode 2.8)"
echo "  (quick 1080p preview:  python3 engine/make_videos.py --engine edge --quality 1080p)"
echo "  (one file per module:  ./make-video.sh --modules)"
echo "  -------------------------------------------"
if ! python3 engine/make_videos.py --engine edge "$@"; then
  echo
  echo "  RENDER FAILED. Read the message above - it says why."
  exit 1
fi

echo
echo "  =========================================================="
echo "   DONE. Videos:   $(pwd)/dist/video/"
echo "         Scripts:  $(pwd)/dist/scripts/"
echo "  =========================================================="
