"""Domain-specific exception hierarchy for UkrGram."""

from __future__ import annotations


class UkrGramError(Exception):
    """Base class for all UkrGram domain errors."""


class ConfigurationError(UkrGramError):
    """Raised when application configuration is missing or invalid."""


class AuthenticationError(UkrGramError):
    """Raised when Telegram authentication fails or is aborted."""


class ClientConnectionError(UkrGramError):
    """Raised when the client cannot establish or maintain a connection."""


class ServiceError(UkrGramError):
    """Raised when a high-level service operation fails."""
