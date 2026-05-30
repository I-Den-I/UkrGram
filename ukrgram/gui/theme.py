"""Telegram-like dark theme: color palette and Qt style sheet."""

from __future__ import annotations

PALETTE: dict[str, str] = {
    "window_bg": "#0e1621",
    "sidebar_bg": "#17212b",
    "sidebar_item_hover": "#202b36",
    "sidebar_item_selected": "#2b5278",
    "chat_bg": "#0e1621",
    "header_bg": "#17212b",
    "divider": "#101921",
    "bubble_in": "#182533",
    "bubble_out": "#2b5278",
    "text": "#ffffff",
    "text_muted": "#6d7f8f",
    "accent": "#3390ec",
    "input_bg": "#242f3d",
    "scrollbar": "#2b3947",
}


def build_stylesheet() -> str:
    """Build the application-wide Qt style sheet.

    Returns:
        A QSS string themed after the Telegram desktop dark palette.
    """
    p = PALETTE
    return f"""
    QMainWindow {{ background-color: {p['window_bg']}; }}
    QWidget {{ color: {p['text']}; font-size: 13px; }}
    #Sidebar {{
        background-color: {p['sidebar_bg']};
        border: none;
        outline: 0;
    }}
    #Sidebar::item {{
        border: none;
        padding: 0px;
    }}
    #Sidebar::item:hover {{
        background-color: {p['sidebar_item_hover']};
    }}
    #Sidebar::item:selected {{
        background-color: {p['sidebar_item_selected']};
    }}
    #ChatHeader {{
        background-color: {p['header_bg']};
        border-bottom: 1px solid {p['divider']};
    }}
    #ChatTitle {{ font-size: 15px; font-weight: 600; color: {p['text']}; }}
    #ChatSubtitle {{ font-size: 12px; color: {p['text_muted']}; }}
    #ChatScroll {{ border: none; background-color: {p['chat_bg']}; }}
    #ChatContainer {{ background-color: {p['chat_bg']}; }}
    #EmptyHint {{ color: {p['text_muted']}; font-size: 14px; }}
    #BubbleIn {{ background-color: {p['bubble_in']}; border-radius: 12px; }}
    #BubbleOut {{ background-color: {p['bubble_out']}; border-radius: 12px; }}
    #BubbleText {{ color: {p['text']}; font-size: 13px; }}
    #BubbleMeta {{ color: rgba(255, 255, 255, 0.55); font-size: 11px; }}
    #DialogTitle {{ color: {p['text']}; font-size: 14px; font-weight: 600; }}
    #DialogPreview {{ color: {p['text_muted']}; font-size: 12px; }}
    #DialogTime {{ color: {p['text_muted']}; font-size: 11px; }}
    #UnreadBadge {{
        background-color: {p['accent']};
        color: white;
        font-size: 11px;
        font-weight: 600;
        border-radius: 9px;
        padding: 1px 6px;
    }}
    #InputBar {{
        background-color: {p['header_bg']};
        border-top: 1px solid {p['divider']};
    }}
    #MessageInput {{
        background-color: {p['input_bg']};
        border: none;
        border-radius: 18px;
        padding: 9px 14px;
        color: {p['text']};
        font-size: 13px;
    }}
    #SendButton {{
        background-color: {p['accent']};
        color: white;
        border: none;
        border-radius: 18px;
        min-width: 64px;
        padding: 9px 18px;
        font-weight: 600;
    }}
    #SendButton:hover {{ background-color: #4aa3f0; }}
    QToolBar {{
        background-color: {p['header_bg']};
        border: none;
        spacing: 6px;
        padding: 4px 8px;
    }}
    QToolButton {{ color: {p['text']}; padding: 4px 12px; border-radius: 6px; }}
    QToolButton:checked {{ background-color: {p['accent']}; color: white; }}
    QMenuBar {{ background-color: {p['sidebar_bg']}; color: {p['text']}; }}
    QMenuBar::item:selected {{ background-color: {p['sidebar_item_selected']}; }}
    QMenu {{
        background-color: {p['sidebar_bg']};
        color: {p['text']};
        border: 1px solid {p['divider']};
    }}
    QMenu::item:selected {{ background-color: {p['sidebar_item_selected']}; }}
    QStatusBar {{ background-color: {p['header_bg']}; color: {p['text_muted']}; }}
    QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
    QScrollBar::handle:vertical {{
        background: {p['scrollbar']};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
    """
