"""Command-line interface for FlakeHunter."""

import json
import shlex
import warnings
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from flakehunter import __version__
from flakehunter.classify import classify
from flakehunter.history import HistoryWarning, detect_candidates, load_history
from flakehunter.replay import replay_order_dependence

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


@app.command()
def investigate(
    history_path: Annotated[
        Path, typer.Option("--history", exists=True, file_okay=False, resolve_path=True)
    ],
    repo: Annotated[
        Path, typer.Option("--repo", exists=True, file_okay=False, resolve_path=True)
    ],
) -> None:
    """Replay the demo order-dependence case and write an investigation report."""
    target = "tests/test_order.py::test_starts_clean"
    predecessor = "tests/test_order.py::test_changes_state"
    candidates = [
        candidate
        for candidate in detect_candidates(load_history(history_path))
        if candidate.node_id == target
    ]
    if len(candidates) != 1:
        typer.echo(
            "Expected one comparable history candidate for the demo test.", err=True
        )
        raise typer.Exit(1)

    candidate = candidates[0]
    signature = candidate.signatures[0] if len(candidate.signatures) == 1 else None
    trigger, control = replay_order_dependence(repo, predecessor, candidate.node_id)
    diagnosis = classify(signature, trigger.trials, control.trials)

    report = {
        "node_id": candidate.node_id,
        "head_sha": candidate.head_sha,
        "env_key": candidate.env_key,
        "signature": signature,
        "repo": str(repo),
        **diagnosis.model_dump(),
    }
    typer.echo(f"Node ID: {candidate.node_id}")
    typer.echo(f"Signature: {signature or 'unavailable'}")
    typer.echo(f"Cause: {diagnosis.cause}")
    typer.echo(f"Confidence: {diagnosis.confidence:.2f}")
    typer.echo(f"cd {shlex.quote(repo.name)}")
    for name, arm in (("trigger", trigger), ("control", control)):
        report[name] = arm.model_dump() | {"passes": arm.passes, "fails": arm.fails}
        typer.echo(f"{name.capitalize()}: {arm.passes} passed, {arm.fails} failed")
        nodes = (
            (predecessor, candidate.node_id)
            if name == "trigger"
            else (candidate.node_id,)
        )
        typer.echo(shlex.join(("python", "-m", "pytest", "-p", "no:randomly", *nodes)))

    reports = Path("reports")
    reports.mkdir(exist_ok=True)
    report_path = reports / f"investigation-{uuid4().hex}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"Report: {report_path}")
