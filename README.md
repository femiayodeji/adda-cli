# adda

**adda** is a CLI assistant that translates plain English into Linux shell commands, powered by a local or remote LLM. Describe what you want to do — adda suggests the right command and runs it on your confirmation.

---

## Demo

```sh
$ adda "show me files larger than 100MB"

  ╭─ Suggested Command ────────────────────────────────────╮
  │                                                        │
  │   find . -type f -size +100M                          │
  │                                                        │
  │   Finds all files larger than 100MB in the current    │
  │   directory.                                          │
  │                                                        │
  ╰────────────────────────────────────────────────────────╯

  Run this command? [y/N]: y

  ╭─ Output ───────────────────────────────────────────────╮
  │  ./videos/recording.mp4   2.1G                        │
  │  ./backup/archive.tar.gz  430M                        │
  ╰────────────────────────────────────────────────────────╯
```

---

## Features

- Plain English to shell command translation
- Runs the suggested command on your confirmation
- Conversation history — follow-up requests remember context
- Supports **Ollama** (local) and **Groq** (cloud) as providers
- Asks for clarification when your request is ambiguous
- `--yes` flag to skip confirmation for power users

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally, **or** a Groq API key

---

## Installation

Clone the repo and install:

```sh
git clone https://github.com/femiayodeji/adda-cli.git
cd adda
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verify everything is working:

```sh
adda status
```

---

## Usage

```sh
# Ask anything in plain English
adda "list all files modified in the last 24 hours"

# Explicit subcommand (same result)
adda cmd "list all files modified in the last 24 hours"

# Skip confirmation and run immediately
adda "show disk usage" --yes

# Start a fresh conversation
adda "show running processes" --new
```

### Conversation

adda remembers context across requests in the same session:

```sh
$ adda "show me log files"
# suggests: find . -name "*.log"

$ adda "now only ones modified today"
# suggests: find . -name "*.log" -mtime 0
```

Clear the session at any time:

```sh
adda clear
```

---

## Configuration

Config is stored at `~/.config/adda/config.json`.

### Commands

```sh
# Set provider
adda config --provider ollama
adda config --provider groq

# Set model
adda config --model llama3.1
adda config --model llama-3.3-70b-versatile

# Enable or disable streaming
adda config --stream true
adda config --stream false

# Show current config
adda config --show
```

### Providers

#### Ollama (default)

Install Ollama from [ollama.com](https://ollama.com), then pull a model:

```sh
ollama pull llama3.1
ollama serve
```

#### Groq

1. Sign up at [console.groq.com](https://console.groq.com)
2. Go to **API Keys** and create a new key
3. Set it as an environment variable (never stored on disk):

```sh
export GROQ_API_KEY=your_groq_api_key
```

To persist it across terminal sessions, add it to your shell config:

```sh
# ~/.bashrc or ~/.zshrc
export GROQ_API_KEY=your_groq_api_key
```

Then reload:

```sh
source ~/.bashrc
```

4. Configure adda to use Groq:

```sh
adda config --provider groq --model llama-3.3-70b-versatile
```

5. Verify:

```sh
adda status
```

Available Groq models can be found at [console.groq.com/docs/models](https://console.groq.com/docs/models).

### Example config.json

```json
{
  "provider": "ollama",
  "model": "llama3.1",
  "stream": false
}
```

---

## Commands Reference

| Command | Description |
|---|---|
| `adda "<query>"` | Suggest and optionally run a command |
| `adda cmd "<query>"` | Same as above, explicit subcommand |
| `adda config --show` | Show current configuration |
| `adda config --provider <name>` | Set provider (ollama or groq) |
| `adda config --model <name>` | Set model |
| `adda config --stream <true/false>` | Toggle streaming |
| `adda status` | Check provider and model availability |
| `adda clear` | Clear conversation history |

### Options for `adda` / `adda cmd`

| Option | Description |
|---|---|
| `--yes`, `-y` | Run command without confirmation |
| `--new`, `-n` | Start a fresh conversation |

---

## License

MIT