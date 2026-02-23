"""Valuation Engine: Identifies undervalued quality stocks."""

from typing import Optional, Dict
from data.models import ValuationMetrics
from data.yahoo_fetcher import YahooFinanceFetcher
from config import (
    VALUATION_PE_LOOKBACK_YEARS,
    VALUATION_PEG_THRESHOLD,
)


class ValuationEngine:
    """Scores stocks on valuation: are they cheap relative to quality/growth?"""

    def __init__(self):
        self.fetcher = YahooFinanceFetcher()

    def calculate_score(self, symbol: str, current_pe: Optional[float] = None,
                       historical_pe_avg: Optional[float] = None,
                       peg_ratio: Optional[float] = None,
                       roe: Optional[float] = None,
                       roic: Optional[float] = None) -> ValuationMetrics:
        """
        Calculate comprehensive valuation score.

        Score formula:
        - 30% relative P/E vs 5-year average
        - 25% PEG ratio (P/E to growth)
        - 20% Quality score (ROE, ROIC, margins)
        - 15% Free cash flow yield
        - 10% Balance sheet strength

        Returns score 0-100 where:
        - 70-100: Deeply undervalued
        - 55-69: Undervalued
        - 45-54: Fairly valued
        - 30-44: Overvalued
        - 0-29: Deeply overvalued
        """

        metrics = ValuationMetrics(symbol=symbol)

        # Fetch data if not provided
        if current_pe is None or historical_pe_avg is None:
            financials = self.fetcher.fetch_financials(symbol)
            current_pe = metrics.current_pe = financials.get("pe_ratio")
            metrics.roe = financials.get("roe")
            metrics.roic = financials.get("roic")
            metrics.pb_ratio = financials.get("pb_ratio")
            metrics.ps_ratio = financials.get("ps_ratio")
            metrics.fcf_yield = financials.get("fcf_yield")
            metrics.debt_to_equity = financials.get("debt_to_equity")
            metrics.current_ratio = financials.get("current_ratio")

        if not current_pe:
            metrics.valuation_score = 50.0  # Neutral if no data
            return metrics

        # --- COMPONENT 1: Relative P/E Score (30%) ---
        if historical_pe_avg and historical_pe_avg > 0:
            pe_ratio = current_pe / historical_pe_avg
            # If current PE is 80% of historical = good value
            pe_score = max(0, min(100, (1 - (pe_ratio - 0.7) / 0.3) * 100))
        else:
            pe_score = 50.0  # Neutral

        # --- COMPONENT 2: PEG Ratio Score (25%) ---
        if peg_ratio:
            metrics.peg_ratio = peg_ratio
            # PEG < 1.0 is undervalued, > 2.0 is overvalued
            if peg_ratio < 0.5:
                peg_score = 95.0
            elif peg_ratio < 1.0:
                peg_score = 75.0
            elif peg_ratio < 1.5:
                peg_score = 60.0
            elif peg_ratio < 2.0:
                peg_score = 40.0
            else:
                peg_score = 20.0
        else:
            peg_score = 50.0

        # --- COMPONENT 3: Quality Score (20%) ---
        quality_score = self._calculate_quality_score(
            roe=roe or metrics.roe,
            roic=roic or metrics.roic,
            pb_ratio=metrics.pb_ratio,
        )

        # --- COMPONENT 4: Free Cash Flow Score (15%) ---
        fcf_score = self._calculate_fcf_score(metrics.fcf_yield)

        # --- COMPONENT 5: Balance Sheet Score (10%) ---
        balance_score = self._calculate_balance_sheet_score(
            debt_to_equity=metrics.debt_to_equity,
            current_ratio=metrics.current_ratio,
        )

        # --- COMPOSITE SCORE ---
        metrics.valuation_score = (
            (pe_score * 0.30) +
            (peg_score * 0.25) +
            (quality_score * 0.20) +
            (fcf_score * 0.15) +
            (balance_score * 0.10)
        )

        # Determine if undervalued
        metrics.is_undervalued = metrics.valuation_score >= 55

        # Estimate upside if undervalued
        if metrics.is_undervalued and historical_pe_avg and current_pe:
            # Assume fair value is historical average
            fair_value_multiple = historical_pe_avg / current_pe
            metrics.upside_to_fair_value = (fair_value_multiple - 1.0) * 100

        return metrics

    def _calculate_quality_score(self, roe: Optional[float] = None,
                                roic: Optional[float] = None,
                                pb_ratio: Optional[float] = None) -> float:
        """Score quality metrics (ROE, ROIC, Price-to-Book)."""
        scores = []

        # ROE: Above 15% is good
        if roe is not None:
            if roe > 0.20:
                scores.append(90.0)
            elif roe > 0.15:
                scores.append(75.0)
            elif roe > 0.10:
                scores.append(60.0)
            elif roe > 0.05:
                scores.append(40.0)
            else:
                scores.append(20.0)

        # ROIC: Should exceed WACC (typically >8%)
        if roic is not None:
            if roic > 0.15:
                scores.append(85.0)
            elif roic > 0.10:
                scores.append(70.0)
            elif roic > 0.08:
                scores.append(55.0)
            else:
                scores.append(35.0)

        # Price-to-Book: Lower is better
        if pb_ratio is not None:
            if pb_ratio < 1.0:
                scores.append(80.0)
            elif pb_ratio < 1.5:
                scores.append(65.0)
            elif pb_ratio < 2.0:
                scores.append(50.0)
            else:
                scores.append(35.0)

        return sum(scores) / len(scores) if scores else 50.0

    def _calculate_fcf_score(self, fcf_yield: Optional[float]) -> float:
        """Score free cash flow yield."""
        if fcf_yield is None:
            return 50.0

        # FCF yield above 5% is excellent, above 3% is good
        if fcf_yield > 0.08:
            return 90.0
        elif fcf_yield > 0.05:
            return 75.0
        elif fcf_yield > 0.03:
            return 60.0
        elif fcf_yield > 0.01:
            return 40.0
        else:
            return 20.0

    def _calculate_balance_sheet_score(self, debt_to_equity: Optional[float] = None,
                                       current_ratio: Optional[float] = None) -> float:
        """Score balance sheet health."""
        scores = []

        # Debt-to-Equity: Lower is better (< 1.0 is good)
        if debt_to_equity is not None:
            if debt_to_equity < 0.5:
                scores.append(85.0)
            elif debt_to_equity < 1.0:
                scores.append(70.0)
            elif debt_to_equity < 1.5:
                scores.append(50.0)
            else:
                scores.append(30.0)

        # Current Ratio: 1.5-2.0 is ideal
        if current_ratio is not None:
            if current_ratio > 2.0:
                scores.append(75.0)
            elif current_ratio > 1.5:
                scores.append(85.0)
            elif current_ratio > 1.0:
                scores.append(60.0)
            else:
                scores.append(30.0)

        return sum(scores) / len(scores) if scores else 50.0

    def analyze_stock(self, symbol: str) -> ValuationMetrics:
        """Complete valuation analysis for a stock."""
        # Fetch all financial data
        financials = self.fetcher.fetch_financials(symbol)
        historical = self.fetcher.fetch_historical_financials(symbol)

        current_pe = financials.get("pe_ratio")

        # Calculate historical average PE (simplified)
        # In production, would compute from historical quarterly data
        historical_pe_avg = current_pe * 1.1 if current_pe else None

        # PEG calculation would require earnings growth rate
        # For now, use forward PE as proxy
        forward_pe = financials.get("forward_pe")
        peg_ratio = None
        if current_pe and forward_pe and forward_pe > 0:
            # Simple estimate: if forward PE < current, implies growth
            growth_rate = (current_pe / forward_pe - 1) * 100 if forward_pe > 0 else 10
            peg_ratio = current_pe / max(growth_rate, 1)

        return self.calculate_score(
            symbol=symbol,
            current_pe=current_pe,
            historical_pe_avg=historical_pe_avg,
            peg_ratio=peg_ratio,
            roe=financials.get("roe"),
            roic=financials.get("roic"),
        )
