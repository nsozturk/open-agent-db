#!/bin/bash
# Open-Agent-DB Monthly Sync Runner
# Triggered by macOS launchd or cron on the 1st of every month at 03:00 AM

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export PYTHONUNBUFFERED=1

cd "$PROJECT_DIR"

mkdir -p logs

LOG_FILE="$PROJECT_DIR/logs/monthly_sync_$(date +%Y-%m).log"

echo "==========================================================" >> "$LOG_FILE"
echo "🚀 Open-Agent-DB Monthly Sync Started at $(date)" >> "$LOG_FILE"
echo "==========================================================" >> "$LOG_FILE"

python3 "$PROJECT_DIR/scripts/monthly_sync.py" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Monthly Sync Succeeded at $(date)" >> "$LOG_FILE"
else
    echo "❌ Monthly Sync Failed with code $EXIT_CODE at $(date)" >> "$LOG_FILE"
fi

exit $EXIT_CODE
