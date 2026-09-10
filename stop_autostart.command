#!/bin/bash
cd "$(dirname "$0")"
PLIST_PATH="$HOME/Library/LaunchAgents/com.orineeman.dictationtool.plist"
if [ -f "$PLIST_PATH" ]; then
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
  rm -f "$PLIST_PATH"
  echo "Background auto-start removed."
else
  echo "Auto-start was not installed."
fi
echo "You can still run the tool manually any time with run.command."
read -p "Press Enter to close..."
