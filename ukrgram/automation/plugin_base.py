"""Base abstractions for the automation plugin system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from telethon.events.common import EventBuilder, EventCommon

EventCallback = Callable[[EventCommon], Awaitable[None]]


@dataclass(frozen=True)
class HandlerRegistration:
    """Binding between a Telethon event filter and its async callback.

    Attributes:
        event: The Telethon event builder used as a filter.
        callback: The coroutine invoked when a matching event arrives.
    """

    event: EventBuilder
    callback: EventCallback


class AutomationPlugin(ABC):
    """Base class for userbot automation plugins.

    A plugin is a self-contained unit of automation. It declares the event
    handlers it contributes; the :class:`~ukrgram.automation.engine.AutomationEngine`
    is responsible for attaching and detaching them. New behaviors are added as
    new plugins without modifying the engine (Open/Closed Principle).

    Attributes:
        name: Stable, unique identifier of the plugin.
        description: Human-readable summary of what the plugin does.
    """

    name: str = "unnamed"
    description: str = ""

    @abstractmethod
    def build_handlers(self) -> list[HandlerRegistration]:
        """Return the event handlers contributed by this plugin.

        Returns:
            A list of :class:`HandlerRegistration` bindings; may be empty when
            the plugin is configured to do nothing.
        """
