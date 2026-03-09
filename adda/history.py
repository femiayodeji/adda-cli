import json
from pathlib import Path
from datetime import datetime

# ~/.config/adda/session.json
CONFIG_DIR = Path.home() / ".config" / "adda"
SESSION_FILE = CONFIG_DIR / "session.json"

# Limit how many past exchanges are sent to the model.
# Each exchange = 1 user message + 1 assistant message = 2 entries.
MAX_HISTORY_EXCHANGES = 10


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_history() -> list[dict]:
    """Load conversation history from disk. Returns empty list if none exists."""
    if not SESSION_FILE.exists():
        return []
    try:
        data = json.loads(SESSION_FILE.read_text())
        return data.get("messages", [])
    except (json.JSONDecodeError, KeyError):
        return []


def save_history(messages: list[dict]) -> None:
    """Persist conversation history to disk."""
    _ensure_config_dir()
    SESSION_FILE.write_text(json.dumps({
        "updated_at": datetime.now().isoformat(),
        "messages": messages,
    }, indent=2))


def append_exchange(history: list[dict], user_input: str, assistant_response: str) -> list[dict]:
    """Add a user/assistant exchange to history and trim if needed."""
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": assistant_response})

    # Keep only the last N exchanges to avoid overflowing the context window
    max_messages = MAX_HISTORY_EXCHANGES * 2
    if len(history) > max_messages:
        history = history[-max_messages:]

    return history


def clear_history() -> None:
    """Delete the session file to start a fresh conversation."""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def history_summary() -> str:
    """Human-readable summary of current session state."""
    messages = load_history()
    if not messages:
        return "No active session."
    exchanges = len(messages) // 2
    return f"{exchanges} exchange(s) in current session. ({SESSION_FILE})"