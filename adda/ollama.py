import requests
import os
from dataclasses import dataclass
from typing import Callable

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_CHAT_ENDPOINT = f"{GROQ_BASE_URL}/chat/completions"
GROQ_MODELS_ENDPOINT = f"{GROQ_BASE_URL}/models"

@dataclass
class OllamaResponse:
    kind: str        # "command" | "clarify" | "humane" | "error"
    command: str | None = None
    reason: str | None = None
    clarification: str | None = None
    raw: str | None = None

def _handle_error(message: str) -> OllamaResponse:
    return OllamaResponse(
        kind="error",
        raw=message,
    )

def get_groq_api_key() -> str | None:
    env_key = os.environ.get("GROQ_API_KEY")
    if env_key:
        return env_key
    return None

def prepare_messages(system_prompt: str, history: list[dict], user_message: str) -> list[dict]:
    return (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": user_message}]
    )

def _parse_response(text: str) -> OllamaResponse:
    lines = text.strip().splitlines()
    result: dict[str, str | None] = {"command": None, "reason": None, "clarification": None}
    for line in lines:
        if line.startswith("COMMAND:"):
            result["command"] = line[len("COMMAND:"):].strip()
        elif line.startswith("REASON:"):
            result["reason"] = line[len("REASON:"):].strip()
        elif line.startswith("CLARIFY:"):
            result["clarification"] = line[len("CLARIFY:"):].strip()
    if result["clarification"]:
        return OllamaResponse(kind="clarify", clarification=result["clarification"], raw=text)
    if result["command"]:
        return OllamaResponse(kind="command", command=result["command"], reason=result["reason"], raw=text)
    
    # A REASON without a COMMAND means the model responded conversationally
    if result["reason"]:
        return OllamaResponse(kind="humane", reason=result["reason"], raw=text)
    return OllamaResponse(kind="error", raw=text)

def chat(
    model: str,
    system_prompt: str,
    history: list[dict],
    user_message: str,
    provider: str = "ollama",
    api_key: str | None = None,
    stream: bool = False,
) -> OllamaResponse:
    normalized_provider = provider.strip().lower()
    messages = prepare_messages(system_prompt, history, user_message)

    if normalized_provider == "groq":
        key = api_key or get_groq_api_key()
        if not key:
            return OllamaResponse(
                kind="error",
                raw="Missing GROQ_API_KEY. Export it first: export GROQ_API_KEY=...",
            )
        endpoint = GROQ_CHAT_ENDPOINT
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        json_payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        parse_content = lambda resp: resp.json()["choices"][0]["message"]["content"]
    else:
        endpoint = OLLAMA_CHAT_ENDPOINT
        headers = None
        json_payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        parse_content = lambda resp: resp.json()["message"]["content"]

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=json_payload,
            stream=stream,
            timeout=60,
        )
        response.raise_for_status()

        content = parse_content(response)

        return _parse_response(content)

    except requests.ConnectionError:
        if normalized_provider == "ollama":
            return _handle_error("Cannot connect to Ollama. Is it running? Try: ollama serve")
        else:
            return _handle_error("Cannot connect to Groq. Check your network or API key.")
    except requests.Timeout:
        if normalized_provider == "ollama":
            return _handle_error("Ollama took too long to respond. The model may still be loading.")
        else:
            return _handle_error("Groq took too long to respond. Please try again.")
    except requests.HTTPError as e:
        return _handle_error(f"{provider.capitalize()} returned an error: {e.response.status_code} {e.response.text}")
    except (requests.RequestException, KeyError, ValueError) as e:
        return _handle_error(f"Unexpected response format from {provider.capitalize()}: {e}")

def check_ollama_running() -> bool:
    try:
        requests.get(OLLAMA_BASE_URL, timeout=3)
        return True
    except requests.ConnectionError:
        return False

def check_model_available(model: str) -> bool:
    try:
        response = requests.get(OLLAMA_TAGS_ENDPOINT, timeout=5)
        models = [m["name"] for m in response.json().get("models", [])]
        return any(model in m for m in models)
    except (requests.RequestException, KeyError):
        return False

def check_groq_model_available(model: str, api_key: str | None = None) -> bool:
    key = api_key or get_groq_api_key()
    if not key:
        return False
    try:
        response = requests.get(
            GROQ_MODELS_ENDPOINT,
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        response.raise_for_status()
        models = [m.get("id", "") for m in response.json().get("data", [])]
        return model in models
    except (requests.RequestException, KeyError):
        return False
