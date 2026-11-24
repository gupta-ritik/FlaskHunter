import subprocess
from pathlib import Path

import pytest

from flakehunter.replay import replay_order_dependence


def test_replay_records_a_per_run_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def expire(
        argv: list[str], *, cwd: Path, timeout: float, **kwargs: object
    ) -> subprocess.CompletedProcess[bytes]:
        assert cwd == tmp_path
        assert timeout == 30
        raise subprocess.TimeoutExpired(argv, timeout)

    monkeypatch.setattr(subprocess, "run", expire)
    trigger, control = replay_order_dependence(
        tmp_path, "tests/test_demo.py::test_first", "tests/test_demo.py::test_second"
    )
    for arm in (trigger, control):
        assert len(arm.trials) == 5
        assert (arm.passes, arm.fails) == (0, 0)
        assert all(
            trial.outcome == "timeout" and trial.exit_code is None
            for trial in arm.trials
        )
