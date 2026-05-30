"""Immutable domain models (DTOs) shared across layers."""

from __future__ import annotations

from dataclasses import dataclass


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
