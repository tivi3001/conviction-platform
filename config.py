"""Configuration constants for Conviction Trading Platform."""

# ============================================================================
# THREE-TIER WATCHLIST STRUCTURE
# ============================================================================

# TIER 1: Personal Watchlist (User's specific focus stocks) - ALPHABETICALLY SORTED
TIER_1_STOCKS = [
    "AAPL",    # Apple
    "ADBE",    # Adobe
    "AMZN",    # Amazon
    "GOOGL",   # Alphabet/Google
    "META",    # Meta Platforms
    "MSFT",    # Microsoft
    "NVDA",    # NVIDIA
    "PYPL",    # PayPal
    "TSLA",    # Tesla
]

# TIER 2: US Tech & Growth Stocks - ALPHABETICALLY SORTED (additional tech/growth exposure)
TIER_2_STOCKS = [
    "ACN",     # Accenture
    "CRM",     # Salesforce
    "CSCO",    # Cisco
    "INTC",    # Intel
    "INTU",    # Intuit
    "MSTR",    # MicroStrategy
    "NFLX",    # Netflix
    "ORCL",    # Oracle
    "PLTR",    # Palantir
    "SHOP",    # Shopify
    "SNOW",    # Snowflake
    "SPLK",    # Splunk
    "SNPS",    # Synopsys
    "SQ",      # Square/Block
    "VEEV",    # Veeva
]

# TIER 3: US Large-Cap Dividend / Defensive Stocks - ALPHABETICALLY SORTED (market stabilizers)
TIER_3_STOCKS = [
    "AXP",     # American Express
    "BA",      # Boeing
    "BAC",     # Bank of America
    "CCI",     # Crown Castle
    "COF",     # Capital One
    "GE",      # General Electric
    "GM",      # General Motors
    "GS",      # Goldman Sachs
    "JNJ",     # Johnson & Johnson
    "JPM",     # JPMorgan Chase
    "KO",      # Coca-Cola
    "PEP",     # PepsiCo
    "PG",      # Procter & Gamble
    "PNC",     # PNC Financial
    "UNP",     # Union Pacific
    "WMT",     # Walmart
]

# Combined target stocks for all tiers (union of all three)
TARGET_STOCKS = TIER_1_STOCKS + TIER_2_STOCKS + TIER_3_STOCKS

# Tier membership mapping (for UI filtering)
TIER_MAPPING = {
    **{stock: 1 for stock in TIER_1_STOCKS},
    **{stock: 2 for stock in TIER_2_STOCKS},
    **{stock: 3 for stock in TIER_3_STOCKS},
}

# Tier display labels
TIER_LABELS = {
    1: "Personal Watchlist",
    2: "US Tech & Growth",
    3: "US Large-Cap & Dividends",
}

# Pillar Weights (Initial - will optimize via backtesting)
PILLAR_WEIGHTS = {
    "valuation": 0.30,
    "growth": 0.35,
    "sentiment": 0.35,
}

# Conviction Score Thresholds
CONVICTION_THRESHOLDS = {
    "core_conviction": 70,      # Highest confidence trades
    "high_conviction": 60,      # Good trading opportunity
    "moderate_conviction": 55,  # Monitor closely
    "avoid": 45,               # Insufficient data
}

# Data Refresh Intervals (seconds)
VALUATION_REFRESH = 3600      # Update valuation daily (slower moving)
GROWTH_REFRESH = 3600         # Update growth daily (quarterly data)
SENTIMENT_REFRESH = 300       # Update sentiment every 5 minutes (more volatile)
PRICE_REFRESH = 60            # Update price data every minute

# Valuation Parameters
VALUATION_PE_LOOKBACK_YEARS = 5
VALUATION_PEG_THRESHOLD = 1.5  # Undervalued if PEG < 1.5

# Growth Parameters
GROWTH_REVENUE_LOOKBACK_YEARS = 3
GROWTH_EARNINGS_LOOKBACK_YEARS = 3
EXPECTED_CAGR_MIN = 0.10       # Expect at least 10% annual growth

# Sentiment Parameters
INSIDER_BUYING_BULLISH_THRESHOLD = 0.60     # If >60% buys, bullish
INSIDER_SELLING_BEARISH_THRESHOLD = 0.40    # If <40% buys, bearish
PUTCALL_RATIO_HIGH = 0.70                    # High put/call = bearish
PUTCALL_RATIO_LOW = 0.50                     # Low put/call = bullish

# Backtesting Parameters
BACKTEST_START_YEARS = 5
BACKTEST_WIN_RATE_TARGET = 0.55  # Target >55% win rate
BACKTEST_LOOKAHEAD_MONTHS = [1, 3, 6]  # Test 1M, 3M, 6M forward returns

# Kelly Criterion Parameters
KELLY_FRACTION_MAX = 0.40  # Never risk more than 40% per type
KELLY_POSITION_CAP = 0.10  # Never risk more than 10% per stock

# Portfolio Constraints
MAX_SECTOR_EXPOSURE = 0.40      # Max 40% in any sector
MAX_SINGLE_POSITION = 0.10      # Max 10% in any single stock
CORRELATION_THRESHOLD = 0.70    # Flag if >70% correlated

# GUI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
REFRESH_GUI_INTERVAL = 5  # Update dashboard every 5 seconds

# Caching TTL (seconds)
CACHE_TTL_VALUATION = 3600 * 24      # Cache fundamentals 24 hours
CACHE_TTL_GROWTH = 3600 * 24         # Cache growth 24 hours
CACHE_TTL_SENTIMENT = 3600 * 1       # Cache sentiment 1 hour
CACHE_TTL_PRICE = 60                 # Cache prices 1 minute

# API Settings
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# SEC Edgar API
SEC_API_BASE = "https://www.sec.gov/cgi-bin/browse-edgar"
SEC_FORM4_API = "https://data.sec.gov/submissions/"

# Yahoo Finance
YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
YAHOO_FALLBACK_URL = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "conviction_platform.log"
