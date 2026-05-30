"""Scrollable conversation view rendering message bubbles."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from ukrgram.gui.widgets.message_bubble import build_message_row
from ukrgram.models.domain import MessageInfo


class ChatView(QScrollArea):
    """A vertically scrolling list of message bubbles with auto-scroll.

    A leading stretch keeps a short conversation anchored to the bottom, the way
    desktop chat clients do; new messages are appended below and the view scrolls
    to reveal them.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ChatScroll")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setObjectName("ChatContainer")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(6, 8, 6, 8)
        self._layout.setSpacing(2)
        self._layout.addStretch(1)
        self.setWidget(self._container)

    def clear(self) -> None:
        """Remove all message rows, keeping the leading stretch."""
        while self._layout.count() > 1:
            item = self._layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def set_messages(self, messages: list[MessageInfo]) -> None:
        """Replace the view contents with the given messages.

        Args:
            messages: Messages ordered oldest-first.
        """
        self.clear()
        for message in messages:
            self._layout.addWidget(build_message_row(message))
        self._scroll_to_bottom()

    def add_message(self, message: MessageInfo) -> None:
        """Append a single message and scroll to the bottom.

        Args:
            message: The message DTO to append.
        """
        self._layout.addWidget(build_message_row(message))
        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        """Scroll to the newest message after the layout has settled."""
        scrollbar = self.verticalScrollBar()
        QTimer.singleShot(0, lambda: scrollbar.setValue(scrollbar.maximum()))
