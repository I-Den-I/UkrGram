"""Application settings loaded from environment variables / .env file."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


class Settings(BaseSettings):
    """Strongly-typed application configuration.

    Values are read from environment variables or a local ``.env`` file. The
    secret ``api_hash`` is wrapped in :class:`~pydantic.SecretStr` to avoid
    accidental exposure in logs or tracebacks.

    Attributes:
        api_id: Telegram API ID issued at https://my.telegram.org/apps.
        api_hash: Telegram API hash paired with ``api_id``.
        session_name: Base file name for the Telethon session.
        session_dir: Directory where session files are stored.
        phone: Optional phone number (international format) used for login.
        log_level: Root logging level name (e.g. ``INFO``, ``DEBUG``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_id: int = Field(..., description="Telegram API ID.")
    api_hash: SecretStr = Field(..., description="Telegram API hash.")
    session_name: str = Field(default="ukrgram", description="Session file base name.")
    session_dir: Path = Field(default=Path("./sessions"), description="Session storage directory.")
    phone: str | None = Field(default=None, description="Optional login phone number.")
    log_level: str = Field(default="INFO", description="Root logging level.")

    @field_validator("log_level")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        """Normalize and validate the logging level name.

        Args:
            value: Raw level string from configuration.

        Returns:
            The upper-cased, validated level name.

        Raises:
            ValueError: If ``value`` is not a recognized logging level.
        """
        normalized = value.strip().upper()
        if normalized not in _VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid log level '{value}'. Expected one of {sorted(_VALID_LOG_LEVELS)}."
            )
        return normalized

    @property
    def session_path(self) -> Path:
        """Build the absolute Telethon session file path (without suffix).

        Returns:
            Full path composed from ``session_dir`` and ``session_name``.
        """
        return self.session_dir.expanduser().resolve() / self.session_name


def load_settings() -> Settings:
    """Instantiate :class:`Settings` from the environment.

    Returns:
        A validated :class:`Settings` instance.

    Raises:
        ConfigurationError: If required configuration is missing or invalid.
    """
    from ukrgram.core.exceptions import ConfigurationError

    try:
        return Settings()  # type: ignore[call-arg]
    except Exception as exc:
        raise ConfigurationError(f"Failed to load application settings: {exc}") from exc
