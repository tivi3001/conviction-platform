"""Email sender using Gmail SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass
from watchlist_alerts_config import EMAIL_CONFIG


class EmailSender:
    def __init__(self):
        self.from_email = EMAIL_CONFIG["from_email"]
        self.to_email = EMAIL_CONFIG["to_email"]
        self.smtp_server = EMAIL_CONFIG["smtp_server"]
        self.smtp_port = EMAIL_CONFIG["smtp_port"]
        self.password = None

    def get_password(self):
        """Prompt for email password once per session."""
        if not self.password:
            self.password = getpass(f"Enter password for {self.from_email}: ")
        return self.password

    def send_alert(self, subject, body_html, stock_ticker):
        """Send alert email."""
        try:
            password = self.get_password()

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = self.to_email

            msg.attach(MIMEText(body_html, "html"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.from_email, password)
                server.sendmail(self.from_email, self.to_email, msg.as_string())

            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False

    def send_digest(self, subject, body_html):
        """Send weekly digest email."""
        return self.send_alert(subject, body_html, "DIGEST")


if __name__ == "__main__":
    sender = EmailSender()
    test_html = "<h1>Test Email</h1><p>This is a test.</p>"
    result = sender.send_alert("Test Alert", test_html, "TEST")
    print(f"Email sent: {result}")
