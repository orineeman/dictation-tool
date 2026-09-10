#!/bin/bash
set -e
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.orineeman.dictationtool.plist"

if [ ! -x "$PROJECT_DIR/venv/bin/python3" ]; then
  echo "venv not found - please run setup.command first."
  read -p "Press Enter to close..."
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$PROJECT_DIR/logs"

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.orineeman.dictationtool</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/venv/bin/python3</string>
        <string>$PROJECT_DIR/dictation.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>ThrottleInterval</key>
    <integer>10</integer>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/dictation.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/dictation.err.log</string>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
        <key>HF_HUB_OFFLINE</key>
        <string>1</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
PLIST

launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo "=== Installed ==="
echo "The tool will now start automatically at login and run quietly in the background (no Terminal window)."
echo "It just started now too - try it (hold Option, speak, release)."
echo ""
echo "Logs (if something doesn't work): $PROJECT_DIR/logs/dictation.log and dictation.err.log"
echo ""
echo "IMPORTANT: since it's no longer running through Terminal, macOS may ask AGAIN for permissions"
echo "(Microphone / Accessibility / Input Monitoring) - this time for this exact program:"
echo "  $PROJECT_DIR/venv/bin/python3"
echo "If it doesn't respond to the hotkey, open System Settings > Privacy & Security, and in each of"
echo "Microphone / Accessibility / Input Monitoring, click + and add that exact file (Cmd+Shift+G in"
echo "the file picker to paste the path above), then run this file again."
echo ""
read -p "Press Enter to close..."
