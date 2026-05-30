"""UkrGram application entry point.

Launches the PyQt6 GUI, which drives the Telethon core client through the
service layer over a single asyncio event loop bridged by qasync.
"""

from __future__ import annotations

from ukrgram.gui import run_app


def main() -> None:
    """Synchronous entry point invoked by ``python main.py``."""
    raise SystemExit(run_app())


if __name__ == "__main__":
    main()
