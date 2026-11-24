import json
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from flakehunter.cli import app

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "tests" / "fixtures" / "slice" / "history"
DEMO = ROOT / "demo_repo"
TARGET = "tests/test_order.py::test_starts_clean"
PREDECESSOR = "tests/test_order.py::test_changes_state"
SIGNATURE = "AssertionError: shared state was changed"


def test_investigate_replays_demo_and_writes_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app, ["investigate", "--history", str(HISTORY), "--repo", str(DEMO)]
    )

    assert result.exit_code == 0, result.output
    assert TARGET in result.output and SIGNATURE in result.output
    assert "order_dependence" in result.output and "0.80" in result.output
    lines = result.output.splitlines()
    assert "cd demo_repo" in lines
    assert f"python -m pytest -p no:randomly {PREDECESSOR} {TARGET}" in lines
    assert f"python -m pytest -p no:randomly {TARGET}" in lines
    assert str(DEMO) not in result.output
    assert sys.executable not in result.output
    assert "--junitxml" not in result.output
    assert "Trigger: 0 passed, 5 failed" in result.output
    assert "Control: 5 passed, 0 failed" in result.output

    [report_path] = (tmp_path / "reports").glob("*.json")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["node_id"] == TARGET
    assert report["signature"] == SIGNATURE
    assert (report["cause"], report["confidence"]) == ("order_dependence", 0.80)
    assert report["repo"] == str(DEMO)

    trigger, control = report["trigger"], report["control"]
    assert (trigger["passes"], trigger["fails"]) == (0, 5)
    assert (control["passes"], control["fails"]) == (5, 0)
    assert trigger["argv"][-2:] == [PREDECESSOR, TARGET]
    assert control["argv"][-1:] == [TARGET] and PREDECESSOR not in control["argv"]
    for arm, outcome, exit_code, signature in (
        (trigger, "fail", 1, SIGNATURE),
        (control, "pass", 0, None),
    ):
        assert arm["argv"][0] == sys.executable
        assert "no:randomly" in arm["argv"]
        assert any(arg.startswith("--junitxml=") for arg in arm["argv"])
        assert len(arm["trials"]) == 5
        for trial in arm["trials"]:
            assert (trial["outcome"], trial["exit_code"], trial["signature"]) == (
                outcome,
                exit_code,
                signature,
            )
            assert trial["elapsed_s"] > 0
