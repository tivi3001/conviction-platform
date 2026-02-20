"""Watchlist configuration for 3-tier alert system."""

# Tier 1: Your custom 106 stocks from Red list
TIER_1_CUSTOM = [
    "AAL", "AAPL", "AAPU", "ABAT", "ABNB", "AEVA", "AFRM", "AMAT", "AMD", "AMDL",
    "AMZN", "AMZU", "ANET", "APLD", "APP", "ARKK", "ARM", "ASML", "ASTS", "AVGO",
    "AVL", "AXP", "BA", "BABA", "BAC", "BBAI", "BHVN", "BITO", "BLSH", "BMNR",
    "BTCUSD", "C", "CEG", "COIN", "CRCL", "CRM", "CROX", "CRWD", "CRWV", "DELL",
    "DJT", "DPST", "ETHUSD", "FIG", "FLY", "FMST", "FTNT", "GAP", "GE", "GGLL",
    "GLD", "GOOGL", "GS", "HIMS", "HOOD", "IBIT", "IBM", "INOD", "INTC", "IONQ",
    "IOS", "IREN", "JPM", "KLAR", "LAC", "LHX", "LMT", "LULU", "LYFT", "MA",
    "MARA", "META", "METU", "MOB", "MRVL", "MSFT", "MSTR", "MU", "NBIS", "NDX",
    "NET", "NFLX", "NOC", "NUGT", "NVDA", "NVDL", "NVO", "OKLO", "ORCL", "ORCX",
    "OXY", "PANW", "PFE", "PLTR", "PLTU", "PPTA", "PTIR", "PYPL", "QCOM", "QID",
    "QUBT", "RBLX", "RDDT", "RHM", "RKLB", "RR", "RTX", "S", "SAP", "SDS",
    "SHOP", "SLV", "SMR", "SNDK", "SNOW", "SOFI", "SOUN", "SPX", "SPXU", "SPY",
    "SQQQ", "T", "TEM", "TJX", "TMUS", "TNA", "TQQQ", "TSLA", "TSLL", "TSM",
    "TXN", "UAL", "UBER", "UDOW", "UEC", "UMAC", "UNH", "UPRO", "USAR", "V",
    "VEEV", "VIX", "VKTX", "VST", "VZ", "WM", "XOM", "ZETA"
]

# Tier 2: US Growth/Tech stocks (auto-qualified major tech/growth companies)
TIER_2_GROWTH_TECH = [
    "NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "TSLA", "ADBE", "NFLX",
    "AMD", "INTC", "AVGO", "ASML", "MU", "ARM", "QCOM",
    "CRM", "SNOW", "PLTR", "NET", "PANW", "CRWD",
    "ABNB", "LYFT", "UBER", "MSTR", "PYPL", "SHOP",
    "RBLX", "VEEV", "HOOD", "SOFI", "FTNT", "COIN",
]

# Tier 3: US Large-Cap stocks (S&P 500, dividend aristocrats, defensive)
TIER_3_LARGE_CAP = [
    "JPM", "BAC", "GS", "C", "AXP", "V", "MA",
    "UNH", "PFE", "JNJ",
    "BA", "GE", "LMT", "RTX", "LHX",
    "WM", "T", "VZ",
    "XOM", "OXY",
    "IBM", "ORCL",
]

# Crypto subset (only these 2)
CRYPTO_ONLY = ["BTCUSD", "ETHUSD"]

# Alert Thresholds
ALERT_THRESHOLDS = {
    "critical": {
        "conviction_level": 65,
        "conviction_jump": 15,
        "valuation_drop": 20,
    },
    "warning": {
        "conviction_drop_from": 60,
        "conviction_drop_to": 45,
        "sentiment_drop": 10,
        "pillar_disagreement": 30,
    },
}

# Email Configuration
EMAIL_CONFIG = {
    "from_email": "Aktienbot1@gmail.com",
    "to_email": "tivi3001@gmail.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
}

# Alert dispatch settings
ALERT_DISPATCH = {
    "critical_and_warning": "immediate",
    "info_digest": "weekly_friday_5pm",
}

# Monitoring schedule
MONITORING_SCHEDULE = {
    "weekdays_only": True,
    "update_interval_minutes": 5,
}

def get_all_watchlist_tickers():
    """Get all unique tickers from all 3 tiers (deduplicated)."""
    all_tickers = set(TIER_1_CUSTOM) | set(TIER_2_GROWTH_TECH) | set(TIER_3_LARGE_CAP)
    return sorted(list(all_tickers))

def get_stock_tier_membership(ticker):
    """Return which tier(s) a stock belongs to."""
    tiers = []
    if ticker in TIER_1_CUSTOM:
        tiers.append("Tier 1")
    if ticker in TIER_2_GROWTH_TECH:
        tiers.append("Tier 2")
    if ticker in TIER_3_LARGE_CAP:
        tiers.append("Tier 3")
    return tiers

if __name__ == "__main__":
    tickers = get_all_watchlist_tickers()
    print(f"Total unique tickers: {len(tickers)}")
    print(f"NVDA tiers: {get_stock_tier_membership('NVDA')}")
    print(f"Sample tickers: {tickers[:10]}")
