"""Application controller bridging the view and the async service layer."""

from __future__ import annotations

import asyncio

from PyQt6.QtWidgets import QListWidgetItem

from ukrgram.core.client import TelegramClientManager
from ukrgram.core.exceptions import UkrGramError
from ukrgram.gui.main_window import MainWindow
from ukrgram.services import DialogService, MessageService
from ukrgram.utils.logger import get_logger

_LOGGER = get_logger(__name__)


class AppController:
    """Translate user interactions into async service calls and update the view.

    The controller owns no UI widgets directly; it observes the window's signals
    and mutates the window through its public methods. Synchronous Qt slots
    schedule coroutines on the shared qasync event loop.

    Args:
        window: The main application window (view).
        manager: The Telegram client manager (core).
        dialog_service: Service providing dialog listings.
        message_service: Service providing message history and sending.
    """

    def __init__(
        self,
        window: MainWindow,
        manager: TelegramClientManager,
        dialog_service: DialogService,
        message_service: MessageService,
    ) -> None:
        self._window = window
        self._manager = manager
        self._dialogs = dialog_service
        self._messages = message_service
        self._dialog_titles: dict[int, str] = {}
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect window signals to scheduling slots."""
        self._window.dialog_list.itemClicked.connect(self._on_dialog_clicked)
        self._window.send_button.clicked.connect(self._on_send_clicked)
        self._window.message_input.returnPressed.connect(self._on_send_clicked)

    def _on_dialog_clicked(self, _item: QListWidgetItem) -> None:
        """Schedule loading of the conversation for the clicked dialog."""
        asyncio.ensure_future(self._load_conversation())

    def _on_send_clicked(self) -> None:
        """Schedule sending of the message currently in the input field."""
        asyncio.ensure_future(self._send_current_message())

    async def start(self) -> None:
        """Connect, authenticate and populate the dialog list.

        All :class:`~ukrgram.core.exceptions.UkrGramError` failures are reported
        in the status bar instead of propagating, so the window stays open.
        """
        try:
            self._window.set_status("Connecting to Telegram…")
            await self._manager.start()
            account = await self._manager.get_me()
            self._window.set_status(f"Connected as {account.display_name}")
            dialogs = await self._dialogs.list_dialogs()
            self._dialog_titles = {dialog.id: dialog.title for dialog in dialogs}
            self._window.set_dialogs(dialogs)
        except UkrGramError as exc:
            _LOGGER.error("Failed to start session: %s", exc)
            self._window.set_status(f"Error: {exc}")

    async def _load_conversation(self) -> None:
        """Load and display the message history for the selected dialog."""
        dialog_id = self._window.selected_dialog_id()
        if dialog_id is None:
            return
        title = self._dialog_titles.get(dialog_id, "Chat")
        try:
            self._window.set_status(f"Loading '{title}'…")
            messages = await self._messages.get_history(dialog_id)
            self._window.set_conversation(title, messages)
            self._window.set_status(f"Conversation: {title}")
        except UkrGramError as exc:
            _LOGGER.error("Failed to load conversation %s: %s", dialog_id, exc)
            self._window.set_status(f"Error: {exc}")

    async def _send_current_message(self) -> None:
        """Send the input-field text to the selected dialog."""
        dialog_id = self._window.selected_dialog_id()
        if dialog_id is None:
            self._window.set_status("Select a chat before sending.")
            return
        text = self._window.take_input_text()
        if not text:
            return
        try:
            message = await self._messages.send_message(dialog_id, text)
            self._window.append_message(message)
        except UkrGramError as exc:
            _LOGGER.error("Failed to send message: %s", exc)
            self._window.set_status(f"Error: {exc}")
