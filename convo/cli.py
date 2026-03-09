import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from rich import print as rprint

from convo.config import load_config, set_model, show_config
from convo.history import load_history, save_history, append_exchange, clear_history, history_summary
from convo.ollama import chat, check_ollama_running, check_model_available
from convo.prompt import build_system_prompt

app = typer.Typer(
    help="convo — plain English to Linux commands, powered by a local LLM.",
    add_completion=False,
)
console = Console()


def _preflight_checks(model: str) -> bool:
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


def _display_clarification(question: str) -> None:
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


@app.command()
def ask(
    query: str = typer.Argument(..., help="What you want to do in plain English."),
    new: bool = typer.Option(False, "--new", "-n", help="Start a fresh conversation."),
):
    config = load_config()

    if not _preflight_checks(config.model):
        raise typer.Exit(1)

    if new:
        clear_history()
        console.print("[dim]Starting a new conversation.[/dim]\n")

    history = load_history()
    system_prompt = build_system_prompt()

    with console.status("[dim]Thinking...[/dim]", spinner="dots"):
        response = chat(
            model=config.model,
            system_prompt=system_prompt,
            history=history,
            user_message=query,
        )

    if response.kind == "command":
        _display_command(response.command, response.reason)

    elif response.kind == "clarify":
        _display_clarification(response.clarification)

    else:
        _display_error(response.raw or "Unknown error.")

    updated_history = append_exchange(history, query, response.raw or "")
    save_history(updated_history)


@app.command()
def config(
    llm: str = typer.Option(None, "--llm", help="Set the Ollama model to use."),
    show: bool = typer.Option(False, "--show", help="Show current config."),
):
    if llm:
        updated = set_model(llm)
        console.print(f"[green]✓[/green] Model set to [cyan]{updated.model}[/cyan]")
        return

    console.print(show_config())


@app.command()
def clear():
    clear_history()
    console.print("[green]✓[/green] Conversation history cleared.")


@app.command()
def status():
    cfg = load_config()

    ollama_ok = check_ollama_running()
    model_ok = check_model_available(cfg.model) if ollama_ok else False

    ollama_status = "[green]running[/green]" if ollama_ok else "[red]not running[/red]"
    model_status = "[green]available[/green]" if model_ok else "[red]not found[/red]"

    rprint(f"  Ollama     : {ollama_status}")
    rprint(f"  Model      : [cyan]{cfg.model}[/cyan] — {model_status}")
    rprint(f"  {history_summary()}")


if __name__ == "__main__":
    app()