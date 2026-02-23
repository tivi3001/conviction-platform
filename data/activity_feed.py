"""
Activity Feed System

Manages logging and retrieval of conviction changes.
Provides a feed of recent activity showing what changed and why.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from .conviction_history import ActivityLogEntry


class ActivityFeed:
    """Manages activity feed with JSON persistence"""

    def __init__(self, activity_dir: Optional[str] = None):
        """Initialize activity feed"""
        if activity_dir is None:
            activity_dir = os.path.join(
                os.path.dirname(__file__), "..", "data", "activity_feed"
            )

        self.activity_dir = Path(activity_dir)
        self.activity_dir.mkdir(parents=True, exist_ok=True)

        # Main activity feed file
        self.main_feed_file = self.activity_dir / "activity_feed.json"

    def log_activity(
        self,
        symbol: str,
        action: str,
        old_value: float,
        new_value: float,
        reason: str,
        tier: str,
    ) -> str:
        """Log a conviction change event"""
        entry_id = str(uuid4())
        magnitude = abs(new_value - old_value)

        entry = ActivityLogEntry(
            id=entry_id,
            timestamp=datetime.now(),
            symbol=symbol,
            action=action,
            old_value=old_value,
            new_value=new_value,
            magnitude=magnitude,
            reason=reason,
            tier=tier,
        )

        # Append to main feed file
        self._append_to_file(self.main_feed_file, entry)

        # Also append to daily index file
        daily_file = self._get_daily_file()
        self._append_to_file(daily_file, entry)

        return entry_id

    def _append_to_file(self, filepath: Path, entry: ActivityLogEntry) -> None:
        """Append entry to a JSON file"""
        entries = []

        if filepath.exists():
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    entries = data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError):
                entries = []

        entries.append(entry.to_dict())

        with open(filepath, "w") as f:
            json.dump(entries, f, indent=2)

    def _get_daily_file(self) -> Path:
        """Get today's daily index file"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.activity_dir / f"activity_feed_{date_str}.json"

    def get_last_24_hours_activity(self, tier: Optional[str] = None) -> List[ActivityLogEntry]:
        """Get activity from last 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)

        entries = []
        
        # Try today's and yesterday's files
        for i in range(2):
            date = datetime.now() - timedelta(days=i)
            filepath = self._get_daily_file_for_date(date)
            
            if not filepath.exists():
                continue

            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    file_entries = data if isinstance(data, list) else [data]
            except (json.JSONDecodeError, IOError):
                continue

            entries.extend(
                [
                    ActivityLogEntry.from_dict(e)
                    for e in file_entries
                    if datetime.fromisoformat(e["timestamp"]) > cutoff
                ]
            )

        # Filter by tier if specified
        if tier:
            entries = [e for e in entries if e.tier == tier]

        # Return most recent first
        return sorted(entries, key=lambda x: x.timestamp, reverse=True)

    def _get_daily_file_for_date(self, date: datetime) -> Path:
        """Get daily index file for a specific date"""
        date_str = date.strftime("%Y-%m-%d")
        return self.activity_dir / f"activity_feed_{date_str}.json"

    def cleanup_old_activity(self, keep_days: int = 30) -> int:
        """Remove activity files older than specified days"""
        cutoff = datetime.now() - timedelta(days=keep_days)
        removed = 0

        for filepath in self.activity_dir.glob("activity_feed_*.json"):
            try:
                # Extract date from filename
                date_str = filepath.stem.split("_", 2)[2]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff:
                    filepath.unlink()
                    removed += 1
            except (ValueError, IndexError):
                pass

        return removed
