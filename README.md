# UkrGram

A custom Telegram client built on **Telethon** (MTProto) with a **PyQt6** GUI and
a hybrid manual/automation design.

## Architecture

Layered, with strict separation of concerns. Dependencies point inward only
(UI → services → core); the GUI never touches Telethon directly.

| Layer | Responsibility |
|-------|----------------|
| `config` | Environment-backed settings (`.env` → pydantic-settings) |
| `core` | Client lifecycle, authentication, resilience (FloodWait/retry) |
| `services` | High-level operations (dialogs, messages) |
| `automation` | Userbot event engine + plugins (auto-reply, keyword notifier) |
| `gui` | PyQt6 windows/widgets bridged to asyncio via `qasync` |
| `models` | Immutable domain DTOs |
| `utils` | Cross-cutting helpers (logging) |

> **Key design note:** Telethon runs on `asyncio` while PyQt6 has its own Qt
> event loop. The two are bridged with **`qasync`** so Telegram coroutines run in
> the same loop as the GUI without separate threads.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the environment template and fill in your credentials from
   <https://my.telegram.org/apps>:
   ```bash
   cp .env.example .env
   ```

## Run

```bash
python main.py
```

Launches the PyQt6 desktop window. On first run you are prompted — via modal
dialogs — for your phone number, the login code and, if enabled, your 2FA
password; the session is then cached under `SESSION_DIR` for subsequent runs.
The window is a Telegram-style dark UI: a chat list with avatars, last-message
previews and unread badges on the left, and the selected conversation rendered
as message bubbles on the right, with a rounded input box to send messages.

## Automation

UkrGram runs in hybrid mode: alongside manual use, a plugin-based engine can
react to incoming events. Toggle it from the **Automation** menu in the window.

Built-in plugins:

- **auto_reply** — replies once to each new incoming private chat, using
  `AUTO_REPLY_TEXT`.
- **keyword_notifier** — logs incoming messages containing any of
  `NOTIFY_KEYWORDS` (comma-separated; contributes no handlers when empty).

Add your own by subclassing `AutomationPlugin` and registering it with the
`AutomationEngine` — no engine changes required (Open/Closed Principle).
