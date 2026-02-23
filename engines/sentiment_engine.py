"""Sentiment Engine: Measures market perception and momentum toward a stock."""

from typing import Optional
from data.models import SentimentMetrics
from data.yahoo_fetcher import YahooFinanceFetcher
from config import (
    INSIDER_BUYING_BULLISH_THRESHOLD,
    INSIDER_SELLING_BEARISH_THRESHOLD,
    PUTCALL_RATIO_HIGH,
    PUTCALL_RATIO_LOW,
)


class SentimentEngine:
    """Scores stocks on sentiment: Is market perception improving or deteriorating?"""

    def __init__(self):
        self.fetcher = YahooFinanceFetcher()

    def calculate_score(self, symbol: str, insider_net_buying: Optional[float] = None,
                       putcall_ratio: Optional[float] = None,
                       news_sentiment: Optional[float] = None,
                       analyst_rating: Optional[float] = None,
                       social_sentiment: Optional[float] = None) -> SentimentMetrics:
        """
        Calculate sentiment score.

        Score formula:
        - 25% News sentiment
        - 20% Social media sentiment
        - 20% Analyst direction
        - 15% Options flow (put/call ratio)
        - 10% Insider activity
        - 10% Relative strength vs market

        Returns score 0-100 where:
        - 70-100: Strong bullish
        - 55-69: Bullish
        - 45-54: Neutral
        - 30-44: Bearish
        - 0-29: Strong bearish
        """

        metrics = SentimentMetrics(symbol=symbol)

        # --- COMPONENT 1: Insider Trading (10%) ---
        if insider_net_buying is not None:
            metrics.insider_net_buying = insider_net_buying
            insider_score = self._score_insider_activity(insider_net_buying)
        else:
            insider_score = 50.0

        # --- COMPONENT 2: Options Flow (15%) ---
        if putcall_ratio is not None:
            metrics.putcall_ratio = putcall_ratio
            # Fetch options data
            options_data = self.fetcher.fetch_options_chain(symbol)
            if options_data:
                metrics.putcall_ratio = options_data.get("put_call_ratio")
            putcall_score = self._score_putcall_ratio(metrics.putcall_ratio)
        else:
            putcall_score = 50.0

        # --- COMPONENT 3: News Sentiment (25%) ---
        # Note: In MVP, set to neutral. Upgrade to Finnhub for real sentiment
        if news_sentiment is not None:
            metrics.news_sentiment = news_sentiment
            news_score = ((news_sentiment + 1) / 2) * 100  # Convert -1..1 to 0..100
        else:
            news_score = 50.0

        # --- COMPONENT 4: Analyst Ratings (20%) ---
        if analyst_rating is not None:
            metrics.analyst_rating = analyst_rating
            analyst_score = ((analyst_rating + 1) / 2) * 100  # Convert -1..1 to 0..100
        else:
            analyst_score = 50.0

        # --- COMPONENT 5: Social Sentiment (20%) ---
        # Note: In MVP, set to neutral. Would scrape Reddit/Twitter in full version
        if social_sentiment is not None:
            metrics.social_sentiment = social_sentiment
            social_score = ((social_sentiment + 1) / 2) * 100  # Convert -1..1 to 0..100
        else:
            social_score = 50.0

        # --- COMPONENT 6: Relative Strength (10%) ---
        # Would calculate vs SPY
        relative_score = 50.0

        # --- COMPOSITE SCORE ---
        metrics.sentiment_score = (
            (news_score * 0.25) +
            (social_score * 0.20) +
            (analyst_score * 0.20) +
            (putcall_score * 0.15) +
            (insider_score * 0.10) +
            (relative_score * 0.10)
        )

        # Determine sentiment trend
        if metrics.sentiment_score >= 65:
            metrics.sentiment_trend = "IMPROVING"
        elif metrics.sentiment_score >= 55:
            metrics.sentiment_trend = "STABLE"
        else:
            metrics.sentiment_trend = "DETERIORATING"

        return metrics

    def _score_insider_activity(self, insider_net_buying: float) -> float:
        """
        Score insider trading activity.

        insider_net_buying = % of insider transactions that were buys
        0.0 = all sells (bearish)
        0.5 = neutral
        1.0 = all buys (bullish)
        """
        if insider_net_buying > 0.75:
            return 90.0
        elif insider_net_buying > 0.60:
            return 75.0
        elif insider_net_buying > 0.55:
            return 60.0
        elif insider_net_buying > 0.45:
            return 50.0
        elif insider_net_buying > 0.40:
            return 40.0
        elif insider_net_buying > 0.25:
            return 25.0
        else:
            return 10.0

    def _score_putcall_ratio(self, putcall_ratio: Optional[float]) -> float:
        """
        Score put/call ratio.

        High ratio (>1.0) = more puts than calls = bearish
        Low ratio (<0.5) = more calls than puts = bullish
        """
        if putcall_ratio is None:
            return 50.0

        if putcall_ratio < 0.50:
            return 80.0
        elif putcall_ratio < 0.65:
            return 70.0
        elif putcall_ratio < 0.80:
            return 60.0
        elif putcall_ratio < 1.0:
            return 50.0
        elif putcall_ratio < 1.2:
            return 40.0
        elif putcall_ratio < 1.5:
            return 30.0
        else:
            return 15.0

    def calculate_insider_net_buying(self, symbol: str) -> Optional[float]:
        """
        Calculate % of insider transactions that were BUYS vs SELLS.

        Returns: 0.0 (all sells) to 1.0 (all buys)

        In MVP version, returns None (would integrate SEC Form 4 API)
        """
        # TODO: Fetch SEC Form 4 filings
        # Parse insider transactions for past 90 days
        # Calculate: buys / (buys + sells)
        return None

    def analyze_stock(self, symbol: str) -> SentimentMetrics:
        """Complete sentiment analysis for a stock."""

        # Fetch available data
        financials = self.fetcher.fetch_financials(symbol)
        options_data = self.fetcher.fetch_options_chain(symbol)

        putcall_ratio = options_data.get("put_call_ratio") if options_data else None
        insider_net_buying = self.calculate_insider_net_buying(symbol)

        metrics = self.calculate_score(
            symbol=symbol,
            insider_net_buying=insider_net_buying,
            putcall_ratio=putcall_ratio,
            news_sentiment=None,  # Would fetch from Finnhub
            analyst_rating=None,  # Would calculate from financials
            social_sentiment=None,  # Would fetch from Reddit/Twitter
        )

        return metrics
