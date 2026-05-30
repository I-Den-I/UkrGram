"""Reusable themed widgets for the UkrGram GUI."""

from ukrgram.gui.widgets.avatar import avatar_color, make_avatar
from ukrgram.gui.widgets.chat_view import ChatView
from ukrgram.gui.widgets.dialog_list_item import DialogListItem
from ukrgram.gui.widgets.message_bubble import build_message_row

__all__ = [
    "avatar_color",
    "make_avatar",
    "ChatView",
    "DialogListItem",
    "build_message_row",
]
