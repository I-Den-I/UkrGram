"""Service layer: high-level operations built on top of the core client."""

from ukrgram.services.dialog_service import DialogService
from ukrgram.services.message_service import MessageService

__all__ = ["DialogService", "MessageService"]
