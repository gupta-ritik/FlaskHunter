# FlakeHunter — Codex Evidence Pack

Project: an agent that finds flaky pytest tests, diagnoses the root cause by
re-running them in isolation, and opens a verified fix PR or a quarantine PR.
Challenge: Build with Codex — One-Month Challenge.
Codex surface used: Codex extension in VS Code (Windows), "Ask for approval" mode.
Model log: see MODEL_LOG.md for model and reasoning effort per task.
Project tracking: https://github.com/gupta-ritik/FlaskHunter/issues (13 issues, #3–#15)

---

## 1. Understand
**Date:** 2026-11-23
**What I did:** Asked Codex, in read-only mode, to explain pytest-randomly,
pytest-repeat, freezegun and pytest-socket and how FlakeHunter could use each,
separating "I am sure" from "I suspect".
**Effort:** Medium (needed accurate tool knowledge; no code written).
**Result:** Codex mapped each root cause to a tool: test order/shared state →
pytest-randomly, timing/accumulated state → pytest-repeat, clock/timezone →
freezegun, network → pytest-socket. It also suggested changing one factor per
experiment, which became a design rule for FlakeHunter.
**Verification:** Confirmed no files were changed (Explorer showed only LICENSE).
**Evidence:** screenshots/01-understand-readonly.png
**Environment check (W1-1, #3) · 2026-11-24:** Confirmed the sandbox prerequisites
on the reference laptop: WSL 2.7.14 with `docker-desktop` running on WSL 2,
Docker 29.7.2 with Linux containers (`OSType: linux`), and network isolation
verified — `docker run --rm --network=none alpine ip route` printed no routes.
Docker VM memory is 7.5 GB, so Ollama will run on the Windows host, not in Docker.
**Evidence:** screenshots/07-docker-wsl-check.png


## 2. Plan
**Date:** 2026-11-24
**What I did:** Codex drafted docs/PLAN.md, docs/issues.md and docs/decisions.md
(effort High).
**My review:** The plan was rigorous but too heavy for a solo 4-week build.
**My edits:** Split v1 vs v1.1 scope; added a week-1 vertical slice; added the
Windows Docker/WSL2 risk; added a real-world flaky-test reproduction target;
added verified problem statistics; changed the single model to a 2-model
comparison; added a TL;DR for judges.
**PR:** #16 docs: add plan, issues and ADRs with review edits (merged)
**Evidence:** docs/PLAN.md, docs/issues.md, docs/decisions.md

**Project tracking (2026-11-24):** Used Codex with the GitHub CLI (effort Medium)
to turn docs/issues.md into 13 GitHub issues (W1-1 … W4-3, #3–#15) with
lifecycle and effort labels, a v1 label, and four weekly milestones. Codex
listed existing issues first to avoid duplicates, and I approved each gh
command. docs/issues.md now links each task to its real issue number.
From now on every implementation PR references its issue with "Fixes #N".
**Evidence:** https://github.com/gupta-ritik/FlaskHunter/issues ·
screenshots/05-issues-board.png

## 3. Build

### Project skeleton
**Date:** 2026-11-24
**What I did:** Asked Codex to create the project skeleton: src layout, Typer
CLI with --version, pyproject.toml, one test, CI workflow, .gitignore, README.
**Effort:** Light (boilerplate, no design decisions).
**Result:** 9 files created (+111 lines). Codex ran ruff (all checks passed),
mypy (no issues in 3 source files) and pytest (1 passed).
**My review:** Checked the diff with "View changes" before committing; confirmed
virtual-env and cache folders were git-ignored.
**Commit:** ba14af2 — chore: project skeleton with CI
**Evidence:** screenshots/02-skeleton-checks.png

### W1-2 · Ingest CI history and detect flaky candidates
**Date:** 2026-11-24 · **Issue:** #4 · **PR:** #18 · **Effort:** Medium
**What I did:** Codex implemented local pytest JUnit ingestion,
comparable-attempt grouping (same SHA + same environment), deduplication of
repeated uploads, and the `flakehunter history` CLI. Work was test-first.
**Test-first evidence:** The first test run stopped at collection because the
history module did not exist yet. After implementation, ruff and mypy passed
and pytest reported 8 passing tests.
**Replay:** `flakehunter history tests/fixtures/history` produced one candidate
(one pass, one fail) and warned about the folder with missing metadata.
A separate offline replay used two real pytest-generated reports (one passing,
one failing) with matching SHA and environment. After copying the failed report
into the same attempt folder, the CLI still reported one pass and one fail for
`test_probe.py::test_ci_probe` (deduplication works) and preserved its
`AssertionError` signature.
**My check:** Ran `flakehunter history tests/fixtures/history` myself: exactly
1 candidate (`tests/test_sample.py::TestCases::test_flaky[case.a]`, 1 pass /
1 fail, `AssertionError: value differs`). Confirmed the pass/fail pair on
different environments and the stable failure were NOT flagged.
**Evidence:** screenshots/06-w1-2-candidates.png ·
[acceptance criteria](docs/issues.md#w1-2--ingest-comparable-github-actions-test-results--4) ·
[history format](docs/history-format.md) · [fixture tests](tests/test_history.py)

**W1-3 rules-only replay (2026-11-24).** The test-first run failed with a
missing CLI command and two missing modules. Two locally captured pytest JUnit
reports produced one candidate. The trigger reproduced
`AssertionError: shared state was changed` in all five runs and the control
passed all five. The report classified `order_dependence` with confidence
0.80. Both stable demo tests passed, and the main suite collected 16 passing
tests under `tests/`. Ruff and mypy passed.

**Replay:** `flakehunter investigate --history tests/fixtures/slice/history --repo demo_repo`.
**Evidence:** [captured JUnit history](tests/fixtures/slice/history),
[demo tests](demo_repo/tests/test_order.py), and [integration test](tests/test_slice.py).

## 4. Test
**CI:** First GitHub Actions run (CI #1) passed in 19s on main.
**Evidence:** screenshots/03-ci-green.png
**Test-first practice:** W1-2 tests were written and shown failing before the
implementation (see Build › W1-2).
**Windows sandbox issue (2026-11-24):** A Codex run left three temp folders with
mangled names (`Usersritik.guptaDesktopFlaskHunter.venvhistory-pytest-*`) in the
repo root, owned by the sandbox user. pytest collection failed with
"Access is denied" and my user could not delete them, even with `takeown`.
Codex removed them. Prevented recurrence by restricting pytest to
`testpaths = ["tests"]`, git-ignoring `/Users*/`, and adding an AGENTS.md rule
(use `tmp_path`, never absolute Windows paths for `--basetemp`).
Result: ruff clean, mypy clean, 8 passed.
_To do: flaky demo repo + benchmark (benchmark/measure_flakiness.py results)._

## 5. Review
**Date:** 2026-11-24
**PR:** #2 docs: add AGENTS.md with agent rules and evidence
**What I did:** Requested @codex review via the Codex GitHub integration (manual trigger).
**Result:** "Didn't find any major issues" 👍 on commit 88b1e30.
**My action:** No changes needed; merged.
**Lesson:** First attempt accidentally closed the PR ("Close with comment") and
showed main and branch identical because files weren't committed — learned to
check `git status` before pushing.
**Evidence:** screenshots/04-codex-review.png

| PR | Change | Codex review result | My action |
|---|---|---|---|
| #2 | AGENTS.md + evidence | No major issues 👍 | Merged |
| #16 | Plan, issues, ADRs | <result> | Merged |
| #17 | Link issues | <result> | Merged |
| #18 | W1-2 history ingestion (Fixes #4) | <result> | <action> |

## 6. Document
**Date:** 2026-11-24
**What I did:** Generated AGENTS.md with /init (effort Light).
**My edits:** The generated file was accurate but missing safety rules. I added:
agent rules (tests for every change, never delete failing tests, no internet in
unit tests, no unexplained dependencies, smallest change, run all checks before
finishing), conventional-commit prefixes, a Windows venv activation note, and
corrected the description of EVIDENCE.md. I left out a benchmark rule because
benchmark/ does not exist yet ("only what is true today").
**PR:** #2 (merged after @codex review)
**Evidence:** AGENTS.md, docs/history-format.md (W1-2 input format)

## 7. Ship
_To do: PyPI release, GitHub Action, setup instructions in README._

## 8. Automate
_To do: nightly scheduled workflow running FlakeHunter on its own repo and the demo repo._

---



## Codex capabilities used (running list)
- [x] Read-only exploration (Understand)
- [x] Approval mode for file edits and commands
- [x] /init for AGENTS.md
- [x] AGENTS.md as standing instructions
- [x] @codex review on pull requests
- [x] Codex + GitHub CLI for project tracking (issues, labels, milestones)
- [x] Test-first implementation (failing tests shown before code)
- [ ] Skills (.agents/skills/*/SKILL.md)
- [ ] Scheduled tasks / GitHub Actions automation