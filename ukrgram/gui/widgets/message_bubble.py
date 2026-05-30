"""Builder for a single chat message row with a styled bubble."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ukrgram.gui.widgets.avatar import avatar_color
from ukrgram.models.domain import MessageInfo

_MAX_BUBBLE_WIDTH = 460


def build_message_row(message: MessageInfo) -> QWidget:
    """Build a chat row containing a left- or right-aligned message bubble.

    Outgoing messages are aligned to the right with the accent bubble; incoming
    messages are aligned to the left and, in groups, prefixed with the colored
    sender name.

    Args:
        message: The message DTO to render.

    Returns:
        A widget wrapping the aligned, styled bubble.
    """
    bubble = QFrame()
    bubble.setObjectName("BubbleOut" if message.outgoing else "BubbleIn")
    bubble.setMaximumWidth(_MAX_BUBBLE_WIDTH)

    column = QVBoxLayout(bubble)
    column.setContentsMargins(12, 7, 12, 6)
    column.setSpacing(2)

    if not message.outgoing and message.sender_name and message.sender_name != "You":
        sender = QLabel(message.sender_name)
        sender.setStyleSheet(
            f"color: {avatar_color(message.sender_name).name()}; font-weight: 600;"
        )
        column.addWidget(sender)

    text = QLabel(message.text or " ")
    text.setObjectName("BubbleText")
    text.setWordWrap(True)
    text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    column.addWidget(text)

    meta = QLabel(message.date.astimezone().strftime("%H:%M") + ("  ✓" if message.outgoing else ""))
    meta.setObjectName("BubbleMeta")
    meta.setAlignment(Qt.AlignmentFlag.AlignRight)
    column.addWidget(meta)

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(10, 2, 10, 2)
    if message.outgoing:
        layout.addStretch(1)
        layout.addWidget(bubble)
    else:
        layout.addWidget(bubble)
        layout.addStretch(1)
    return row
