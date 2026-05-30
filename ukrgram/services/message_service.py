"""Service exposing message history and sending to the upper layers."""

from __future__ import annotations

from telethon.tl.custom import Message

from ukrgram.core.client import TelegramClientManager
from ukrgram.core.resilience import retry_on_flood
from ukrgram.models.domain import MessageInfo
from ukrgram.utils.logger import get_logger

_LOGGER = get_logger(__name__)


class MessageService:
    """Read message history and send new messages for a given dialog.

    Args:
        manager: The started Telegram client manager.
    """

    def __init__(self, manager: TelegramClientManager) -> None:
        self._manager = manager

    @retry_on_flood()
    async def get_history(self, dialog_id: int, limit: int = 50) -> list[MessageInfo]:
        """Fetch recent messages for a dialog in chronological order.

        Args:
            dialog_id: Identifier of the target dialog entity.
            limit: Maximum number of messages to retrieve.

        Returns:
            Messages ordered oldest-first, as immutable DTOs.
        """
        messages = await self._manager.client.get_messages(dialog_id, limit=limit)
        history = [self._to_message_info(message) for message in reversed(messages)]
        _LOGGER.info("Fetched %d messages for dialog %s.", len(history), dialog_id)
        return history

    @retry_on_flood()
    async def send_message(self, dialog_id: int, text: str) -> MessageInfo:
        """Send a text message to a dialog.

        Args:
            dialog_id: Identifier of the target dialog entity.
            text: Message body to send.

        Returns:
            The sent message as an immutable DTO.
        """
        message = await self._manager.client.send_message(dialog_id, text)
        _LOGGER.info("Sent message %s to dialog %s.", message.id, dialog_id)
        return self._to_message_info(message)

    @staticmethod
    def _to_message_info(message: Message) -> MessageInfo:
        """Map a Telethon :class:`~telethon.tl.custom.Message` to a DTO.

        Args:
            message: The Telethon message object.

        Returns:
            The corresponding :class:`~ukrgram.models.domain.MessageInfo`.
        """
        return MessageInfo(
            id=message.id,
            sender_name=MessageService._resolve_sender_name(message),
            text=message.message or "",
            date=message.date,
            outgoing=bool(message.out),
        )

    @staticmethod
    def _resolve_sender_name(message: Message) -> str:
        """Derive a human-readable sender name from a message.

        Args:
            message: The Telethon message object.

        Returns:
            ``"You"`` for outgoing messages, the sender's name when resolvable,
            otherwise ``"Unknown"``.
        """
        if message.out:
            return "You"
        sender = message.sender
        if sender is None:
            return "Unknown"
        for attribute in ("first_name", "title", "username"):
            value = getattr(sender, attribute, None)
            if value:
                return str(value)
        return "Unknown"
