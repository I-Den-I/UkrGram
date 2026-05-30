"""GUI application bootstrap: wires PyQt6 to asyncio via qasync."""

from __future__ import annotations

import asyncio
import sys

from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from ukrgram.automation import AutomationEngine
from ukrgram.automation.plugins import AutoReplyPlugin, KeywordNotifierPlugin
from ukrgram.config import load_settings
from ukrgram.core import TelegramClientManager
from ukrgram.core.exceptions import UkrGramError
from ukrgram.gui.auth import GuiAuthProvider
from ukrgram.gui.controllers import AppController
from ukrgram.gui.main_window import MainWindow
from ukrgram.gui.theme import build_stylesheet
from ukrgram.services import DialogService, MessageService
from ukrgram.utils import configure_logging, get_logger

_LOGGER = get_logger("ukrgram.gui")


async def _lifecycle(
    controller: AppController,
    manager: TelegramClientManager,
    close_event: asyncio.Event,
) -> None:
    """Drive the application from start-up to a clean shutdown.

    Args:
        controller: The application controller to start.
        manager: The client manager to disconnect on shutdown.
        close_event: Event set when the application is about to quit.
    """
    await controller.start()
    await close_event.wait()
    await manager.stop()
    _LOGGER.info("Application shut down cleanly.")


def run_app() -> int:
    """Launch the UkrGram desktop GUI on a qasync-bridged event loop.

    Returns:
        Process exit code: ``0`` on normal shutdown, ``1`` on fatal config error.
    """
    try:
        settings = load_settings()
    except UkrGramError as exc:
        configure_logging()
        _LOGGER.error("Cannot start UkrGram: %s", exc)
        return 1

    configure_logging(settings.log_level)

    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(build_stylesheet())
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    window = MainWindow()
    auth_provider = GuiAuthProvider(parent=window)
    manager = TelegramClientManager(settings, auth_provider)
    engine = AutomationEngine(manager)
    engine.register_plugin(AutoReplyPlugin(settings.auto_reply_text))
    engine.register_plugin(KeywordNotifierPlugin(settings.keyword_list))
    controller = AppController(
        window=window,
        manager=manager,
        dialog_service=DialogService(manager),
        message_service=MessageService(manager),
        engine=engine,
    )

    close_event = asyncio.Event()
    app.aboutToQuit.connect(close_event.set)

    window.show()
    with event_loop:
        event_loop.run_until_complete(_lifecycle(controller, manager, close_event))
    return 0
