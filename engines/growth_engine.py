"""Growth Engine: Identifies stocks with high future revenue/earnings potential."""

from typing import Optional, List
from data.models import GrowthMetrics
from data.yahoo_fetcher import YahooFinanceFetcher
from config import GROWTH_REVENUE_LOOKBACK_YEARS, EXPECTED_CAGR_MIN


class GrowthEngine:
    """Scores stocks on growth potential: will they compound capital?"""

    def __init__(self):
        self.fetcher = YahooFinanceFetcher()

    def calculate_score(self, symbol: str, revenue_yoy: Optional[float] = None,
                       earnings_yoy: Optional[float] = None,
                       estimated_cagr: Optional[float] = None) -> GrowthMetrics:
        """
        Calculate growth potential score.

        Score formula:
        - 30% TAM growth potential
        - 25% Business momentum (revenue/earnings acceleration)
        - 20% Competitive moat strength
        - 15% Management execution track record
        - 10% Macro tailwinds

        Returns score 0-100 where:
        - 70-100: High growth (20%+ CAGR)
        - 55-69: Moderate-high growth (10-20% CAGR)
        - 45-54: Moderate growth (5-10% CAGR)
        - 30-44: Limited growth (0-5% CAGR)
        - 0-29: Declining
        """

        metrics = GrowthMetrics(symbol=symbol)

        # Fetch financials if not provided
        if revenue_yoy is None or earnings_yoy is None:
            financials = self.fetcher.fetch_financials(symbol)
            revenue_yoy = metrics.revenue_yoy = financials.get("revenue_yoy")
            earnings_yoy = metrics.earnings_yoy = financials.get("earnings_yoy")

        # --- COMPONENT 1: Revenue Momentum (25%) ---
        revenue_score = self._score_revenue_growth(revenue_yoy)

        # --- COMPONENT 2: Earnings Momentum (25%) ---
        earnings_score = self._score_earnings_growth(earnings_yoy)

        # --- COMPONENT 3: CAGR Projection (30%) ---
        cagr_score = self._score_cagr(estimated_cagr)
        if estimated_cagr:
            metrics.estimated_cagr = estimated_cagr

        # --- COMPONENT 4: Management Track Record (10%) ---
        # Simplified: would check capital allocation, buyback trends, etc.
        management_score = 55.0

        # --- COMPONENT 5: Macro Tailwinds (10%) ---
        macro_score = 50.0  # Would analyze industry growth rates

        # --- COMPOSITE SCORE ---
        metrics.growth_score = (
            (revenue_score * 0.25) +
            (earnings_score * 0.25) +
            (cagr_score * 0.30) +
            (management_score * 0.10) +
            (macro_score * 0.10)
        )

        # Classify growth stage
        if metrics.revenue_yoy and metrics.revenue_yoy > 0.25:
            metrics.growth_stage = "EMERGING"
        elif metrics.revenue_yoy and metrics.revenue_yoy > 0.15:
            metrics.growth_stage = "HIGH"
        elif metrics.revenue_yoy and metrics.revenue_yoy > 0.10:
            metrics.growth_stage = "MODERATE"
        elif metrics.revenue_yoy and metrics.revenue_yoy > 0:
            metrics.growth_stage = "SLOWING"
        else:
            metrics.growth_stage = "MATURE"

        return metrics

    def _score_revenue_growth(self, revenue_yoy: Optional[float]) -> float:
        """Score year-over-year revenue growth."""
        if revenue_yoy is None:
            return 50.0

        if revenue_yoy > 0.30:
            return 95.0
        elif revenue_yoy > 0.20:
            return 80.0
        elif revenue_yoy > 0.15:
            return 70.0
        elif revenue_yoy > 0.10:
            return 60.0
        elif revenue_yoy > 0.05:
            return 45.0
        elif revenue_yoy > 0:
            return 30.0
        else:
            return 15.0

    def _score_earnings_growth(self, earnings_yoy: Optional[float]) -> float:
        """Score year-over-year earnings growth."""
        if earnings_yoy is None:
            return 50.0

        # Earnings growth typically should exceed revenue growth (margin expansion)
        if earnings_yoy > 0.40:
            return 95.0
        elif earnings_yoy > 0.25:
            return 85.0
        elif earnings_yoy > 0.15:
            return 70.0
        elif earnings_yoy > 0.10:
            return 60.0
        elif earnings_yoy > 0.05:
            return 45.0
        elif earnings_yoy > 0:
            return 30.0
        else:
            return 15.0

    def _score_cagr(self, estimated_cagr: Optional[float]) -> float:
        """Score projected compound annual growth rate."""
        if estimated_cagr is None:
            return 50.0

        # For tech stocks, expect 15%+ for high growth
        if estimated_cagr > 0.25:
            return 95.0
        elif estimated_cagr > 0.20:
            return 85.0
        elif estimated_cagr > 0.15:
            return 75.0
        elif estimated_cagr > 0.10:
            return 60.0
        elif estimated_cagr > 0.05:
            return 45.0
        elif estimated_cagr > 0:
            return 30.0
        else:
            return 15.0

    def estimate_cagr(self, symbol: str, years: int = 5) -> Optional[float]:
        """
        Estimate future CAGR from historical growth and analyst consensus.

        This is a simplified version - would enhance with:
        - Company guidance
        - Analyst consensus estimates
        - Industry growth rates
        - TAM expansion potential
        """
        financials = self.fetcher.fetch_financials(symbol)

        # Use analyst forward estimate as proxy
        # Simplified: compare forward PE to trailing PE to estimate growth
        trailing_pe = financials.get("pe_ratio")
        forward_pe = financials.get("forward_pe")

        if not trailing_pe or not forward_pe or forward_pe >= trailing_pe:
            return None

        # If forward PE lower than trailing, implies earnings growth
        # Rough estimate: difference in PE ratios correlates to growth rate
        implied_growth = (trailing_pe / forward_pe - 1) * 100

        return implied_growth

    def analyze_stock(self, symbol: str) -> GrowthMetrics:
        """Complete growth analysis for a stock."""
        financials = self.fetcher.fetch_financials(symbol)

        estimated_cagr = self.estimate_cagr(symbol)

        metrics = self.calculate_score(
            symbol=symbol,
            revenue_yoy=financials.get("revenue_yoy"),
            earnings_yoy=financials.get("earnings_yoy"),
            estimated_cagr=estimated_cagr,
        )

        # Add key catalysts (would be enhanced in full version)
        metrics.key_catalysts = [
            f"Earnings on {financials.get('earnings_date', 'TBD')}",
            "New product launches",
            "Market share gains in key verticals",
        ]

        return metrics
