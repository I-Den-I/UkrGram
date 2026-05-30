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
| `services` | High-level operations (dialogs, messages, contacts) — *next* |
| `automation` | Userbot event engine + plugins — *next* |
| `gui` | PyQt6 windows/widgets bridged to asyncio via `qasync` — *next* |
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

## Run (bootstrap auth check)

```bash
python main.py
```

This validates configuration and performs an interactive Telegram login,
printing the authenticated account. The PyQt6 GUI is layered on top of the same
core client in a later iteration.
