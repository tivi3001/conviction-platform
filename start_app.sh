#!/bin/bash

# Conviction Trading Platform - Launch Script with Passcode Authentication

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

source venv/bin/activate
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Require passcode authentication before proceeding
echo "🔐 Conviction Trading Platform"
python passcode_auth.py
if [ $? -ne 0 ]; then
    echo "❌ Access denied. Exiting."
    exit 1
fi

echo "✅ Starting monitoring systems..."

# Launch GUI (which spawns background daemon)
python gui/app.py
