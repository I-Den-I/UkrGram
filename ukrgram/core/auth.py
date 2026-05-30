"""Authentication credential providers (Dependency Inversion boundary)."""

from __future__ import annotations

import asyncio
import getpass
from typing import Protocol, runtime_checkable


@runtime_checkable
class AuthCredentialsProvider(Protocol):
    """Protocol supplying interactive credentials during Telegram login.

    Implementations decouple the authentication flow from any specific UI,
    allowing a console prompt, a GUI dialog, or an automated source to be
    injected interchangeably (Dependency Inversion Principle).
    """

    async def get_phone(self) -> str:
        """Return the account phone number in international format."""
        ...

    async def get_code(self) -> str:
        """Return the login code delivered by Telegram."""
        ...

    async def get_password(self) -> str:
        """Return the two-step-verification (2FA) password."""
        ...


class ConsoleAuthProvider:
    """Console-based credential provider for headless/CLI bootstrap.

    Prompts run in a thread-pool executor so that blocking ``input``/``getpass``
    calls never stall the asyncio event loop.

    Args:
        default_phone: Optional phone number to use without prompting.
    """

    def __init__(self, default_phone: str | None = None) -> None:
        self._default_phone = default_phone

    @staticmethod
    async def _prompt(prompt: str, *, secret: bool = False) -> str:
        """Read a single line of input off the event loop.

        Args:
            prompt: Text shown to the user.
            secret: If ``True``, the input is hidden (used for passwords).

        Returns:
            The stripped user input.
        """
        reader = getpass.getpass if secret else input
        loop = asyncio.get_running_loop()
        value = await loop.run_in_executor(None, reader, prompt)
        return value.strip()

    async def get_phone(self) -> str:
        """Return the configured phone number or prompt for one.

        Returns:
            The account phone number in international format.
        """
        if self._default_phone:
            return self._default_phone
        return await self._prompt("Enter phone number (international format): ")

    async def get_code(self) -> str:
        """Prompt for the Telegram login code.

        Returns:
            The verification code entered by the user.
        """
        return await self._prompt("Enter the login code you received: ")

    async def get_password(self) -> str:
        """Prompt for the two-step-verification password.

        Returns:
            The 2FA password entered by the user.
        """
        return await self._prompt("Enter your 2FA password: ", secret=True)
