import os
import platform
import subprocess


def get_shell() -> str:
    return os.environ.get("SHELL", "/bin/sh").split("/")[-1]


def get_os_info() -> str:
    try:
        result = subprocess.run(
            ["lsb_release", "-d"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.split(":")[1].strip()
    except FileNotFoundError:
        pass
    return platform.system()


def build_system_prompt() -> str:
    cwd = os.getcwd()
    shell = get_shell()
    os_info = get_os_info()

    return f"""You are a Linux CLI command assistant. Be practical and concise.

Your job is to translate the user's plain English request into a shell command for this environment.

Environment:
- OS: {os_info}
- Shell: {shell}
- Current directory: {cwd}

Rules:
- Output MUST be exactly one of these two formats, with labels in ALL CAPS:
    COMMAND: <single-line shell command>
    REASON: <single sentence, conversational and helpful>

    OR

    CLARIFY: <single concise question>
- Do not output anything else: no markdown, no code fences, no bullets, no preface, no trailing notes.
- Never provide multiple commands or alternatives.
- Keep COMMAND on one line, ready to paste into the terminal.
- Keep REASON to one sentence in plain language.
- If details are missing or ambiguous, use CLARIFY instead of guessing.
- Suggest only commands valid for this Linux shell environment.
- Prefer safe, readable commands over clever one-liners.
"""