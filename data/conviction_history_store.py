"""
Conviction History Store

Manages JSON-based persistence of historical conviction scores.
Each stock gets its own JSON file in data/history/{symbol}.json
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from .conviction_history import ConvictionHistory


class ConvictionHistoryStore:
    """Manages historical conviction data with JSON persistence"""

    def __init__(self, history_dir: Optional[str] = None):
        """Initialize history store

        Args:
            history_dir: Directory to store history JSON files.
                        Defaults to ./data/history/
        """
        if history_dir is None:
            history_dir = os.path.join(
                os.path.dirname(__file__), "..", "data", "history"
            )

        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _get_history_path(self, symbol: str) -> Path:
        """Get file path for a stock's history"""
        return self.history_dir / f"{symbol}.json"

    def save_conviction_history(self, symbol: str, history_entry: ConvictionHistory) -> None:
        """Append conviction history entry to stock's JSON file"""
        filepath = self._get_history_path(symbol)

        # Load existing history
        entries = []
        if filepath.exists():
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    entries = data if isinstance(data, list) else [data]
            except (json.JSONDecodeError, IOError):
                entries = []

        # Append new entry
        entries.append(history_entry.to_dict())

        # Keep only last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        entries = [
            e
            for e in entries
            if datetime.fromisoformat(e["timestamp"]) > cutoff_date
        ]

        # Write back to file
        with open(filepath, "w") as f:
            json.dump(entries, f, indent=2)

    def load_conviction_history(
        self, symbol: str, days: int = 7
    ) -> List[ConvictionHistory]:
        """Load recent conviction history for a stock"""
        filepath = self._get_history_path(symbol)

        if not filepath.exists():
            return []

        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                entries = data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, IOError):
            return []

        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = [
            ConvictionHistory.from_dict(e)
            for e in entries
            if datetime.fromisoformat(e["timestamp"]) > cutoff_date
        ]

        # Return most recent first
        return sorted(filtered, key=lambda x: x.timestamp, reverse=True)

    def get_conviction_trend_sparkline(
        self, symbol: str, points: int = 7
    ) -> List[float]:
        """Get last N conviction scores for sparkline charting"""
        history = self.load_conviction_history(symbol, days=30)

        if not history:
            return []

        # Reverse to get oldest first
        history = list(reversed(history))

        # Return last N points
        sparkline = [h.conviction_score for h in history[-points:]]
        return sparkline

    def get_last_conviction(self, symbol: str) -> Optional[ConvictionHistory]:
        """Get the most recent conviction history entry"""
        history = self.load_conviction_history(symbol, days=30)
        return history[0] if history else None

    def get_symbol_activity(self, symbol: str, hours: int = 24) -> List[dict]:
        """Get conviction changes for a specific symbol in last N hours"""
        history = self.load_conviction_history(symbol, days=int(hours / 24) + 1)

        if len(history) < 2:
            return []

        # Identify changes
        changes = []
        for i in range(len(history) - 1):
            current = history[i]
            previous = history[i + 1]

            delta = current.conviction_score - previous.conviction_score

            if abs(delta) > 0.5:  # Only log meaningful changes
                changes.append(
                    {
                        "timestamp": current.timestamp.isoformat(),
                        "symbol": symbol,
                        "old_conviction": previous.conviction_score,
                        "new_conviction": current.conviction_score,
                        "change": delta,
                        "reasons": current.change_reasons,
                    }
                )

        return changes

    def cleanup_all_histories(self, keep_days: int = 7) -> dict:
        """Clean up old data from all stock history files"""
        stats = {}

        for filepath in self.history_dir.glob("*.json"):
            symbol = filepath.stem
            
            if not filepath.exists():
                continue
                
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    entries = data if isinstance(data, list) else [data]
            except (json.JSONDecodeError, IOError):
                continue

            cutoff_date = datetime.now() - timedelta(days=keep_days)
            original_count = len(entries)

            entries = [
                e
                for e in entries
                if datetime.fromisoformat(e["timestamp"]) > cutoff_date
            ]

            removed = original_count - len(entries)

            if removed > 0:
                with open(filepath, "w") as f:
                    json.dump(entries, f, indent=2)
                stats[symbol] = removed

        return stats
