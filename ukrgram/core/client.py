"""Telegram client lifecycle management."""

from __future__ import annotations

from types import TracebackType

from telethon import TelegramClient
from telethon.errors import RPCError
from telethon.tl.types import User

from ukrgram.config.settings import Settings
from ukrgram.core.auth import AuthCredentialsProvider
from ukrgram.core.exceptions import AuthenticationError, ClientConnectionError
from ukrgram.core.resilience import retry_on_flood
from ukrgram.models.domain import AccountInfo
from ukrgram.utils.logger import get_logger

_LOGGER = get_logger(__name__)


class TelegramClientManager:
    """Own the Telethon client lifecycle: connection, auth and teardown.

    This manager is the single entry point through which higher layers obtain a
    connected, authorized :class:`~telethon.TelegramClient`. It is usable as an
    async context manager.

    Args:
        settings: Validated application settings.
        auth_provider: Source of interactive login credentials.
    """

    def __init__(self, settings: Settings, auth_provider: AuthCredentialsProvider) -> None:
        self._settings = settings
        self._auth = auth_provider
        self._client: TelegramClient | None = None

    @property
    def client(self) -> TelegramClient:
        """Return the underlying connected client.

        Returns:
            The active :class:`~telethon.TelegramClient`.

        Raises:
            ClientConnectionError: If accessed before :meth:`start`.
        """
        if self._client is None:
            raise ClientConnectionError("Client is not started. Call start() first.")
        return self._client

    async def start(self) -> None:
        """Connect to Telegram and ensure the session is authorized.

        Creates the session directory if needed, opens the connection and runs
        the interactive login flow when the stored session is not yet authorized.

        Raises:
            ClientConnectionError: If the network connection cannot be opened.
            AuthenticationError: If the interactive login flow fails.
        """
        self._settings.session_dir.mkdir(parents=True, exist_ok=True)
        client = TelegramClient(
            session=str(self._settings.session_path),
            api_id=self._settings.api_id,
            api_hash=self._settings.api_hash.get_secret_value(),
        )

        try:
            await client.connect()
        except OSError as exc:
            raise ClientConnectionError(f"Unable to connect to Telegram: {exc}") from exc

        try:
            if not await client.is_user_authorized():
                _LOGGER.info("Session is not authorized; starting interactive login.")
                await client.start(
                    phone=self._auth.get_phone,
                    code_callback=self._auth.get_code,
                    password=self._auth.get_password,
                )
        except RPCError as exc:
            await client.disconnect()
            raise AuthenticationError(f"Telegram authentication failed: {exc}") from exc

        self._client = client
        _LOGGER.info("Telegram client started and authorized.")

    async def stop(self) -> None:
        """Disconnect the client and release resources."""
        if self._client is not None:
            await self._client.disconnect()
            self._client = None
            _LOGGER.info("Telegram client disconnected.")

    @retry_on_flood()
    async def get_me(self) -> AccountInfo:
        """Fetch information about the authenticated account.

        Returns:
            An :class:`AccountInfo` snapshot of the current user.

        Raises:
            AuthenticationError: If account information cannot be retrieved.
        """
        user = await self.client.get_me()
        if not isinstance(user, User):
            raise AuthenticationError("Failed to retrieve authenticated account.")
        return AccountInfo(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            phone=user.phone,
        )

    async def __aenter__(self) -> TelegramClientManager:
        """Enter the async context, starting the client.

        Returns:
            This manager instance, started and authorized.
        """
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the async context, stopping the client."""
        await self.stop()
