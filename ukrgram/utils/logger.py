"""Centralized logging configuration."""

from __future__ import annotations

import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger for the application.

    Idempotent: repeated calls replace existing handlers instead of stacking
    them, preventing duplicated log lines on re-initialization.

    Args:
        level: Logging level name (e.g. ``INFO``, ``DEBUG``).
    """
    root = logging.getLogger()
    root.setLevel(level)

    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(handler)

    logging.getLogger("telethon").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        A :class:`logging.Logger` instance for ``name``.
    """
    return logging.getLogger(name)
