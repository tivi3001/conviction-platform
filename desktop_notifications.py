"""macOS desktop notifications with Apple Glass design."""

import subprocess
from datetime import datetime

class DesktopNotification:
    """Send macOS notifications with Glass design styling."""

    @staticmethod
    def send_critical(stock_ticker, conviction_score, valuation, growth, sentiment, thesis):
        """Send CRITICAL alert notification."""
        title = f"🔴 CRITICAL: {stock_ticker}"
        message = f"{conviction_score}/100 (+15 pts)\nValuation: {valuation} | Growth: {growth}\n{thesis}"

        DesktopNotification._send_notification(title, message, alert_type="critical")

    @staticmethod
    def send_warning(stock_ticker, conviction_score, reason):
        """Send WARNING alert notification."""
        title = f"🟡 WARNING: {stock_ticker}"
        message = f"{conviction_score}/100\n{reason}"

        DesktopNotification._send_notification(title, message, alert_type="warning")

    @staticmethod
    def _send_notification(title, message, alert_type="info"):
        """Send native macOS notification via osascript."""
        script = f"""
        display notification "{message}" with title "{title}"
        """

        try:
            process = subprocess.Popen(
                ["osascript", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            process.communicate(input=script)
        except Exception as e:
            print(f"Notification failed: {e}")

if __name__ == "__main__":
    # Test CRITICAL alert
    DesktopNotification.send_critical(
        "NVDA", "72", "72", "85", "65",
        "Strong AI momentum, entry point"
    )

    # Test WARNING alert
    DesktopNotification.send_warning(
        "META", "42", "Conviction drop 58→42, analyst downgrade"
    )
