"""GUI-based authentication credential provider."""

from __future__ import annotations

from PyQt6.QtWidgets import QInputDialog, QLineEdit, QWidget

from ukrgram.core.exceptions import AuthenticationError

_LOGIN_TITLE = "UkrGram — Login"


class GuiAuthProvider:
    """Collect login credentials through modal Qt input dialogs.

    Implements the :class:`~ukrgram.core.auth.AuthCredentialsProvider` protocol
    so it can be injected into the core client in place of the console provider
    without any change to the core layer (Dependency Inversion Principle).

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
        return self._ask("Enter phone number (international format):")

    async def get_code(self) -> str:
        """Prompt for the login code delivered by Telegram.

        Returns:
            The verification code.
        """
        return self._ask("Enter the login code from Telegram:")

    async def get_password(self) -> str:
        """Prompt for the two-step-verification password.

        Returns:
            The 2FA password.
        """
        return self._ask("Enter your 2FA password:", secret=True)

    def _ask(self, label: str, *, secret: bool = False) -> str:
        """Show a modal text-input dialog and return the entered value.

        Args:
            label: Prompt label shown to the user.
            secret: If ``True``, characters are masked (used for passwords).

        Returns:
            The stripped, non-empty user input.

        Raises:
            AuthenticationError: If the user cancels or submits an empty value.
        """
        echo_mode = QLineEdit.EchoMode.Password if secret else QLineEdit.EchoMode.Normal
        text, accepted = QInputDialog.getText(self._parent, _LOGIN_TITLE, label, echo_mode)
        if not accepted or not text.strip():
            raise AuthenticationError("Authentication was cancelled by the user.")
        return text.strip()
