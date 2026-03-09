import requests
import json
from dataclasses import dataclass
from typing import Callable

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"


@dataclass
class OllamaResponse:
    kind: str        # "command" | "clarify" | "error"
    command: str | None = None
    reason: str | None = None
    clarification: str | None = None
    raw: str | None = None


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


def _parse_response(text: str) -> OllamaResponse:
    """
    Expected formats:
        COMMAND: <command>
        REASON: <reason>

        or

        CLARIFY: <question>
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

    return OllamaResponse(kind="error", raw=text)


def chat(
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