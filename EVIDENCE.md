# FlakeHunter — Codex Evidence Pack

Project: an agent that finds flaky pytest tests, diagnoses the root cause by
re-running them in isolation, and opens a verified fix PR or a quarantine PR.
Challenge: Build with Codex — One-Month Challenge.
Codex surface used: Codex extension in VS Code (Windows), "Ask for approval" mode.
Model log: see MODEL_LOG.md for model and reasoning effort per task.

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

## 2. Plan
_To do: docs/PLAN.md (effort High), docs/architecture.svg, docs/issues.md.
Record what I changed in Codex's plan and why._

## 3. Build
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

## 4. Test
**CI:** First GitHub Actions run (CI #1) passed in 19s on main.
**Evidence:** screenshots/03-ci-green.png
_To do: flaky demo repo + benchmark (benchmark/measure_flakiness.py results)._

## 5. Review
_To do: @codex review on each pull request — record what it found and what I changed._

## 6. Document
**Date:** 2026-11-24
**What I did:** Generated AGENTS.md with /init (effort Light).
**My edits:** The generated file was accurate but missing safety rules. I added:
agent rules (tests for every change, never delete failing tests, no internet in
unit tests, no unexplained dependencies, smallest change, run all checks before
finishing), conventional-commit prefixes, a Windows venv activation note, and
corrected the description of EVIDENCE.md. I left out a benchmark rule because
benchmark/ does not exist yet ("only what is true today").
**Evidence:** AGENTS.md, PR link: <add after opening PR>

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
- [ ] Skills (skills/*/SKILL.md)
- [ ] Scheduled tasks / GitHub Actions automation





**Date:** 2026-11-24
**PR:** #2 docs: add AGENTS.md with agent rules and evidence
**What I did:** Requested @codex review via the Codex GitHub integration (manual trigger).
**Result:** "Didn't find any major issues" 👍 on commit 88b1e30.
**My action:** No changes needed; merged.
**Lesson:** First attempt accidentally closed the PR ("Close with comment") and
showed main and branch identical because files weren't committed — learned to
check `git status` before pushing.
**Evidence:** screenshots/04-codex-review.png