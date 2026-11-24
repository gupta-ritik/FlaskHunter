# Repository Guidelines

## Project Structure

- `src/flakehunter/` contains the Python package. `cli.py` defines the Typer app
  exposed by the `flakehunter` command, and `__init__.py` reads the installed
  package version from distribution metadata. `history.py` loads CI test history
  (JUnit XML + `metadata.json`) and detects flaky candidates.
- `tests/` contains pytest tests. `test_cli.py` exercises the version flag and
  `test_history.py` covers history ingestion using fixtures in `tests/fixtures/`.
- `docs/` holds the plan (`PLAN.md`), issue drafts (`issues.md`), architecture
  decisions (`decisions.md`) and the history input format (`history-format.md`).
- `pyproject.toml` defines package metadata, dependencies, and tool settings.
  `.github/workflows/ci.yml` runs checks on pushes and pull requests.
- `MODEL_LOG.md` records which Codex model and reasoning effort was used for each
  task and why. `EVIDENCE.md` is the Codex evidence pack, organised by lifecycle
  stage (Understand, Plan, Build, Test, Review, Document, Ship, Automate).

## Local Development and CI

Use a Python 3.12 virtual environment with pip 25.1 or newer. On Windows,
activate it with `.venv\Scripts\activate`. Run these commands from the
repository root:

| Command | Purpose |
| --- | --- |
| `python -m pip install -e . --group dev` | Install the package in editable mode with development tools. |
| `flakehunter --version` | Verify the installed CLI and package version. |
| `flakehunter history <path>` | List flaky candidates from a local history directory. |
| `ruff check .` | Lint the repository. |
| `mypy src tests` | Type-check source and tests. |
| `pytest` | Run the test suite (collects only `tests/`). |

## Rules for Coding Agents

- Every behaviour change needs a test. Write the failing test first when fixing a bug.
- Never delete, skip, or weaken a failing test to make CI green.
- Unit tests must never call the internet; use mocks or local fixtures.
- Do not add dependencies without stating why in the pull request.
- Make the smallest change that solves the task; do not refactor unrelated code.
- Before finishing any task, run `ruff check . && mypy src tests && pytest`
  and report the results.
- On Windows, use pytest's default `tmp_path` fixture; never pass absolute
  Windows paths to `--basetemp` or create folders outside `tests/`.

## Coding Style

Use four spaces for indentation, `snake_case` for Python modules and functions,
and `PascalCase` for classes. Annotate function parameters and return types.
Keep Typer command handlers focused on arguments and output, and put reusable
logic in package modules.

## Testing

Name test files `test_*.py` and test functions `test_*`. Use Typer's
`CliRunner` to check CLI exit codes and output. Run a single file with
`pytest tests/test_cli.py`. When investigating order-dependent failures, record
the pytest-randomly seed and replay it with `pytest --randomly-seed=<seed>`.
CI currently sets no coverage threshold. Add regression tests for behaviour changes.

## Commits and Pull Requests

Use conventional-commit subjects: `feat:`, `fix:`, `docs:`, `test:`, `chore:`
(for example, `chore: project skeleton with CI`). Keep commits small and focused.
In a pull request, start the description with `Fixes #<issue>` when it completes
an issue, describe the change, and report the checks you ran. For flaky-test
fixes, include the failing test's node ID, reproduction steps, and before-and-after
results. Never merge a pull request or force-push without the maintainer's approval.