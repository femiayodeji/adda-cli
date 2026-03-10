# adda

**adda** is a simple CLI conversational assistant that translates plain English instructions into Linux shell commands, powered by a local LLM.

## Features

- Converts natural language requests into practical shell commands.
- Supports interactive conversations and command clarification.
- Works locally with Ollama or remotely with Groq.
- Keeps conversation history and can start fresh sessions.

## Usage

```sh
adda ask "List all files modified in the last 24 hours"
```

- Use plain English to describe what you want to do.
- The assistant will respond with the appropriate shell command.
- You can start a new conversation with `--new`.

## Requirements

- Python 3.8+
- Ollama running locally (or Groq API key for remote)

## Installation

Clone the repo and install dependencies:

```sh
git clone <repo-url>
cd adda
pip install -r requirements.txt
```

Or install with pip using the included pyproject.toml:

```sh
pip install .
```

This will install the `adda` CLI command.

## Configuration


### Default Configuration

- By default, adda uses Ollama as the provider and the `llama3.1` model.
- The configuration file is stored at `~/.config/adda/config.json`.

### Changing Provider or Model

You can change the provider (e.g., to `groq`) or the model by editing the config file or using the CLI (if supported):

- **Provider:** `ollama` (default) or `groq`
- **Model:** e.g., `llama3.1` (default)

### Setting Groq API Key

If you want to use Groq as the provider, set your API key as an environment variable:

```sh
export GROQ_API_KEY=your-groq-api-key
```

Or add it to the config file at `~/.config/adda/config.json` under `groq_api_key`.

### Example config.json

```json
{
	"provider": "ollama",
	"model": "llama3.1",
	"stream": true,
	"groq_api_key": null
}
```

You can also customize whether responses are streamed (`stream: true`) or returned all at once.

---

---

Let me know if you want to add usage examples, contribution guidelines, or more details!
