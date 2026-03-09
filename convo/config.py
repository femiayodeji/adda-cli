import json
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG_DIR = Path.home() / ".config" / "convo"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_MODEL = "llama3.1"
DEFAULT_STREAM = True


@dataclass
class Config:
    model: str = DEFAULT_MODEL
    stream: bool = DEFAULT_STREAM


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    if not CONFIG_FILE.exists():
        return Config()
    try:
        data = json.loads(CONFIG_FILE.read_text())
        return Config(
            model=data.get("model", DEFAULT_MODEL),
            stream=data.get("stream", DEFAULT_STREAM),
        )
    except (json.JSONDecodeError, KeyError):
        return Config()


def save_config(config: Config) -> None:
    _ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(asdict(config), indent=2))


def set_model(model: str) -> Config:
    config = load_config()
    config.model = model
    save_config(config)
    return config

def set_stream(stream: bool) -> Config:
    config = load_config()
    config.stream = stream
    save_config(config)
    return config

def show_config() -> str:
    config = load_config()
    return (
        f"Config file : {CONFIG_FILE}\n"
        f"Model       : {config.model}\n"
        f"Stream      : {config.stream}\n"
    )