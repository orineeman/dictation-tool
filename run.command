#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export HF_HUB_OFFLINE=1
python3 dictation.py
echo ""
echo "(the program stopped - see any error message above)"
read -p "Press Enter to close..."
