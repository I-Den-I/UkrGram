"""Plugin that logs incoming messages matching configured keywords."""

from __future__ import annotations

from telethon import events

from ukrgram.automation.plugin_base import AutomationPlugin, HandlerRegistration
from ukrgram.utils.logger import get_logger

_LOGGER = get_logger(__name__)


class KeywordNotifierPlugin(AutomationPlugin):
    """Log a warning whenever an incoming message contains a tracked keyword.

    Matching is case-insensitive. When no keywords are configured the plugin
    contributes no handlers, adding zero runtime overhead.

    Args:
        keywords: Keywords to watch for in incoming messages.
    """

    name = "keyword_notifier"
    description = "Logs incoming messages that contain tracked keywords."

    def __init__(self, keywords: list[str]) -> None:
        self._keywords = [keyword.lower() for keyword in keywords if keyword.strip()]

    def build_handlers(self) -> list[HandlerRegistration]:
        """Return the handler, or nothing when no keywords are configured.

        Returns:
            A single registration, or an empty list when there are no keywords.
        """
        if not self._keywords:
            return []
        return [
            HandlerRegistration(
                event=events.NewMessage(incoming=True),
                callback=self._on_new_message,
            )
        ]

    async def _on_new_message(self, event: events.NewMessage.Event) -> None:
        """Log incoming messages that contain any tracked keyword.

        Args:
            event: The incoming new-message event.
        """
        text = (event.raw_text or "").lower()
        matched = [keyword for keyword in self._keywords if keyword in text]
        if matched:
            _LOGGER.warning("Keyword match %s in chat %s.", matched, event.chat_id)
