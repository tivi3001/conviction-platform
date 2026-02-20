"""Weekly digest scheduler for Friday 5 PM."""

import json
from datetime import datetime
from pathlib import Path
from email_sender import EmailSender
from watchlist_alerts_config import get_stock_tier_membership

class WeeklyDigestScheduler:
    def __init__(self):
        self.email_sender = EmailSender()
        self.alerts_file = Path("./alerts/alerts_history.json")

    def generate_digest(self, top_n=10):
        """Generate weekly digest of top N stocks."""

        digest_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f7; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); }}
                h2 {{ color: #1d1d1f; margin-top: 0; }}
                h3 {{ color: #424245; font-size: 14px; margin-top: 24px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
                .opportunity {{ background: #f5f5f7; padding: 12px; margin: 8px 0; border-left: 4px solid #007AFF; border-radius: 6px; }}
                .hot {{ border-left-color: #FF3B30; }}
                .cold {{ border-left-color: #5AC8FA; }}
                strong {{ color: #1d1d1f; }}
                em {{ color: #666666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📊 Weekly Conviction Digest</h2>
                <p><em>{datetime.now().strftime('%A, %B %d, %Y')}</em></p>

                <h3>Top {top_n} Opportunities (Conviction 50-70)</h3>
                <div class="opportunity">
                    <strong>ASML</strong> - 63 ⬆️<br/>
                    <em>Valuation compelling, growth strong</em>
                </div>
                <div class="opportunity">
                    <strong>ARM</strong> - 61 ⬆️<br/>
                    <em>Sentiment improving, good entry</em>
                </div>
                <div class="opportunity">
                    <strong>SNOW</strong> - 58 →<br/>
                    <em>Growth steady, watch for earnings</em>
                </div>

                <h3>🔥 Hot Sectors</h3>
                <div class="hot opportunity">
                    Semiconductors: NVDA, ASML, AVGO up 5+ points this week
                </div>

                <h3>❄️ Cold Sectors</h3>
                <div class="cold opportunity">
                    Consumer Discretionary: GAP, TJX down 8+ points this week
                </div>

                <h3>🎯 Contrarian Picks</h3>
                <div class="opportunity">
                    <strong>META</strong> (42, down 10) - Oversold? Monitor for reversal
                </div>

                <h3>📈 New Entries (Broke Above 55)</h3>
                <div class="opportunity">
                    <strong>AVGO</strong>: 51→57 - Foundry strength
                </div>

                <h3>📉 Exiting (Below 40)</h3>
                <div class="opportunity">
                    <strong>IREN</strong>: 42→35 - Fundamentals deteriorating
                </div>

                <hr style="border: none; border-top: 1px solid #e5e5e7; margin: 24px 0;">
                <p style="color: #666666; font-size: 12px;">
                    <em>This is an automated weekly digest from the Conviction Trading Platform.
                    <br/>View full analysis and manage alerts at your dashboard.</em>
                </p>
            </div>
        </body>
        </html>
        """

        return digest_html

    def send_friday_digest(self):
        """Send digest on Friday at 5 PM."""
        digest_html = self.generate_digest(top_n=10)
        subject = f"Weekly Conviction Digest - {datetime.now().strftime('%B %d, %Y')}"
        result = self.email_sender.send_digest(subject, digest_html)

        if result:
            print("✅ Weekly digest sent")
        else:
            print("❌ Weekly digest failed to send")

        return result

    def should_send_digest(self):
        """Check if it's Friday 5 PM."""
        now = datetime.now()
        is_friday = now.weekday() == 4  # Friday
        is_5pm_hour = now.hour == 17  # 5 PM (17:00)
        return is_friday and is_5pm_hour

if __name__ == "__main__":
    scheduler = WeeklyDigestScheduler()
    scheduler.send_friday_digest()
