#!/usr/bin/env bash
# Builds the site and opens it at http://localhost:8000
cd "$(dirname "$0")"
echo
echo "  Folder: $(pwd)"
echo
python3 engine/build.py --serve
