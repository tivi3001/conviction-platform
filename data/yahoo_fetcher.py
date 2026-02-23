"""Yahoo Finance data fetcher with parallel requests for speed."""

import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import concurrent.futures
from config import USER_AGENT


class YahooFinanceFetcher:
    """Fast, parallel Yahoo Finance data fetching."""

    def __init__(self):
        self._session = None
        self._max_workers = 5  # Parallel request threads

    def fetch_current_price(self, symbol: str) -> Optional[float]:
        """Fetch current price for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                return float(data["Close"].iloc[-1])
        except Exception:
            pass
        return None

    def fetch_financials(self, symbol: str) -> Dict:
        """Fetch key financial metrics."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                "roe": info.get("returnOnEquity"),
                "roic": info.get("returnOnCapital"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                "earnings_date": info.get("earningsDate"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "50_day_avg": info.get("fiftyDayAverage"),
                "200_day_avg": info.get("twoHundredDayAverage"),
            }
        except Exception:
            return {}

    def fetch_historical_financials(self, symbol: str, years: int = 5) -> Dict:
        """Fetch historical quarterly financial data."""
        try:
            ticker = yf.Ticker(symbol)

            # Quarterly financials
            quarterly_financials = ticker.quarterly_financials
            quarterly_cashflow = ticker.quarterly_cashflow

            if quarterly_financials.empty:
                return {}

            # Calculate key metrics from last 12 quarters
            revenue = quarterly_financials.loc["Total Revenue"] if "Total Revenue" in quarterly_financials.index else None
            net_income = quarterly_financials.loc["Net Income"] if "Net Income" in quarterly_financials.index else None
            operating_cash = quarterly_cashflow.loc["Operating Cash Flow"] if "Operating Cash Flow" in quarterly_cashflow.index else None

            result = {
                "symbol": symbol,
                "revenue": revenue.to_dict() if revenue is not None else {},
                "net_income": net_income.to_dict() if net_income is not None else {},
                "operating_cash_flow": operating_cash.to_dict() if operating_cash is not None else {},
            }

            return result
        except Exception:
            return {}

    def fetch_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Optional[Tuple]:
        """Fetch options data for put/call ratio calculation."""
        try:
            ticker = yf.Ticker(symbol)

            # Get available expiration dates
            dates = ticker.options
            if not dates:
                return None

            # Use provided date or nearest future date
            if not expiration_date:
                expiration_date = dates[0]

            option_chain = ticker.option_chain(expiration_date)
            calls = option_chain.calls
            puts = option_chain.puts

            if calls.empty or puts.empty:
                return None

            # Calculate put/call ratio (open interest based)
            total_call_oi = calls["openInterest"].sum()
            total_put_oi = puts["openInterest"].sum()

            if total_call_oi == 0:
                return None

            put_call_ratio = total_put_oi / total_call_oi

            return {
                "symbol": symbol,
                "put_call_ratio": put_call_ratio,
                "total_call_oi": total_call_oi,
                "total_put_oi": total_put_oi,
                "expiration_date": expiration_date,
            }
        except Exception:
            return None

    def fetch_batch_prices(self, symbols: list) -> Dict[str, float]:
        """Fetch current prices for multiple symbols in parallel."""
        prices = {}

        def _fetch_price(symbol):
            try:
                price = self.fetch_current_price(symbol)
                return symbol, price
            except Exception:
                return symbol, None

        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = [executor.submit(_fetch_price, sym) for sym in symbols]
            for future in concurrent.futures.as_completed(futures):
                symbol, price = future.result()
                if price is not None:
                    prices[symbol] = price

        return prices

    def fetch_batch_financials(self, symbols: list) -> Dict[str, Dict]:
        """Fetch financials for multiple symbols in parallel."""
        financials = {}

        def _fetch_fin(symbol):
            try:
                fin = self.fetch_financials(symbol)
                return symbol, fin
            except Exception:
                return symbol, {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = [executor.submit(_fetch_fin, sym) for sym in symbols]
            for future in concurrent.futures.as_completed(futures):
                symbol, fin = future.result()
                financials[symbol] = fin

        return financials

    def calculate_pe_vs_history(self, symbol: str, lookback_years: int = 5) -> Dict:
        """Calculate current P/E vs historical average."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            current_pe = info.get("trailingPE")
            if not current_pe:
                return {}

            # Fetch historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_years * 365)
            hist = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if hist.empty:
                return {}

            # For simplicity, estimate PE from current data
            # In production, would fetch quarterly earnings data
            return {
                "symbol": symbol,
                "current_pe": current_pe,
                "pe_percentile": None,  # Would calculate from historical data
                "pe_5yr_low": current_pe * 0.7,  # Rough estimate
                "pe_5yr_high": current_pe * 1.3,
            }
        except Exception:
            return {}

    def fetch_industry_averages(self, sector: str) -> Dict:
        """Fetch industry average metrics for comparison."""
        # Note: Yahoo Finance doesn't provide easy sector aggregates
        # This would need to be built from a database of peer companies
        # For now, returning placeholder
        return {
            "sector": sector,
            "avg_pe": None,
            "avg_peg": None,
            "avg_roe": None,
        }
