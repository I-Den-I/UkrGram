"""Immutable domain models (DTOs) shared across layers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AccountInfo:
    """Snapshot of the authenticated Telegram account.

    Attributes:
        id: Unique Telegram user identifier.
        first_name: Account holder's first name, if set.
        last_name: Account holder's last name, if set.
        username: Public ``@username``, if set.
        phone: Phone number associated with the account, if visible.
    """

    id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    phone: str | None

    @property
    def display_name(self) -> str:
        """Build a human-readable display name.

        Returns:
            The full name when available, otherwise the username, otherwise the id.
        """
        full_name = " ".join(part for part in (self.first_name, self.last_name) if part)
        if full_name:
            return full_name
        if self.username:
            return f"@{self.username}"
        return str(self.id)


@dataclass(frozen=True, slots=True)
class DialogInfo:
    """Lightweight summary of a Telegram dialog (chat) for list rendering.

    Attributes:
        id: Unique identifier of the dialog's entity (user, group or channel).
        title: Human-readable dialog title.
        unread_count: Number of unread messages in the dialog.
        is_user: ``True`` if the dialog is a one-to-one private chat.
        is_group: ``True`` if the dialog is a group chat.
        is_channel: ``True`` if the dialog is a broadcast channel.
    """

    id: int
    title: str
    unread_count: int
    is_user: bool
    is_group: bool
    is_channel: bool
    last_message: str = ""
    timestamp: datetime | None = None

    @property
    def kind(self) -> str:
        """Return a short single-character marker describing the dialog kind.

        Returns:
            ``"@"`` for users, ``"#"`` for channels, ``"*"`` for groups.
        """
        if self.is_user:
            return "@"
        if self.is_channel:
            return "#"
        return "*"


@dataclass(frozen=True, slots=True)
class MessageInfo:
    """Immutable representation of a single Telegram message.

    Attributes:
        id: Unique message identifier within its dialog.
        sender_name: Display name of the sender (or ``"You"`` for outgoing).
        text: Plain-text body of the message; empty for media-only messages.
        date: Timestamp at which the message was sent.
        outgoing: ``True`` if the message was sent by the current account.
    """

    id: int
    sender_name: str
    text: str
    date: datetime
    outgoing: bool
