"""Automation engine: attaches plugin handlers to the Telegram client."""

from __future__ import annotations

from ukrgram.automation.plugin_base import AutomationPlugin, HandlerRegistration
from ukrgram.core.client import TelegramClientManager
from ukrgram.utils.logger import get_logger

_LOGGER = get_logger(__name__)


class AutomationEngine:
    """Manage the lifecycle of automation plugins and their event handlers.

    The engine attaches every registered plugin's handlers to the underlying
    Telethon client when started, and detaches them when stopped. Handlers run
    as coroutines on the same event loop as the rest of the application.

    Args:
        manager: The started Telegram client manager whose client receives the
            event handlers.
    """

    def __init__(self, manager: TelegramClientManager) -> None:
        self._manager = manager
        self._plugins: list[AutomationPlugin] = []
        self._active: list[HandlerRegistration] = []
        self._running = False

    @property
    def is_running(self) -> bool:
        """Return whether the engine is currently dispatching events.

        Returns:
            ``True`` if handlers are attached, ``False`` otherwise.
        """
        return self._running

    @property
    def plugin_names(self) -> list[str]:
        """Return the names of the registered plugins.

        Returns:
            The ``name`` of each registered plugin, in registration order.
        """
        return [plugin.name for plugin in self._plugins]

    def register_plugin(self, plugin: AutomationPlugin) -> None:
        """Register a plugin with the engine.

        Args:
            plugin: The plugin instance to register.

        Raises:
            RuntimeError: If called while the engine is running.
        """
        if self._running:
            raise RuntimeError("Cannot register plugins while the engine is running.")
        self._plugins.append(plugin)
        _LOGGER.info("Registered automation plugin '%s'.", plugin.name)

    def start(self) -> None:
        """Attach every registered plugin's handlers to the client.

        Idempotent: a second call while running is a no-op.

        Raises:
            ClientConnectionError: If the client is not started.
        """
        if self._running:
            return
        client = self._manager.client
        for plugin in self._plugins:
            for registration in plugin.build_handlers():
                client.add_event_handler(registration.callback, registration.event)
                self._active.append(registration)
        self._running = True
        _LOGGER.info(
            "Automation engine started: %d handler(s) from %d plugin(s).",
            len(self._active),
            len(self._plugins),
        )

    def stop(self) -> None:
        """Detach all active handlers from the client.

        Idempotent: a call while stopped is a no-op.
        """
        if not self._running:
            return
        client = self._manager.client
        for registration in self._active:
            client.remove_event_handler(registration.callback, registration.event)
        self._active.clear()
        self._running = False
        _LOGGER.info("Automation engine stopped.")
