"""Alert classification and deduplication engine."""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AlertEvent:
    timestamp: str
    stock_ticker: str
    alert_type: str  # CRITICAL, WARNING, INFO
    conviction_score: float
    previous_score: float
    reason: str
    tiers: List[str]

class AlertManager:
    def __init__(self, alerts_dir="./alerts"):
        self.alerts_dir = Path(alerts_dir)
        self.alerts_dir.mkdir(exist_ok=True)
        self.alerts_file = self.alerts_dir / "alerts_history.json"
        self.conviction_file = self.alerts_dir / "conviction_history.json"

    def classify_alert(self, ticker, conviction_now, conviction_prev, valuation, sentiment):
        """Classify if alert should be triggered."""

        # CRITICAL triggers
        if conviction_now >= 65:
            return "CRITICAL", "Conviction 65+"
        if conviction_now - conviction_prev >= 15:
            return "CRITICAL", f"Conviction jump +{conviction_now - conviction_prev}"

        # WARNING triggers
        if conviction_prev >= 60 and conviction_now <= 45:
            return "WARNING", f"Conviction drop {conviction_prev}→{conviction_now}"
        if sentiment < -10:
            return "WARNING", "Sentiment deteriorated >10 points"

        return None, None

    def log_alert(self, alert: AlertEvent):
        """Log alert to history."""
        alerts = []
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r') as f:
                alerts = json.load(f)

        alerts.append({
            'timestamp': alert.timestamp,
            'ticker': alert.stock_ticker,
            'type': alert.alert_type,
            'conviction': alert.conviction_score,
            'reason': alert.reason,
            'tiers': alert.tiers
        })

        with open(self.alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)

    def get_alerts_since(self, hours=24):
        """Get alerts from last N hours."""
        if not self.alerts_file.exists():
            return []

        with open(self.alerts_file, 'r') as f:
            alerts = json.load(f)

        return [a for a in alerts if a['type'] in ['CRITICAL', 'WARNING']]

if __name__ == "__main__":
    manager = AlertManager()
    alert_type, reason = manager.classify_alert("NVDA", 72, 54, 70, 65)
    print(f"Alert: {alert_type} - {reason}")
