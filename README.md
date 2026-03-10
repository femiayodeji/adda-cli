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


Clone the repo and install with pip (using pyproject.toml):

```sh
git clone <repo-url>
cd adda
pip install .
```

Or, for development and running tests, install [Hatch](https://hatch.pypa.io/latest/):

```sh
pip install --upgrade hatch
# Or with your package manager: python -m pip install --user hatch
```

Then, create a virtual environment and install dependencies:

```sh
hatch env create
hatch shell
# Now you're in the environment, install the project in editable mode:
hatch install
```

You can now run the `adda` CLI command.

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

### Example: Configure for Ollama (Llama Model)

You can configure adda to use Ollama and a llama model with streaming enabled:

```sh
adda config --provider ollama --model llama3.1 --stream true
```

### Example: Configure for Groq

You can configure adda to use Groq and a specific model with streaming enabled and your API key:

```sh
adda config --provider groq --model llama-3.3-70b-versatile --stream true --api-key GROQ_API_KEY
```

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
