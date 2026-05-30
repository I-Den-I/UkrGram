"""Service exposing Telegram dialogs (chats) to the upper layers."""

from __future__ import annotations

from telethon.tl.custom import Dialog

from ukrgram.core.client import TelegramClientManager
from ukrgram.core.resilience import retry_on_flood
from ukrgram.models.domain import DialogInfo
from ukrgram.utils.logger import get_logger

_LOGGER = get_logger(__name__)


class DialogService:
    """Provide read access to the authenticated account's dialogs.

    Acts as a boundary between the GUI and Telethon: callers receive immutable
    :class:`~ukrgram.models.domain.DialogInfo` DTOs and never touch raw
    Telethon objects.

    Args:
        manager: The started Telegram client manager.
    """

    def __init__(self, manager: TelegramClientManager) -> None:
        self._manager = manager

    @retry_on_flood()
    async def list_dialogs(self, limit: int = 50) -> list[DialogInfo]:
        """Fetch the most recent dialogs ordered by Telegram's default ranking.

        Args:
            limit: Maximum number of dialogs to retrieve.

        Returns:
            A list of :class:`~ukrgram.models.domain.DialogInfo` DTOs.
        """
        dialogs = await self._manager.client.get_dialogs(limit=limit)
        result = [self._to_dialog_info(dialog) for dialog in dialogs]
        _LOGGER.info("Fetched %d dialogs.", len(result))
        return result

    @staticmethod
    def _to_dialog_info(dialog: Dialog) -> DialogInfo:
        """Map a Telethon :class:`~telethon.tl.custom.Dialog` to a DTO.

        Args:
            dialog: The Telethon dialog object.

        Returns:
            The corresponding :class:`~ukrgram.models.domain.DialogInfo`.
        """
        last = dialog.message
        return DialogInfo(
            id=dialog.id,
            title=dialog.name or "Unknown",
            unread_count=dialog.unread_count,
            is_user=bool(dialog.is_user),
            is_group=bool(dialog.is_group),
            is_channel=bool(dialog.is_channel),
            last_message=(last.message or "") if last is not None else "",
            timestamp=last.date if last is not None else None,
        )
