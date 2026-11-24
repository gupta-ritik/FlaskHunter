"""Replay a known order-dependent scenario in fresh pytest processes."""

import subprocess
import sys
import tempfile
from pathlib import Path
from time import perf_counter
from typing import Literal
from xml.etree import ElementTree

from pydantic import BaseModel

from flakehunter.history import Outcome, read_junit


class Trial(BaseModel):
    exit_code: int | None
    outcome: Outcome | Literal["timeout"]
    signature: str | None
    elapsed_s: float


class ReplayArm(BaseModel):
    argv: list[str]
    trials: list[Trial]

    @property
    def passes(self) -> int:
        return sum(trial.outcome == "pass" for trial in self.trials)

    @property
    def fails(self) -> int:
        return sum(trial.outcome == "fail" for trial in self.trials)


def _run_trial(
    repo: Path, xml_path: Path, argv: list[str], node_ids: list[str], timeout_s: float
) -> Trial:
    xml_path.unlink(missing_ok=True)
    started = perf_counter()
    try:
        result = subprocess.run(
            argv,
            cwd=repo,
            check=False,
            timeout=timeout_s,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return Trial(
            exit_code=None,
            outcome="timeout",
            signature=None,
            elapsed_s=perf_counter() - started,
        )
    except OSError:
        return Trial(
            exit_code=None,
            outcome="error",
            signature=None,
            elapsed_s=perf_counter() - started,
        )

    elapsed_s = perf_counter() - started
    try:
        observations = read_junit(xml_path)
    except (OSError, ElementTree.ParseError, LookupError, ValueError):
        observations = []

    outcome: Outcome = "error"
    signature = None
    if [observation.node_id for observation in observations] == node_ids and all(
        observation.outcome == "pass" for observation in observations[:-1]
    ):
        target = observations[-1]
        expected_exit = {"pass": 0, "fail": 1, "skip": 0, "error": 1}
        if result.returncode == expected_exit[target.outcome]:
            outcome, signature = target.outcome, target.signature
    return Trial(
        exit_code=result.returncode,
        outcome=outcome,
        signature=signature,
        elapsed_s=elapsed_s,
    )


def replay_order_dependence(
    repo: Path, predecessor: str, target: str, *, timeout_s: float = 30
) -> tuple[ReplayArm, ReplayArm]:
    """Run five predecessor/target trials and five target-only trials in pairs."""
    with tempfile.NamedTemporaryFile(
        prefix="flakehunter-replay-", suffix=".xml", delete=False
    ) as xml:
        xml_path = Path(xml.name)

    command = [
        sys.executable,
        "-B",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:randomly",
        "-p",
        "no:cacheprovider",
        "--confcutdir=.",
        f"--junitxml={xml_path}",
    ]
    trigger_nodes = [predecessor, target]
    control_nodes = [target]
    trigger = ReplayArm(argv=command + trigger_nodes, trials=[])
    control = ReplayArm(argv=command + control_nodes, trials=[])
    try:
        for _ in range(5):
            trigger.trials.append(
                _run_trial(repo, xml_path, trigger.argv, trigger_nodes, timeout_s)
            )
            control.trials.append(
                _run_trial(repo, xml_path, control.argv, control_nodes, timeout_s)
            )
    finally:
        xml_path.unlink(missing_ok=True)
    return trigger, control
