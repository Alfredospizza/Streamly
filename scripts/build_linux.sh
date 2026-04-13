#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

rm -rf build dist release
mkdir -p release

python -m pip install -r requirements-build.txt

pyinstaller \
  --noconfirm \
  --clean \
  --name Streamly \
  --windowed \
  --onedir \
  --hidden-import PIL.ImageTk \
  --hidden-import PIL._tkinter_finder \
  --hidden-import PIL._imagingtk \
  --add-data "assets:assets" \
  streamly_gui.py

mkdir -p dist/Streamly/tools/linux
mkdir -p dist/Streamly/assets

if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  cp "$(command -v ffmpeg)" dist/Streamly/tools/linux/
  cp "$(command -v ffprobe)" dist/Streamly/tools/linux/
else
  echo "[WARN] ffmpeg/ffprobe non trovati: includili manualmente in dist/Streamly/tools/linux/"
fi

cp assets/streamly.svg dist/Streamly/assets/
if [ -f assets/streamly.ico ]; then cp assets/streamly.ico dist/Streamly/assets/; fi
cp README.md LICENSE scripts/install_linux.sh dist/Streamly/
chmod +x dist/Streamly/install_linux.sh
chmod +x dist/Streamly/Streamly

tar -C dist -czf release/Streamly-linux-portable.tar.gz Streamly

printf "Build Linux completata. Artifact: release/Streamly-linux-portable.tar.gz\n"
