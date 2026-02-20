"""Background monitoring daemon with real-time alerts."""

import time
import threading
from datetime import datetime
from watchlist_alerts_config import (
    get_all_watchlist_tickers,
    MONITORING_SCHEDULE,
    get_stock_tier_membership
)
from alert_manager import AlertManager, AlertEvent
from email_sender import EmailSender
from desktop_notifications import DesktopNotification
from engines.confluence_engine import ConfluenceEngine

class BackgroundDaemonAlerts:
    def __init__(self):
        self.alert_manager = AlertManager()
        self.email_sender = EmailSender()
        self.confluence_engine = ConfluenceEngine()
        self.running = False
        self.last_scores = {}  # Track previous scores

    def start(self):
        """Start background monitoring daemon."""
        self.running = True
        daemon_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        daemon_thread.start()
        print("✅ Background daemon started")

    def _monitor_loop(self):
        """Main monitoring loop (runs every 5 minutes on weekdays)."""
        while self.running:
            if self._is_weekday():
                self._score_all_stocks()
                self._check_for_alerts()

            time.sleep(MONITORING_SCHEDULE["update_interval_minutes"] * 60)

    def _score_all_stocks(self):
        """Score all deduplicated stocks."""
        tickers = get_all_watchlist_tickers()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scoring {len(tickers)} stocks...")

        for ticker in tickers:
            try:
                score = self.confluence_engine.analyze_stock(ticker)
                self.last_scores[ticker] = score
            except Exception as e:
                print(f"Error scoring {ticker}: {e}")

    def _check_for_alerts(self):
        """Check if any alerts should be triggered."""
        for ticker, score in self.last_scores.items():
            conviction_now = score.score
            conviction_prev = self.last_scores.get(ticker, score).score if ticker in self.last_scores else conviction_now

            alert_type, reason = self.alert_manager.classify_alert(
                ticker, conviction_now, conviction_prev,
                score.valuation_score, score.sentiment_score
            )

            if alert_type:
                self._dispatch_alert(alert_type, ticker, score, reason)

    def _dispatch_alert(self, alert_type, ticker, score, reason):
        """Dispatch CRITICAL/WARNING alerts immediately."""
        tiers = get_stock_tier_membership(ticker)

        # Desktop notification (IMMEDIATE)
        if alert_type == "CRITICAL":
            DesktopNotification.send_critical(
                ticker, int(score.score), int(score.valuation_score),
                int(score.growth_score), int(score.sentiment_score), reason
            )
        elif alert_type == "WARNING":
            DesktopNotification.send_warning(ticker, int(score.score), reason)

        # Email notification (IMMEDIATE)
        subject = f"{alert_type}: {ticker} - {reason}"
        body = f"<h2>{alert_type}: {ticker}</h2><p>Conviction: {score.score:.1f}/100</p><p>Reason: {reason}</p>"
        self.email_sender.send_alert(subject, body, ticker)

        # Log alert
        event = AlertEvent(
            timestamp=datetime.now().isoformat(),
            stock_ticker=ticker,
            alert_type=alert_type,
            conviction_score=score.score,
            previous_score=0,
            reason=reason,
            tiers=tiers
        )
        self.alert_manager.log_alert(event)

    def _is_weekday(self):
        """Check if today is a weekday."""
        return datetime.now().weekday() < 5  # Mon-Fri

    def stop(self):
        """Stop the daemon gracefully."""
        self.running = False
        print("Daemon stopped")

if __name__ == "__main__":
    daemon = BackgroundDaemonAlerts()
    daemon.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()
        print("Background daemon terminated")
