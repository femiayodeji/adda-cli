import requests
import json
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


def get_groq_api_key() -> str | None:
    env_key = os.environ.get("GROQ_API_KEY")
    if env_key:
        return env_key

    # Fallback to persisted CLI config when environment variable is not set.
    try:
        from adda.config import load_config

        return load_config().groq_api_key
    except Exception:
        return None


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


def check_groq_api_key() -> bool:
    return bool(get_groq_api_key())


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


def _parse_response(text: str) -> OllamaResponse:
    """
    Expected formats:
        COMMAND: <command>
        REASON: <reason>

        or

        CLARIFY: <question>

        or

        REASON: <message>
    """
    lines = text.strip().splitlines()
    result = {"command": None, "reason": None, "clarification": None}

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
    on_token: Callable[[str], None] | None = None,
) -> OllamaResponse:
    normalized_provider = provider.strip().lower()
    if normalized_provider == "qroq":
        normalized_provider = "groq"

    if normalized_provider == "groq":
        return _chat_groq(
            model=model,
            system_prompt=system_prompt,
            history=history,
            user_message=user_message,
            api_key=api_key,
            stream=stream,
            on_token=on_token,
        )

    return _chat_ollama(
        model=model,
        system_prompt=system_prompt,
        history=history,
        user_message=user_message,
        stream=stream,
        on_token=on_token,
    )


def _chat_ollama(
    model: str,
    system_prompt: str,
    history: list[dict],
    user_message: str,
    stream: bool = False,
    on_token: Callable[[str], None] | None = None,
) -> OllamaResponse:
    messages = (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": user_message}]
    )

    try:
        response = requests.post(
            OLLAMA_CHAT_ENDPOINT,
            json={
                "model": model,
                "messages": messages,
                "stream": stream,
            },
            stream=stream,
            timeout=60,
        )
        response.raise_for_status()

        if stream:
            chunks: list[str] = []
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                if token:
                    chunks.append(token)
                    if on_token:
                        on_token(token)
            content = "".join(chunks)
        else:
            content = response.json()["message"]["content"]

        return _parse_response(content)

    except requests.ConnectionError:
        return OllamaResponse(
            kind="error",
            raw="Cannot connect to Ollama. Is it running? Try: ollama serve"
        )
    except requests.Timeout:
        return OllamaResponse(
            kind="error",
            raw="Ollama took too long to respond. The model may still be loading."
        )
    except requests.HTTPError as e:
        return OllamaResponse(
            kind="error",
            raw=f"Ollama returned an error: {e.response.status_code} {e.response.text}"
        )
    except (KeyError, ValueError) as e:
        return OllamaResponse(
            kind="error",
            raw=f"Unexpected response format from Ollama: {e}"
        )


def _chat_groq(
    model: str,
    system_prompt: str,
    history: list[dict],
    user_message: str,
    api_key: str | None = None,
    stream: bool = False,
    on_token: Callable[[str], None] | None = None,
) -> OllamaResponse:
    key = api_key or get_groq_api_key()
    if not key:
        return OllamaResponse(
            kind="error",
            raw="Missing GROQ_API_KEY. Export it first: export GROQ_API_KEY=...",
        )

    messages = (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": user_message}]
    )

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            GROQ_CHAT_ENDPOINT,
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                "stream": stream,
            },
            stream=stream,
            timeout=60,
        )
        response.raise_for_status()

        if stream:
            chunks: list[str] = []
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                if line == "data: [DONE]":
                    break
                if not line.startswith("data: "):
                    continue

                data = json.loads(line[len("data: "):])
                token = (
                    data.get("choices", [{}])[0]
                    .get("delta", {})
                    .get("content", "")
                )
                if token:
                    chunks.append(token)
                    if on_token:
                        on_token(token)
            content = "".join(chunks)
        else:
            content = response.json()["choices"][0]["message"]["content"]

        return _parse_response(content)

    except requests.Timeout:
        return OllamaResponse(
            kind="error",
            raw="Groq took too long to respond. Please try again.",
        )
    except requests.HTTPError as e:
        return OllamaResponse(
            kind="error",
            raw=f"Groq returned an error: {e.response.status_code} {e.response.text}",
        )
    except (requests.RequestException, KeyError, ValueError) as e:
        return OllamaResponse(
            kind="error",
            raw=f"Unexpected response format from Groq: {e}",
        )