"""Data models for Conviction Trading Platform."""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class ConvictionLevel(Enum):
    """Conviction score interpretation."""
    STRONG_BUY = "STRONG_BUY"      # 70+
    BUY = "BUY"                    # 60-69
    HOLD = "HOLD"                  # 55-59
    AVOID = "AVOID"                # <55
    SHORT = "SHORT"                # Reverse signal


@dataclass
class ValuationMetrics:
    """Valuation pillar data."""
    symbol: str
    current_pe: Optional[float] = None
    pe_5yr_avg: Optional[float] = None
    pe_vs_industry: Optional[float] = None
    peg_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    roe: Optional[float] = None
    roic: Optional[float] = None
    fcf_yield: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    valuation_score: float = 50.0  # 0-100
    is_undervalued: bool = False
    upside_to_fair_value: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class GrowthMetrics:
    """Growth potential pillar data."""
    symbol: str
    revenue_yoy: Optional[float] = None  # Year-over-year growth
    earnings_yoy: Optional[float] = None
    fcf_growth_yoy: Optional[float] = None
    revenue_cagr_3yr: Optional[float] = None
    earnings_cagr_3yr: Optional[float] = None
    margin_trend: Optional[float] = None  # Expanding/contracting
    rd_spend_trend: Optional[float] = None
    competitive_moat: str = "UNKNOWN"  # STRONG, MODERATE, WEAK, UNKNOWN
    management_score: float = 50.0  # 0-100 based on track record
    estimated_cagr: Optional[float] = None  # Projected 3-5 year CAGR
    growth_score: float = 50.0  # 0-100
    growth_stage: str = "MATURE"  # EMERGING, HIGH, MODERATE, SLOWING, MATURE
    key_catalysts: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SentimentMetrics:
    """Sentiment pillar data."""
    symbol: str
    news_sentiment: Optional[float] = None  # -1 to 1 (negative to positive)
    news_volume: int = 0  # Articles per day
    insider_net_buying: Optional[float] = None  # % buying vs selling
    insider_transactions_count: int = 0
    putcall_ratio: Optional[float] = None
    short_interest_pct: Optional[float] = None
    social_mentions: int = 0  # Reddit/Twitter mentions
    social_sentiment: Optional[float] = None  # -1 to 1
    analyst_rating: Optional[float] = None  # -1 (sell) to 1 (buy)
    analyst_upgrades_recent: int = 0
    analyst_downgrades_recent: int = 0
    relative_strength: Optional[float] = None  # vs SPY
    sentiment_score: float = 50.0  # 0-100
    sentiment_trend: str = "STABLE"  # IMPROVING, STABLE, DETERIORATING
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ConvictionScore:
    """Combined conviction score and recommendation."""
    symbol: str
    valuation_score: float
    growth_score: float
    sentiment_score: float
    conviction_score: float  # 0-100 weighted average
    conviction_level: ConvictionLevel
    pillar_agreement: float  # How aligned are the three pillars? (0-100)

    # Trade recommendation
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_price_1: Optional[float] = None
    target_price_2: Optional[float] = None
    risk_reward_ratio: Optional[float] = None

    # Kelly Criterion sizing (from backtesting edge)
    kelly_optimal_fraction: Optional[float] = None
    recommended_position_size: Optional[float] = None  # % of portfolio
    kelly_optimal: Optional[float] = None  # Full Kelly as % of portfolio
    kelly_conservative: Optional[float] = None  # Kelly / 2

    # Thesis
    thesis: str = ""
    what_could_break: str = ""
    key_catalysts: List[str] = field(default_factory=list)

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)

    # === NEW: History tracking for 7-day trends and "What Changed?" ===
    previous_score: Optional[float] = None
    score_change_points: Optional[float] = None  # Δ from last update
    score_change_percent: Optional[float] = None

    # Previous pillar scores for detecting which changed
    valuation_previous: Optional[float] = None
    growth_previous: Optional[float] = None
    sentiment_previous: Optional[float] = None

    # Track which pillars changed and by how much
    pillar_changes: Dict[str, Dict] = field(default_factory=dict)
    # Example: {
    #   "valuation": {"prev": 68, "curr": 72, "change": +4},
    #   "growth": {"prev": 70, "curr": 71, "change": +1}
    # }

    # Reasons for changes (detected during update cycle)
    change_triggers: List[str] = field(default_factory=list)
    # Example: ["Insider buying spike", "Analyst upgrade"]

    # 7-day conviction history for sparkline charting
    conviction_7d_sparkline: List[float] = field(default_factory=list)


@dataclass
class StockSnapshot:
    """Complete data for a stock at a point in time."""
    symbol: str
    price: float
    price_timestamp: datetime
    valuation: ValuationMetrics
    growth: GrowthMetrics
    sentiment: SentimentMetrics
    conviction: ConvictionScore

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "symbol": self.symbol,
            "price": self.price,
            "conviction_score": self.conviction.conviction_score,
            "conviction_level": self.conviction.conviction_level.value,
            "valuation_score": self.conviction.valuation_score,
            "growth_score": self.conviction.growth_score,
            "sentiment_score": self.conviction.sentiment_score,
            "recommendation": {
                "entry": self.conviction.entry_price,
                "stop_loss": self.conviction.stop_loss,
                "target_1": self.conviction.target_price_1,
                "target_2": self.conviction.target_price_2,
                "risk_reward": self.conviction.risk_reward_ratio,
            },
            "position_size": self.conviction.recommended_position_size,
            "thesis": self.conviction.thesis,
            "timestamp": self.conviction.timestamp.isoformat(),
        }


@dataclass
class BacktestResult:
    """Results from backtesting a conviction strategy."""
    symbol: str
    start_date: datetime
    end_date: datetime

    # Performance metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0  # %

    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    avg_trade_return: float = 0.0

    # Risk metrics
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0

    # Optimal sizing
    kelly_optimal: Optional[float] = None
    kelly_half: Optional[float] = None

    # Pillar importance (from sensitivity analysis)
    valuation_importance: float = 0.30
    growth_importance: float = 0.35
    sentiment_importance: float = 0.35

    # Notes
    notes: str = ""
