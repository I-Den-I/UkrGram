"""Generation of round, colored initial-based avatars (Telegram style)."""

from __future__ import annotations

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPixmap

_AVATAR_COLORS: tuple[str, ...] = (
    "#e17076",
    "#eda86c",
    "#a695e7",
    "#7bc862",
    "#6ec9cb",
    "#65aadd",
    "#ee7aae",
)


def avatar_color(key: int | str) -> QColor:
    """Pick a stable avatar color for a given key.

    Args:
        key: A dialog id (int) or a name (str) used to choose the color.

    Returns:
        A :class:`~PyQt6.QtGui.QColor` from the Telegram-like palette.
    """
    index = (key if isinstance(key, int) else sum(ord(char) for char in key))
    return QColor(_AVATAR_COLORS[index % len(_AVATAR_COLORS)])


def _initials(title: str) -> str:
    """Derive up to two uppercase initials from a title.

    Args:
        title: The dialog or sender title.

    Returns:
        One or two characters, or ``"#"`` when the title is empty.
    """
    parts = [part for part in title.strip().split() if part]
    if not parts:
        return "#"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[1][0]).upper()


def make_avatar(title: str, key: int | str, size: int = 46) -> QPixmap:
    """Render a round avatar with centered initials on a colored disc.

    Args:
        title: Text whose initials are drawn.
        key: Key selecting the background color (id or name).
        size: Avatar diameter in pixels.

    Returns:
        A square :class:`~PyQt6.QtGui.QPixmap` containing the avatar.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(avatar_color(key)))
    painter.drawEllipse(0, 0, size, size)

    font = QFont()
    font.setPixelSize(int(size * 0.4))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, _initials(title))
    painter.end()
    return pixmap
