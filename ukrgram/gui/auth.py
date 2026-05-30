"""GUI-based authentication credential provider."""

from __future__ import annotations

import asyncio

from PyQt6.QtWidgets import QInputDialog, QLineEdit, QWidget

from ukrgram.core.exceptions import AuthenticationError

_LOGIN_TITLE = "UkrGram — Login"
_CANCELLED_MESSAGE = "Authentication was cancelled by the user."


class GuiAuthProvider:
    """Collect login credentials through non-blocking modal Qt dialogs.

    Implements the :class:`~ukrgram.core.auth.AuthCredentialsProvider` protocol
    so it can be injected into the core client in place of the console provider
    without any change to the core layer (Dependency Inversion Principle).

    Dialogs are shown with :meth:`QInputDialog.open` and their results are
    delivered through an :class:`asyncio.Future`. A blocking
    ``QInputDialog.getText`` would spin a *nested* Qt event loop and re-enter the
    running asyncio task, which is illegal while Telethon's connection tasks are
    active under qasync.

    Args:
        parent: Optional parent widget used to anchor the modal dialogs.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        self._parent = parent

    async def get_phone(self) -> str:
        """Prompt for the account phone number.

        Returns:
            The phone number in international format.
        """
        return await self._ask("Enter phone number (international format):")

    async def get_code(self) -> str:
        """Prompt for the login code delivered by Telegram.

        Returns:
            The verification code.
        """
        return await self._ask("Enter the login code from Telegram:")

    async def get_password(self) -> str:
        """Prompt for the two-step-verification password.

        Returns:
            The 2FA password.
        """
        return await self._ask("Enter your 2FA password:", secret=True)

    async def _ask(self, label: str, *, secret: bool = False) -> str:
        """Show a non-blocking modal input dialog and await its result.

        Args:
            label: Prompt label shown to the user.
            secret: If ``True``, characters are masked (used for passwords).

        Returns:
            The stripped, non-empty user input.

        Raises:
            AuthenticationError: If the user cancels or submits an empty value.
        """
        loop = asyncio.get_running_loop()
        future: asyncio.Future[str] = loop.create_future()

        dialog = QInputDialog(self._parent)
        dialog.setWindowTitle(_LOGIN_TITLE)
        dialog.setLabelText(label)
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        if secret:
            dialog.setTextEchoMode(QLineEdit.EchoMode.Password)

        def _accept() -> None:
            if future.done():
                return
            value = dialog.textValue().strip()
            if value:
                future.set_result(value)
            else:
                future.set_exception(AuthenticationError(_CANCELLED_MESSAGE))

        def _reject() -> None:
            if not future.done():
                future.set_exception(AuthenticationError(_CANCELLED_MESSAGE))

        dialog.accepted.connect(_accept)
        dialog.rejected.connect(_reject)
        dialog.open()
        try:
            return await future
        finally:
            dialog.deleteLater()
