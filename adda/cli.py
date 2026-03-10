import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from rich import print as rprint
import subprocess

from adda.config import (
    load_config,
    set_model,
    set_provider,
    show_config,
    set_stream,
)
from adda.history import history_summary, load_history, save_history, append_exchange, clear_history
from adda.ollama import (
    chat,
    check_groq_model_available,
    check_model_available,
    check_ollama_running,
    get_groq_api_key,
)
from adda.prompt import build_system_prompt

app = typer.Typer(
    help="adda — plain English to Linux commands, powered by a local LLM.",
    add_completion=False,
)
console = Console()


def _preflight_checks(provider: str, model: str) -> bool:
    normalized = provider.strip().lower()

    if normalized == "groq":
        api_key = get_groq_api_key()
        if not api_key:
            console.print(
                "[bold red]✗ GROQ_API_KEY is not set.[/bold red]\n"
                "  Export it with: [cyan]export GROQ_API_KEY=your_key[/cyan]"
            )
            return False

        if not check_groq_model_available(model, api_key=api_key):
            console.print(
                f"[bold red]✗ Model '[cyan]{model}[/cyan]' not found on Groq.[/bold red]\n"
                "  Check available models: [cyan]https://console.groq.com/docs/models[/cyan]"
            )
            return False

        return True

    if normalized != "ollama":
        console.print(
            f"[bold red]✗ Unsupported provider '[cyan]{provider}[/cyan]'.[/bold red]\n"
            "  Supported providers: [cyan]ollama[/cyan], [cyan]groq[/cyan]"
        )
        return False

    if not check_ollama_running():
        console.print(
            "[bold red]✗ Ollama is not running.[/bold red]\n"
            "  Start it with: [cyan]ollama serve[/cyan]"
        )
        return False

    if not check_model_available(model):
        console.print(
            f"[bold red]✗ Model '[cyan]{model}[/cyan]' not found.[/bold red]\n"
            f"  Pull it with: [cyan]ollama pull {model}[/cyan]"
        )
        return False

    return True


def _display_command(command: str, reason: str | None) -> None:
    content = Text()
    content.append(f"  {command}", style="bold green")
    if reason:
        content.append(f"\n\n  {reason}", style="dim")

    console.print(
        Panel(
            content,
            title="[bold]Suggested Command[/bold]",
            border_style="green",
            padding=(1, 2),
        )
    )

def _run_command(command: str) -> None:
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
        )
        output = result.stdout or result.stderr

        console.print(
            Panel(
                Text(output.strip()),
                title="[bold]Output[/bold]",
                border_style="blue",
                padding=(1, 2),
            )
        )

        if result.returncode != 0:
            console.print(f"[dim red]  Exit code: {result.returncode}[/dim red]")

    except Exception as e:
        _display_error(f"Failed to run command: {e}")

def _display_clarification(question: str | None) -> None:
    console.print(
        Panel(
            Text(f"  {question}", style="yellow"),
            title="[bold]Clarification needed[/bold]",
            border_style="yellow",
            padding=(1, 2),
        )
    )


def _display_error(message: str) -> None:
    console.print(
        Panel(
            Text(f"  {message}", style="red"),
            title="[bold]Error[/bold]",
            border_style="red",
            padding=(1, 2),
        )
    )


