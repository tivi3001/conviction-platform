"""Confluence Engine: Combines three pillars into unified conviction score."""

from typing import Optional
from data.models import (
    ValuationMetrics, GrowthMetrics, SentimentMetrics,
    ConvictionScore, ConvictionLevel
)
from config import PILLAR_WEIGHTS, CONVICTION_THRESHOLDS
import math


class ConfluenceEngine:
    """Merges valuation, growth, and sentiment into conviction score."""

    def __init__(self, pillar_weights: dict = None):
        """
        Initialize with optional custom pillar weights.

        Default weights sum to 1.0 and are optimized through backtesting.
        """
        self.weights = pillar_weights or PILLAR_WEIGHTS

    def calculate_conviction(self, valuation: ValuationMetrics,
                           growth: GrowthMetrics,
                           sentiment: SentimentMetrics) -> ConvictionScore:
        """
        Calculate unified conviction score from three pillars.

        Algorithm:
        1. Weighted average of three pillar scores
        2. Pillar agreement bonus: higher if all three aligned
        3. Clamp between 0-100

        Conviction thresholds:
        - 70+: STRONG_BUY (core conviction)
        - 60-69: BUY (high conviction)
        - 55-59: HOLD (moderate conviction)
        - <55: AVOID or SHORT
        """

        # --- WEIGHTED AVERAGE ---
        weighted_score = (
            (valuation.valuation_score * self.weights["valuation"]) +
            (growth.growth_score * self.weights["growth"]) +
            (sentiment.sentiment_score * self.weights["sentiment"])
        )

        # --- PILLAR AGREEMENT BONUS ---
        # If all three pillars are aligned (within 15 points), add confidence
        pillar_agreement = self._calculate_pillar_agreement(
            valuation.valuation_score,
            growth.growth_score,
            sentiment.sentiment_score
        )

        # Blend: 80% weighted average, 20% agreement bonus
        conviction_score = (weighted_score * 0.80) + (pillar_agreement * 0.20)
        conviction_score = max(0, min(100, conviction_score))  # Clamp 0-100

        # --- CONVICTION LEVEL ---
        conviction_level = self._determine_conviction_level(conviction_score)

        # --- ENTRY/EXIT PRICES (simplified) ---
        # In full version, would use technical analysis + valuation
        entry_price = None
        stop_loss = None
        target_1 = None
        target_2 = None
        risk_reward = None

        # --- THESIS ---
        thesis, what_breaks = self._generate_thesis(
            valuation, growth, sentiment, conviction_level
        )

        # --- POSITION SIZING (placeholder, updated by Kelly engine) ---
        recommended_size = self._estimate_position_size(conviction_score)

        return ConvictionScore(
            symbol=valuation.symbol,
            valuation_score=valuation.valuation_score,
            growth_score=growth.growth_score,
            sentiment_score=sentiment.sentiment_score,
            conviction_score=conviction_score,
            conviction_level=conviction_level,
            pillar_agreement=pillar_agreement,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price_1=target_1,
            target_price_2=target_2,
            risk_reward_ratio=risk_reward,
            recommended_position_size=recommended_size,
            thesis=thesis,
            what_could_break=what_breaks,
            key_catalysts=growth.key_catalysts,
        )

    def _calculate_pillar_agreement(self, val_score: float,
                                    growth_score: float,
                                    sent_score: float) -> float:
        """
        Calculate how well the three pillars agree.

        High agreement (all three high/low) = stronger conviction
        Disagreement (mixed signals) = lower confidence

        Score 0-100 based on standard deviation of the three scores.
        """
        scores = [val_score, growth_score, sent_score]
        mean = sum(scores) / len(scores)

        # Calculate standard deviation
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)

        # Convert std dev to agreement score
        # std_dev=0 (perfect agreement) -> score=100
        # std_dev=30 (poor agreement) -> score=0
        agreement = max(0, 100 - (std_dev / 0.3) * 100)

        return agreement

    def _determine_conviction_level(self, conviction_score: float) -> ConvictionLevel:
        """Map conviction score to conviction level."""
        if conviction_score >= CONVICTION_THRESHOLDS["core_conviction"]:
            return ConvictionLevel.STRONG_BUY
        elif conviction_score >= CONVICTION_THRESHOLDS["high_conviction"]:
            return ConvictionLevel.BUY
        elif conviction_score >= CONVICTION_THRESHOLDS["moderate_conviction"]:
            return ConvictionLevel.HOLD
        elif conviction_score >= CONVICTION_THRESHOLDS["avoid"]:
            return ConvictionLevel.AVOID
        else:
            return ConvictionLevel.SHORT

    def _estimate_position_size(self, conviction_score: float) -> Optional[float]:
        """
        Rough position size estimate based on conviction.

        Actual sizing will be calculated by Kelly Criterion engine
        using backtest win rates. This is just an initial guideline.
        """
        if conviction_score >= 70:
            return 0.08  # 8% of portfolio
        elif conviction_score >= 60:
            return 0.05  # 5%
        elif conviction_score >= 55:
            return 0.03  # 3%
        else:
            return None  # Don't trade

    def _generate_thesis(self, valuation: ValuationMetrics,
                        growth: GrowthMetrics,
                        sentiment: SentimentMetrics,
                        conviction_level: ConvictionLevel) -> tuple[str, str]:
        """
        Generate human-readable thesis for the trade.

        Format:
        "Why now": Combine signals from all three pillars
        "What breaks": Key risks to the thesis
        """

        thesis_parts = []

        # Valuation reason
        if valuation.valuation_score >= 65:
            thesis_parts.append(
                f"Stock trading {valuation.upside_to_fair_value or 15}% below "
                f"fair value (valuation score: {valuation.valuation_score:.0f}/100)"
            )
        elif valuation.is_undervalued:
            thesis_parts.append(
                f"Undervalued at current multiples (valuation score: {valuation.valuation_score:.0f}/100)"
            )

        # Growth reason
        if growth.growth_score >= 65:
            thesis_parts.append(
                f"Strong growth trajectory with {growth.estimated_cagr*100 or 15:.0f}% "
                f"estimated CAGR (growth score: {growth.growth_score:.0f}/100)"
            )
        elif growth.growth_stage in ["EMERGING", "HIGH"]:
            thesis_parts.append(
                f"High-growth business in {growth.growth_stage} phase "
                f"(growth score: {growth.growth_score:.0f}/100)"
            )

        # Sentiment reason
        if sentiment.sentiment_score >= 65:
            thesis_parts.append(
                f"Positive market sentiment improving, insider buying, "
                f"low put/call ratio (sentiment score: {sentiment.sentiment_score:.0f}/100)"
            )
        elif sentiment.sentiment_trend == "IMPROVING":
            thesis_parts.append(
                f"Market perception improving (sentiment score: {sentiment.sentiment_score:.0f}/100)"
            )

        thesis = " + ".join(thesis_parts) if thesis_parts else "Multiple positive factors aligned"

        # What could break thesis
        breaks_parts = []

        if valuation.upside_to_fair_value and valuation.upside_to_fair_value < 10:
            breaks_parts.append("Limited upside if growth disappoints")

        if growth.growth_stage == "SLOWING":
            breaks_parts.append("Growth deceleration risk - watch next earnings")

        if sentiment.sentiment_trend == "DETERIORATING":
            breaks_parts.append("Deteriorating sentiment could unwind position")

        breaks = " | ".join(breaks_parts) if breaks_parts else "Watch for earnings misses or macro weakness"

        return thesis, breaks

    def rank_opportunities(self, conviction_scores: list[ConvictionScore],
                          min_conviction: int = 55) -> list[ConvictionScore]:
        """
        Rank opportunities by conviction score.

        Filter out low-conviction (<min_conviction) and sort descending.
        """
        filtered = [cs for cs in conviction_scores if cs.conviction_score >= min_conviction]
        ranked = sorted(filtered, key=lambda x: x.conviction_score, reverse=True)

        return ranked

    def update_weights(self, valuation_wt: float, growth_wt: float, sentiment_wt: float):
        """
        Update pillar weights (used after backtesting optimization).

        Weights must sum to 1.0.
        """
        total = valuation_wt + growth_wt + sentiment_wt
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        self.weights = {
            "valuation": valuation_wt,
            "growth": growth_wt,
            "sentiment": sentiment_wt,
        }
