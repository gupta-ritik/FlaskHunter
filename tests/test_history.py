from pathlib import Path

import pytest
from typer.testing import CliRunner

from flakehunter import history
from flakehunter.cli import app

HISTORY_PATH = Path(__file__).parent / "fixtures" / "history"
FLAKY_NODE = "tests/test_sample.py::TestCases::test_flaky[case.a]"


def test_load_history_preserves_observations_and_deduplicates_uploads() -> None:
    with pytest.warns(history.HistoryWarning, match=r"102-1.*metadata\.json"):
        rows = history.load_history(HISTORY_PATH)

    assert len(rows) == 11
    flaky_fail, flaky_pass = sorted(
        (row for row in rows if row.node_id == FLAKY_NODE), key=lambda row: row.attempt
    )
    assert flaky_fail == history.HistoryRow(
        run_id=100,
        attempt=1,
        job_key='["example/project","CI","unit"]',
        env_key='{"python":"3.12","os":"linux"}',
        head_sha="abc123",
        node_id=FLAKY_NODE,
        outcome="fail",
        signature="AssertionError: value differs",
        source_url="https://example.test/runs/100/attempts/1",
    )
    assert (flaky_pass.outcome, flaky_pass.signature) == ("pass", None)
    assert flaky_pass.env_key == flaky_fail.env_key
    assert {
        (row.outcome, row.signature)
        for row in rows
        if row.node_id.endswith("test_setup")
    } == {
        ("error", "RuntimeError: setup failed"),
        ("pass", None),
    }
    assert any(row.outcome == "skip" for row in rows)


def test_detect_candidates_counts_distinct_attempts() -> None:
    with pytest.warns(history.HistoryWarning):
        rows = history.load_history(HISTORY_PATH)

    [candidate] = history.detect_candidates(rows + rows)

    assert candidate.node_id == FLAKY_NODE
    assert candidate.head_sha == "abc123"
    assert candidate.env_key == '{"python":"3.12","os":"linux"}'
    assert (candidate.passes, candidate.fails) == (1, 1)
    assert candidate.signatures == ["AssertionError: value differs"]


def test_detect_candidates_requires_comparable_distinct_attempts() -> None:
    with pytest.warns(history.HistoryWarning):
        rows = history.load_history(HISTORY_PATH)
    failed = next(
        row for row in rows if row.node_id == FLAKY_NODE and row.outcome == "fail"
    )
    passed = next(
        row for row in rows if row.node_id == FLAKY_NODE and row.outcome == "pass"
    )

    assert (
        history.detect_candidates([failed, passed.model_copy(update={"attempt": 1})])
        == []
    )
    assert (
        history.detect_candidates(
            [failed, passed.model_copy(update={"head_sha": "def456"})]
        )
        == []
    )
    assert (
        history.detect_candidates(
            [failed, passed.model_copy(update={"job_key": "other"})]
        )
        == []
    )
    assert (
        len(
            history.detect_candidates(
                [
                    failed,
                    passed.model_copy(
                        update={
                            "run_id": 200,
                            "attempt": 1,
                        }
                    ),
                ]
            )
        )
        == 1
    )


def test_load_history_warns_about_invalid_metadata_and_missing_or_invalid_reports(
    tmp_path: Path,
) -> None:
    metadata = (HISTORY_PATH / "100-1" / "metadata.json").read_text(encoding="utf-8")
    for run_id in (100, 200, 300):
        folder = tmp_path / f"{run_id}-1"
        folder.mkdir()
        contents = (
            "{}"
            if run_id == 100
            else metadata.replace('"run_id": 100', f'"run_id": {run_id}')
        )
        (folder / "metadata.json").write_text(contents, encoding="utf-8")
    (tmp_path / "300-1" / "bad.xml").write_text("<testsuite>", encoding="utf-8")
    (tmp_path / "300-1" / "good.xml").write_text(
        '<testsuite><testcase classname="tests.test_sample" name="test_ok" /></testsuite>',
        encoding="utf-8",
    )

    with pytest.warns(history.HistoryWarning) as warnings:
        [row] = history.load_history(tmp_path)

    assert row.node_id == "tests/test_sample.py::test_ok"
    assert len(warnings) == 3
    assert any(
        "100-1" in str(item.message) and "metadata.json" in str(item.message)
        for item in warnings
    )
    assert any(
        "200-1" in str(item.message) and "JUnit XML" in str(item.message)
        for item in warnings
    )
    assert any(
        "300-1" in str(item.message) and "bad.xml" in str(item.message)
        for item in warnings
    )


def test_history_cli_prints_candidates_and_warnings() -> None:
    result = CliRunner().invoke(
        app, ["history", str(HISTORY_PATH)], env={"COLUMNS": "160"}
    )

    assert result.exit_code == 0, result.output
    assert FLAKY_NODE in result.output
    assert "abc123" in result.output
    assert "AssertionError: value differs" in result.output
    assert "Passes" in result.output and "Fails" in result.output
    assert (
        "test_stable" not in result.output and "test_env_sensitive" not in result.output
    )
    assert "Warning" in result.output and "102-1" in result.output


def test_load_history_preserves_node_ids_when_junit_provides_a_path(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "100-1"
    folder.mkdir()
    (folder / "metadata.json").write_bytes(
        (HISTORY_PATH / "100-1" / "metadata.json").read_bytes()
    )
    (folder / "results.xml").write_text(
        """<testsuite>
        <testcase classname="tests.api.v2.test_api.lowercase" name="test_api"
                  file="tests/api.v2/test_api.py" />
        <testcase classname="ambiguous" name="test_api">
          <properties><property name="nodeid" value="tests/api.v2/test_api.py::test_api[a.b]" /></properties>
        </testcase>
        </testsuite>""",
        encoding="utf-8",
    )

    assert {row.node_id for row in history.load_history(tmp_path)} == {
        "tests/api.v2/test_api.py::lowercase::test_api",
        "tests/api.v2/test_api.py::test_api[a.b]",
    }


def test_history_cli_wraps_long_node_ids_without_truncating_them() -> None:
    result = CliRunner().invoke(
        app, ["history", str(HISTORY_PATH)], env={"COLUMNS": "80"}
    )

    assert result.exit_code == 0, result.output
    cells = [
        line.replace("│", "|").split("|")[1].strip()
        for line in result.output.splitlines()
        if line.lstrip().startswith(("|", "│"))
    ]
    assert FLAKY_NODE in "".join(cells), result.output