def _display_humane(message: str) -> None:
    console.print(
        Panel(
            Text(f"  {message}", style="cyan"),
            title="[bold]Humane[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


@app.command()
def ask(
    query: str = typer.Argument(..., help="What you want to do in plain English."),
    new: bool = typer.Option(False, "--new", "-n", help="Start a fresh conversation."),
    stream: bool | None = typer.Option(None, "--stream/--no-stream", help="Stream model output as it is generated."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Run command without confirmation."),
):
    config = load_config()
    use_stream = config.stream if stream is None else stream

    if not _preflight_checks(config.provider, config.model):
        raise typer.Exit(1)

    if new:
        clear_history()
        console.print("[dim]Starting a new conversation.[/dim]\n")

    history = load_history()
    system_prompt = build_system_prompt()

    if use_stream:
        console.print("[dim]Streaming response...[/dim]")
        streamed_tokens = []
        def on_token(token):
            streamed_tokens.append(token)
            console.print(token, end="", highlight=False, soft_wrap=True)
        response = chat(
            model=config.model,
            system_prompt=system_prompt,
            history=history,
            user_message=query,
            provider=config.provider,
            api_key=get_groq_api_key(),
            stream=True,
            on_token=on_token,
        )
        console.print()

        if response.kind == "command":
            if response.reason:
                _display_command("", response.reason)
                if yes or Confirm.ask("  Run this command?", default=False):
                    _run_command(response.command)
        elif response.kind == "clarify":
            _display_clarification(response.clarification or "")
        elif response.kind == "humane":
            _display_humane(response.reason or response.raw or "Done.")
        elif response.kind != "command":
            _display_error(response.raw or "Unknown error.")
    else:
        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            response = chat(
                model=config.model,
                system_prompt=system_prompt,
                history=history,
                user_message=query,
                provider=config.provider,
                api_key=get_groq_api_key(),
            )
        if response.kind == "command":
            _display_command(response.command or "", response.reason or "")
            if yes or Confirm.ask("  Run this command?", default=False):
                _run_command(response.command)

        elif response.kind == "clarify":
            _display_clarification(response.clarification or "")
        elif response.kind == "humane":
            _display_humane(response.reason or response.raw or "Done.")
        else:
            _display_error(response.raw or "Unknown error.")

    updated_history = append_exchange(history, query, response.raw or "")
    save_history(updated_history)


@app.command()
def config(
    model: str | None = typer.Option(None, "--model", help="Set the model to use for the selected provider."),
    llm: str | None = typer.Option(None, "--llm", help="Deprecated alias for --model."),
    provider: str | None = typer.Option(None, "--provider", help="Set provider: ollama or groq."),
    show: bool = typer.Option(False, "--show", help="Show current config."),
    stream: str | None = typer.Option(None, "--stream", help="Set whether to stream model output (true/false)."),
    no_stream: bool = typer.Option(False, "--no-stream", help="Disable streamed model output."),
):
    updated_any = False

    if provider:
        normalized = provider.strip().lower()
        if normalized not in {"ollama", "groq"}:
            _display_error("Invalid --provider value. Use ollama or groq.")
            raise typer.Exit(2)
        updated = set_provider(normalized)
        console.print(f"[green]✓[/green] Provider set to [cyan]{updated.provider}[/cyan]")
        updated_any = True

    target_model = model or llm
    if target_model:
        updated = set_model(target_model)
        console.print(f"[green]✓[/green] Model set to [cyan]{updated.model}[/cyan]")
        updated_any = True

    if no_stream:
        updated = set_stream(False)
        console.print(f"[green]✓[/green] Stream output {'enabled' if updated.stream else 'disabled'}")
        updated_any = True

    if stream is not None:
        normalized = stream.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            stream_value = True
        elif normalized in {"false", "0", "no", "off"}:
            stream_value = False
        else:
            _display_error("Invalid --stream value. Use true or false.")
            raise typer.Exit(2)

        updated = set_stream(stream_value)
        console.print(f"[green]✓[/green] Stream output {'enabled' if updated.stream else 'disabled'}")
        updated_any = True

    if show or not updated_any:
        console.print(show_config())


@app.command()
def clear():
    clear_history()
    console.print("[green]✓[/green] Conversation history cleared.")


@app.command()
def status():
    cfg = load_config()
    provider = cfg.provider.strip().lower()
    if provider == "groq":
        api_key_ok = bool(get_groq_api_key())
        model_ok = check_groq_model_available(cfg.model) if api_key_ok else False
        provider_status = "[green]configured[/green]" if api_key_ok else "[red]missing GROQ_API_KEY[/red]"
        model_status = "[green]available[/green]" if model_ok else "[red]not found[/red]"
        rprint(f"  Provider   : [cyan]{provider}[/cyan] — {provider_status}")
        rprint(f"  Model      : [cyan]{cfg.model}[/cyan] — {model_status}")
    else:
        ollama_ok = check_ollama_running()
        model_ok = check_model_available(cfg.model) if ollama_ok else False
        provider_status = "[green]running[/green]" if ollama_ok else "[red]not running[/red]"
        model_status = "[green]available[/green]" if model_ok else "[red]not found[/red]"
        rprint(f"  Provider   : [cyan]ollama[/cyan] — {provider_status}")
        rprint(f"  Model      : [cyan]{cfg.model}[/cyan] — {model_status}")

    rprint(f"  {history_summary()}")


if __name__ == "__main__":
    app()