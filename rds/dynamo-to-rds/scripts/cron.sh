#!/bin/bash

cd "$(dirname "$0")"/..

case "$1" in
  daily)
    echo "🕒 [03:00] Running daily diff + reset scripts..."
    python3 scripts/update_hourly_dispatch_pickup_diff.py
    python3 scripts/sync_and_reset_daily_stats.py
    ;;
  dispatch)
    echo "⏱️ [Every 5min] Syncing dispatch counts..."
    python3 scripts/sync_zone_hourly_activity_log.py dispatch_only
    ;;
  pickup)
    echo "⏰ [Hourly] Syncing pickup counts..."
    python3 scripts/sync_zone_hourly_activity_log.py pickup_only
    ;;
  both)
    echo "🌀 [Manual or fallback] Syncing both dispatch and pickup..."
    python3 scripts/sync_zone_hourly_activity_log.py
    ;;
  *)
    echo "❌ Unknown command. Use: daily | dispatch | pickup | both"
    exit 1
    ;;
esac
