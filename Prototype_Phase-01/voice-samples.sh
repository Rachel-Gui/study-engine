#!/usr/bin/env bash
# Hear the course narration paragraph in several voices, then choose one.
# Writes dist/voice-samples/index.html with a player per voice.
cd "$(dirname "$0")"
echo
echo "  Folder: $(pwd)"
echo "  Rendering the sample paragraph in each shortlisted voice (needs internet)..."
echo
if ! python3 engine/voice_samples.py "$@"; then
  echo; echo "  Could not render the samples. Is edge-tts installed?   pip install edge-tts"; exit 1
fi
echo
if command -v open >/dev/null; then open dist/voice-samples/index.html; elif command -v xdg-open >/dev/null; then xdg-open dist/voice-samples/index.html; fi
echo "  To use a voice, edit course.yml:   voice: \"en-US-JennyNeural\"   (the line is shown under each sample)"
