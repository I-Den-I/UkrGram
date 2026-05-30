"""Main application window (pure view, free of business logic)."""

from __future__ import annotations

from PyQt6.QtCore import Qt
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ukrgram.models.domain import DialogInfo, MessageInfo

_DIALOG_ID_ROLE = Qt.ItemDataRole.UserRole


class MainWindow(QMainWindow):
    """Two-pane chat window: dialog list on the left, conversation on the right.

    The window is a passive view. It exposes widgets and helper methods for a
    controller to populate; it contains no networking or business logic.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("UkrGram")
        self.resize(960, 640)
        self.dialog_list = QListWidget()
        self.chat_title = QLabel("Select a chat")
        self.message_view = QTextEdit()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.toggle_automation_action = QAction("Enable automation", self)
        self.toggle_automation_action.setCheckable(True)
        self._build_menu()
        self._build_layout()

    def _build_menu(self) -> None:
        """Create the application menu bar with the automation toggle."""
        automation_menu = self.menuBar().addMenu("Automation")
        automation_menu.addAction(self.toggle_automation_action)

    def _build_layout(self) -> None:
        """Assemble the widget tree and install it as the central widget."""
        self.message_view.setReadOnly(True)
        self.message_input.setPlaceholderText("Type a message…")

        conversation = QWidget()
        conversation_layout = QVBoxLayout(conversation)
        conversation_layout.addWidget(self.chat_title)
        conversation_layout.addWidget(self.message_view)

        input_row = QHBoxLayout()
        input_row.addWidget(self.message_input)
        input_row.addWidget(self.send_button)
        conversation_layout.addLayout(input_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.dialog_list)
        splitter.addWidget(conversation)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 680])

        self.setCentralWidget(splitter)
        self.set_status("Starting…")

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
            item = QListWidgetItem(self._format_dialog(dialog))
            item.setData(_DIALOG_ID_ROLE, dialog.id)
            self.dialog_list.addItem(item)

    def set_conversation(self, title: str, messages: list[MessageInfo]) -> None:
        """Render a full conversation for the selected dialog.

        Args:
            title: Dialog title to show above the messages.
            messages: Messages ordered oldest-first.
        """
        self.chat_title.setText(title)
        self.message_view.clear()
        for message in messages:
            self.message_view.append(self._format_message(message))

    def append_message(self, message: MessageInfo) -> None:
        """Append a single message to the current conversation view.

        Args:
            message: The message DTO to append.
        """
        self.message_view.append(self._format_message(message))

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

    @staticmethod
    def _format_dialog(dialog: DialogInfo) -> str:
        """Build the display string for a dialog list row.

        Args:
            dialog: The dialog DTO.

        Returns:
            A single-line label, including an unread badge when applicable.
        """
        badge = f"  ({dialog.unread_count})" if dialog.unread_count else ""
        return f"{dialog.kind} {dialog.title}{badge}"

    @staticmethod
    def _format_message(message: MessageInfo) -> str:
        """Build the display string for a single message.

        Args:
            message: The message DTO.

        Returns:
            A formatted ``[HH:MM] sender: text`` line.
        """
        timestamp = message.date.strftime("%H:%M")
        return f"[{timestamp}] {message.sender_name}: {message.text}"
