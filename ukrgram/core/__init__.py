"""Core layer: Telegram client lifecycle, authentication and resilience."""

from ukrgram.core.client import TelegramClientManager
from ukrgram.core.exceptions import (
    AuthenticationError,
    ClientConnectionError,
    ConfigurationError,
    ServiceError,
    UkrGramError,
)

__all__ = [
    "TelegramClientManager",
    "UkrGramError",
    "ConfigurationError",
    "AuthenticationError",
    "ClientConnectionError",
    "ServiceError",
]
