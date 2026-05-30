"""Main application window (pure view, free of business logic)."""

from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ukrgram.gui.widgets import ChatView, DialogListItem, make_avatar
from ukrgram.models.domain import DialogInfo, MessageInfo

_DIALOG_ID_ROLE = Qt.ItemDataRole.UserRole


class MainWindow(QMainWindow):
    """Telegram-like two-pane window: dialog list and conversation.

    The window is a passive view. It exposes widgets and helper methods for a
    controller to populate; it holds no networking or business logic.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("UkrGram")
        self.resize(1040, 680)

        self.dialog_list = QListWidget()
        self.chat_avatar = QLabel()
        self.chat_title = QLabel("Select a chat")
        self.chat_subtitle = QLabel("")
        self.chat_view = ChatView()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.toggle_automation_action = QAction("Enable automation", self)
        self.toggle_automation_action.setCheckable(True)

        self._build_menu()
        self._build_toolbar()
        self._build_layout()

    def _build_menu(self) -> None:
        """Create the application menu bar with the automation toggle."""
        automation_menu = self.menuBar().addMenu("Automation")
        automation_menu.addAction(self.toggle_automation_action)

    def _build_toolbar(self) -> None:
        """Create an always-visible toolbar exposing the automation toggle.

        On macOS the menu bar is rendered at the top of the screen rather than
        inside the window, so a toolbar button keeps the toggle discoverable.
        Menu and toolbar share the same action and stay in sync.
        """
        toolbar = QToolBar("Main", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        toolbar.addAction(self.toggle_automation_action)
        self.addToolBar(toolbar)

    def _build_layout(self) -> None:
        """Assemble the widget tree and install it as the central widget."""
        self.dialog_list.setObjectName("Sidebar")
        self.dialog_list.setFixedWidth(320)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.dialog_list)
        splitter.addWidget(self._build_conversation_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([320, 720])
        splitter.setHandleWidth(1)

        self.setCentralWidget(splitter)
        self.set_status("Starting…")

    def _build_conversation_panel(self) -> QWidget:
        """Build the right-hand panel: header, message view and input bar.

        Returns:
            The assembled conversation panel widget.
        """
        header = QWidget()
        header.setObjectName("ChatHeader")
        header.setFixedHeight(62)
        self.chat_avatar.setFixedSize(42, 42)
        self.chat_title.setObjectName("ChatTitle")
        self.chat_subtitle.setObjectName("ChatSubtitle")

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(0)
        title_column.addStretch(1)
        title_column.addWidget(self.chat_title)
        title_column.addWidget(self.chat_subtitle)
        title_column.addStretch(1)

        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(14, 0, 14, 0)
        header_row.setSpacing(12)
        header_row.addWidget(self.chat_avatar)
        header_row.addLayout(title_column)
        header_row.addStretch(1)

        input_bar = QWidget()
        input_bar.setObjectName("InputBar")
        input_bar.setFixedHeight(60)
        self.message_input.setObjectName("MessageInput")
        self.message_input.setPlaceholderText("Write a message…")
        self.send_button.setObjectName("SendButton")

        input_row = QHBoxLayout(input_bar)
        input_row.setContentsMargins(12, 10, 12, 10)
        input_row.setSpacing(8)
        input_row.addWidget(self.message_input)
        input_row.addWidget(self.send_button)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(self.chat_view, 1)
        layout.addWidget(input_bar)
        return panel

    def set_status(self, text: str) -> None:
        """Show a message in the status bar.

        Args:
            text: Status text to display.
        """
        self.statusBar().showMessage(text)

    def set_dialogs(self, dialogs: list[DialogInfo]) -> None:
        """Replace the dialog list with the supplied dialogs.

        Args:
            dialogs: Dialog DTOs to render.
        """
        self.dialog_list.clear()
        for dialog in dialogs:
            item = QListWidgetItem(self.dialog_list)
            item.setData(_DIALOG_ID_ROLE, dialog.id)
            item.setSizeHint(QSize(0, 64))
            self.dialog_list.addItem(item)
            self.dialog_list.setItemWidget(item, DialogListItem(dialog))

    def set_conversation(self, title: str, messages: list[MessageInfo]) -> None:
        """Render a full conversation for the selected dialog.

        Args:
            title: Dialog title to show in the header.
            messages: Messages ordered oldest-first.
        """
        dialog_id = self.selected_dialog_id()
        key = dialog_id if dialog_id is not None else title
        self.chat_avatar.setPixmap(make_avatar(title, key, 42))
        self.chat_title.setText(title)
        self.chat_subtitle.setText(f"{len(messages)} messages")
        self.chat_view.set_messages(messages)

    def append_message(self, message: MessageInfo) -> None:
        """Append a single message to the current conversation view.

        Args:
            message: The message DTO to append.
        """
        self.chat_view.add_message(message)

    def selected_dialog_id(self) -> int | None:
        """Return the entity id of the currently selected dialog.

        Returns:
            The selected dialog id, or ``None`` when nothing is selected.
        """
        item = self.dialog_list.currentItem()
        if item is None:
            return None
        dialog_id = item.data(_DIALOG_ID_ROLE)
        return int(dialog_id) if dialog_id is not None else None

    def take_input_text(self) -> str:
        """Read and clear the message input field.

        Returns:
            The stripped text that was present in the input field.
        """
        text = self.message_input.text().strip()
        self.message_input.clear()
        return text
