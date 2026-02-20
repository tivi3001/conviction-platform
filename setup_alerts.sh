#!/bin/bash

# Setup macOS launchd plist for auto-start background daemon

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="$HOME/Library/LaunchAgents/com.conviction-platform.alerts.plist"

echo "📋 Setting up auto-start daemon..."

cat > "$PLIST_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.conviction-platform.alerts</string>
    <key>Program</key>
    <string>SCRIPT_DIR_PLACEHOLDER/venv/bin/python</string>
    <key>ProgramArguments</key>
    <array>
        <string>SCRIPT_DIR_PLACEHOLDER/background_daemon_alerts.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>SCRIPT_DIR_PLACEHOLDER</string>
    <key>StandardErrorPath</key>
    <string>/var/log/conviction-alerts-error.log</string>
    <key>StandardOutPath</key>
    <string>/var/log/conviction-alerts.log</string>
</dict>
</plist>
EOF

# Replace placeholder with actual script directory
sed -i '' "s|SCRIPT_DIR_PLACEHOLDER|$SCRIPT_DIR|g" "$PLIST_FILE"

# Load the plist
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Auto-start daemon configured"
    echo "📁 Plist: $PLIST_FILE"
    echo "📝 Logs: /var/log/conviction-alerts.log"
else
    echo "❌ Failed to load plist"
    exit 1
fi
