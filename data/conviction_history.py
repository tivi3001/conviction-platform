"""
Conviction History Data Models

Tracks historical conviction scores per stock with pillar changes and reasons.
Used for:
- 7-day sparkline trends
- "What changed?" detection
- Activity feed generation
- Analyzing conviction momentum
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class ConvictionAction(Enum):
    """Types of actions that trigger activity log entries"""
    CONVICTION_INCREASED = "conviction_increased"
    CONVICTION_DECREASED = "conviction_decreased"
    SENTIMENT_IMPROVED = "sentiment_improved"
    SENTIMENT_DETERIORATED = "sentiment_deteriorated"
    VALUATION_IMPROVED = "valuation_improved"
    VALUATION_DETERIORATED = "valuation_deteriorated"
    GROWTH_ACCELERATED = "growth_accelerated"
    GROWTH_SLOWED = "growth_slowed"
    THESIS_BROKEN = "thesis_broken"  # Conviction < 45
    HIGH_CONVICTION_REACHED = "high_conviction_reached"  # Conviction >= 70
    SENTIMENT_FLIPPED = "sentiment_flipped"  # Positive <-> Negative


@dataclass
class ConvictionHistory:
    """Historical record of conviction score for a single stock at a point in time"""

    symbol: str
    timestamp: datetime

    # Core scores
    conviction_score: float
    valuation_score: float
    growth_score: float
    sentiment_score: float
    pillar_agreement: float = 0.0  # 0-100, how aligned are the pillars

    # Track changes from previous update
    changes: Dict[str, Dict] = field(default_factory=dict)
    change_reasons: List[str] = field(default_factory=list)

    # Calculated fields for display
    thesis: str = ""  # Why buy this stock
    what_could_break: str = ""  # Main risks to thesis
    key_catalysts: List[str] = field(default_factory=list)  # Next triggers

    # For comparing to previous conviction
    previous_conviction: Optional[float] = None
    conviction_change: Optional[float] = None  # Delta from last update
    conviction_change_percent: Optional[float] = None  # % change from last

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "conviction_score": self.conviction_score,
            "valuation_score": self.valuation_score,
            "growth_score": self.growth_score,
            "sentiment_score": self.sentiment_score,
            "pillar_agreement": self.pillar_agreement,
            "changes": self.changes,
            "change_reasons": self.change_reasons,
            "thesis": self.thesis,
            "what_could_break": self.what_could_break,
            "key_catalysts": self.key_catalysts,
            "previous_conviction": self.previous_conviction,
            "conviction_change": self.conviction_change,
            "conviction_change_percent": self.conviction_change_percent,
        }

    @staticmethod
    def from_dict(data: dict) -> "ConvictionHistory":
        """Deserialize from dictionary (JSON storage)"""
        data_copy = data.copy()
        if isinstance(data_copy.get("timestamp"), str):
            data_copy["timestamp"] = datetime.fromisoformat(data_copy["timestamp"])
        return ConvictionHistory(**data_copy)


@dataclass
class ActivityLogEntry:
    """Log entry for the recent activity feed"""

    id: str  # UUID for unique identification
    timestamp: datetime
    symbol: str
    action: str  # See ConvictionAction enum
    old_value: float  # Previous conviction score (or pillar score)
    new_value: float  # Current conviction score (or pillar score)
    magnitude: float  # Absolute change |new - old|
    reason: str  # Human-readable explanation (e.g., "Analyst upgrade")
    tier: str  # "Tier 1", "Tier 2", or "Tier 3"

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "action": self.action,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "magnitude": self.magnitude,
            "reason": self.reason,
            "tier": self.tier,
        }

    @staticmethod
    def from_dict(data: dict) -> "ActivityLogEntry":
        """Deserialize from dictionary (JSON storage)"""
        data_copy = data.copy()
        if isinstance(data_copy.get("timestamp"), str):
            data_copy["timestamp"] = datetime.fromisoformat(data_copy["timestamp"])
        return ActivityLogEntry(**data_copy)

    def format_for_display(self) -> str:
        """Format as human-readable activity entry

        Example: "[14:32] NVDA ▲ conviction +5 (Analyst upgrade)"
        """
        time_str = self.timestamp.strftime("%H:%M")

        # Determine direction symbol
        direction = "▲" if self.new_value > self.old_value else "▼"

        # Clean up action name for display
        action_display = self.action.replace("_", " ").title()

        return f"[{time_str}] {self.symbol} {direction} {action_display} {self.magnitude:+.1f} ({self.reason})"
