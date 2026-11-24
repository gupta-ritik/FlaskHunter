"""Command-line interface for FlakeHunter."""

import warnings
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from flakehunter import __version__
from flakehunter.history import HistoryWarning, detect_candidates, load_history

app = typer.Typer(help="Investigate flaky pytest tests.")


def show_version(value: bool) -> None:
    if value:
        typer.echo(f"flakehunter {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", callback=show_version, is_eager=True),
    ] = False,
) -> None:
    """Run the FlakeHunter CLI."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def history(path: Path) -> None:
    """Find flaky candidates in local JUnit history."""
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", HistoryWarning)
        rows = load_history(path)

    table = Table(title="Flaky candidates")
    for heading in ("Node ID", "SHA", "Env", "Passes", "Fails", "Signatures"):
        table.add_column(heading, overflow="fold")
    for candidate in detect_candidates(rows):
        table.add_row(
            Text(candidate.node_id),
            Text(candidate.head_sha),
            Text(candidate.env_key),
            str(candidate.passes),
            str(candidate.fails),
            Text("\n".join(candidate.signatures)),
        )
    Console().print(table)

    warning_console = Console(stderr=True)
    for item in captured:
        warning_console.print(Text(f"Warning: {item.message}"))
