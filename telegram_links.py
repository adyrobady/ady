"""Generate Telegram shareable links for dashboard access."""

import urllib.parse
from typing import Dict, List


class TelegramDashboardLinks:
    """Manager for creating Telegram-shareable dashboard links."""

    # Default dashboard links
    DASHBOARDS = {
        "Alpaca Paper Trading": "https://app.alpaca.markets/paper/dashboard/overview",
        "Alpaca Portfolio": "https://app.alpaca.markets/paper/portfolio",
        "Alpaca Orders": "https://app.alpaca.markets/paper/orders",
    }

    @staticmethod
    def format_message(dashboards: Dict[str, str] = None) -> str:
        """
        Format dashboards as a readable message.

        Args:
            dashboards: Dict of {name: url}. Uses defaults if None.

        Returns:
            Formatted message string
        """
        if dashboards is None:
            dashboards = TelegramDashboardLinks.DASHBOARDS

        lines = ["📊 Dashboard Links:\n"]
        for name, url in dashboards.items():
            lines.append(f"• {name}\n{url}\n")

        return "".join(lines)

    @staticmethod
    def telegram_share_url(
        message: str = None, dashboards: Dict[str, str] = None
    ) -> str:
        """
        Generate a Telegram share URL (t.me/share).

        This creates a link that opens Telegram with a pre-filled message.
        Works on web and in Telegram app.

        Args:
            message: Custom message. Uses formatted dashboards if None.
            dashboards: Dict of {name: url}. Uses defaults if None.

        Returns:
            Telegram share URL
        """
        if message is None:
            message = TelegramDashboardLinks.format_message(dashboards)

        encoded = urllib.parse.quote(message)
        return f"https://t.me/share/url?url=&text={encoded}"

    @staticmethod
    def telegram_me_url(username: str = None) -> str:
        """
        Generate a Telegram @username link.

        Args:
            username: Telegram username (with or without @)

        Returns:
            Telegram link (t.me/username)
        """
        if username is None:
            return "https://t.me/"

        username = username.lstrip("@")
        return f"https://t.me/{username}"

    @staticmethod
    def deep_link(message: str = None, dashboards: Dict[str, str] = None) -> str:
        """
        Generate a Telegram deep link (tg://msg_url).

        This works inside the Telegram app for quicker access.

        Args:
            message: Custom message. Uses formatted dashboards if None.
            dashboards: Dict of {name: url}. Uses defaults if None.

        Returns:
            Deep link for Telegram app
        """
        if message is None:
            message = TelegramDashboardLinks.format_message(dashboards)

        encoded = urllib.parse.quote(message)
        return f"tg://msg_url?url=&text={encoded}"

    @classmethod
    def print_links(cls, custom_dashboards: Dict[str, str] = None) -> None:
        """Print all link formats to console."""
        dashboards = custom_dashboards or cls.DASHBOARDS

        print("\n📱 Telegram Dashboard Links\n")
        print("=" * 50)

        print("\n📋 Formatted Message:")
        print(cls.format_message(dashboards))

        print("=" * 50)
        print("\n🔗 Telegram Share URL (click to send to Telegram):")
        share_url = cls.telegram_share_url(dashboards=dashboards)
        print(share_url)

        print("\n" + "=" * 50)
        print("\n🚀 Telegram Deep Link (app):")
        deep = cls.deep_link(dashboards=dashboards)
        print(deep)

        print("\n" + "=" * 50)


if __name__ == "__main__":
    TelegramDashboardLinks.print_links()
