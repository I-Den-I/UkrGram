"""Plugin that auto-replies once to incoming private messages."""

from __future__ import annotations

from telethon import events

from ukrgram.automation.plugin_base import AutomationPlugin, HandlerRegistration
from ukrgram.utils.logger import get_logger

_LOGGER = get_logger(__name__)


class AutoReplyPlugin(AutomationPlugin):
    """Reply automatically to the first incoming message of each private chat.

    A per-session, in-memory set of answered chats guarantees each peer receives
    the auto-reply at most once, which prevents reply loops and spam.

    Args:
        reply_text: The message body sent as the automatic reply.
    """

    name = "auto_reply"
    description = "Replies once to incoming private messages."

    def __init__(self, reply_text: str) -> None:
        self._reply_text = reply_text
        self._answered: set[int] = set()

    def build_handlers(self) -> list[HandlerRegistration]:
        """Return the handler for incoming private messages.

        Returns:
            A single registration filtering incoming messages.
        """
        return [
            HandlerRegistration(
                event=events.NewMessage(incoming=True),
                callback=self._on_new_message,
            )
        ]

    async def _on_new_message(self, event: events.NewMessage.Event) -> None:
        """Send a one-time reply to a new incoming private message.

        Args:
            event: The incoming new-message event.
        """
        if not event.is_private:
            return
        chat_id = event.chat_id
        if chat_id in self._answered:
            return
        self._answered.add(chat_id)
        await event.reply(self._reply_text)
        _LOGGER.info("Auto-replied to chat %s.", chat_id)
