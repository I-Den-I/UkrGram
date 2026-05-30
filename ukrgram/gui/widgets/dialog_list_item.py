"""Custom row widget for the dialog (chat) list."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ukrgram.gui.widgets.avatar import make_avatar
from ukrgram.models.domain import DialogInfo


def _format_time(value: datetime | None) -> str:
    """Format a dialog timestamp as ``HH:MM`` for today, else ``dd.MM``.

    Args:
        value: The timestamp of the last message, if any.

    Returns:
        A short time/date string, or an empty string when ``value`` is ``None``.
    """
    if value is None:
        return ""
    local = value.astimezone()
    now = datetime.now().astimezone()
    if local.date() == now.date():
        return local.strftime("%H:%M")
    return local.strftime("%d.%m")


def _elide(text: str, limit: int) -> str:
    """Collapse whitespace and truncate ``text`` to ``limit`` characters.

    Args:
        text: The raw text to shorten.
        limit: Maximum number of characters before an ellipsis is added.

    Returns:
        A single-line, length-bounded string.
    """
    flattened = " ".join(text.split())
    return flattened if len(flattened) <= limit else flattened[: limit - 1] + "…"


class DialogListItem(QWidget):
    """Row widget showing a dialog's avatar, title, preview, time and badge.

    Args:
        dialog: The dialog DTO to render.
    """

    def __init__(self, dialog: DialogInfo) -> None:
        super().__init__()
        self._build(dialog)

    def _build(self, dialog: DialogInfo) -> None:
        """Assemble the row's widget tree.

        Args:
            dialog: The dialog DTO to render.
        """
        avatar = QLabel()
        avatar.setPixmap(make_avatar(dialog.title, dialog.id))
        avatar.setFixedSize(46, 46)

        title = QLabel(_elide(dialog.title, 24))
        title.setObjectName("DialogTitle")
        time = QLabel(_format_time(dialog.timestamp))
        time.setObjectName("DialogTime")

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.addWidget(title)
        top_row.addStretch(1)
        top_row.addWidget(time)

        preview = QLabel(_elide(dialog.last_message, 38) or " ")
        preview.setObjectName("DialogPreview")
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.addWidget(preview)
        bottom_row.addStretch(1)
        if dialog.unread_count:
            badge = QLabel(str(dialog.unread_count))
            badge.setObjectName("UnreadBadge")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bottom_row.addWidget(badge)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(3)
        text_column.addLayout(top_row)
        text_column.addLayout(bottom_row)

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 7, 10, 7)
        row.setSpacing(10)
        row.addWidget(avatar)
        row.addLayout(text_column)
