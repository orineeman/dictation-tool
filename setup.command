#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Local dictation tool - setup ==="
echo ""

if ! command -v python3 &>/dev/null; then
  echo "python3 not found."
  echo "Install it first from https://www.python.org/downloads/ and then run this file again."
  read -p "Press Enter to close..."
  exit 1
fi

echo "Python found: $(python3 --version)"
echo ""

if ! command -v ffmpeg &>/dev/null; then
  echo "ffmpeg not found - required for audio processing."
  if command -v brew &>/dev/null; then
    echo "Installing ffmpeg via Homebrew (this can take a few minutes)..."
    brew install ffmpeg
  else
    echo ""
    echo "Homebrew is not installed, so ffmpeg can't be installed automatically."
    echo "1. Install Homebrew first: open https://brew.sh and follow the instructions (paste the command shown there into Terminal)."
    echo "2. Then run: brew install ffmpeg"
    echo "3. Then run this setup.command again."
    read -p "Press Enter to close..."
    exit 1
  fi
else
  echo "ffmpeg found: $(command -v ffmpeg)"
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Installing dependencies (this can take a few minutes)..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo ""
echo "=== Setup complete ==="
echo "Starting the tool now."
echo "On first run macOS will ask for a few permissions (Microphone / Accessibility / Input Monitoring)."
echo "Please click Allow on each - the tool needs them to work."
echo "The speech model (~1.6GB) also downloads on first run - this can take a few minutes."
echo ""
python3 dictation.py

echo ""
read -p "Press Enter to close..."
