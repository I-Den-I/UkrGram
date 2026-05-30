"""UkrGram bootstrap entry point.

Performs a headless authentication check against Telegram using the core layer.
This validates configuration, session handling and resilience before the PyQt6
GUI layer is wired on top of the same client in a later iteration.
"""

from __future__ import annotations

import asyncio

from ukrgram.config import load_settings
from ukrgram.core import TelegramClientManager, UkrGramError
from ukrgram.core.auth import ConsoleAuthProvider
from ukrgram.utils import configure_logging, get_logger


async def bootstrap() -> int:
    """Run the authentication bootstrap flow.

    Returns:
        Process exit code: ``0`` on success, ``1`` on a handled failure.
    """
    configure_logging()
    logger = get_logger("ukrgram.main")

    try:
        settings = load_settings()
        configure_logging(settings.log_level)
        auth_provider = ConsoleAuthProvider(default_phone=settings.phone)
        async with TelegramClientManager(settings, auth_provider) as manager:
            account = await manager.get_me()
            logger.info(
                "Authenticated as %s (id=%s, username=%s).",
                account.display_name,
                account.id,
                account.username or "—",
            )
        return 0
    except UkrGramError as exc:
        logger.error("Startup failed: %s", exc)
        return 1


def main() -> None:
    """Synchronous entry point invoked by ``python main.py``."""
    raise SystemExit(asyncio.run(bootstrap()))


if __name__ == "__main__":
    main()
