"""Command-line interface for FlakeHunter."""

from typing import Annotated

import typer

from flakehunter import __version__

app = typer.Typer(help="Investigate flaky pytest tests.")


def show_version(value: bool) -> None:
    if value:
        typer.echo(f"flakehunter {__version__}")
        raise typer.Exit()


@app.command()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", callback=show_version, is_eager=True),
    ] = False,
) -> None:
    """Run the FlakeHunter CLI."""
    typer.echo(ctx.get_help())
