import json
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG_DIR = Path.home() / ".config" / "adda"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_MODEL = "llama3.1"
DEFAULT_STREAM = True
DEFAULT_PROVIDER = "ollama"


@dataclass
class Config:
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    stream: bool = DEFAULT_STREAM
    groq_api_key: str | None = None


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    if not CONFIG_FILE.exists():
        return Config()
    data = json.loads(CONFIG_FILE.read_text())
    return Config(
        provider=data.get("provider", DEFAULT_PROVIDER),
        model=data.get("model", DEFAULT_MODEL),
        stream=data.get("stream", DEFAULT_STREAM),
        groq_api_key=data.get("groq_api_key"),
    )


def save_config(config: Config) -> None:
    _ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(asdict(config), indent=2))


def set_model(model: str) -> Config:
    config = load_config()
    config.model = model
    save_config(config)
    return config


def set_provider(provider: str) -> Config:
    config = load_config()
    normalized = provider.strip().lower()
    config.provider = normalized
    save_config(config)
    return config

def set_stream(stream: bool) -> Config:
    config = load_config()
    config.stream = stream
    save_config(config)
    return config


def set_groq_api_key(api_key: str | None) -> Config:
    config = load_config()
    config.groq_api_key = api_key
    save_config(config)
    return config

def show_config() -> str:
    config = load_config()
    groq_api_key_status = "set" if config.groq_api_key else "not set"
    return (
        f"Config file : {CONFIG_FILE}\n"
        f"Provider    : {config.provider}\n"
        f"Model       : {config.model}\n"
        f"Stream      : {config.stream}\n"
        f"Groq API key: {groq_api_key_status}\n"
    )