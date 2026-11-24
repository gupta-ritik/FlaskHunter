# Model & Reasoning-Effort Log

Every Codex task, the model and reasoning effort used, and why.
Policy: start at the lowest suitable effort; escalate only for design decisions,
trust boundaries, or after a failed attempt (see docs/PLAN.md §9).

| Date | Stage | Task | Model | Effort | Why this choice | Result |
|---|---|---|---|---|---|---|
| 2026-11-23 | Understand | Research pytest plugins (read-only) | GPT-6.2 Sol | Medium | Needs accurate tool knowledge, no code | Clear sure/suspect split; one-factor-per-experiment rule adopted |
| 2026-11-24 | Build | Project skeleton + CI | GPT-6.2 Sol | Light | Boilerplate, no design decisions | ruff/mypy/pytest passed; CI green on first run |
| 2026-11-24 | Document | AGENTS.md via /init | GPT-6.2 Sol | Light | Simple doc from existing files | Accurate but missing safety rules; I added them by hand |
| 2026-11-24 | Plan | PLAN/issues/ADRs draft | GPT-6.2 Sol | High | Sets architecture and scope; mistakes are costly | Rigorous but over-scoped for 4 weeks |
| 2026-11-24 | Plan | Apply my review edits | GPT-6.2 Sol | Medium | Edits to an existing plan, no new design | v1/v1.1 split, vertical slice, WSL2 risk, real-flake target, 2-model comparison, TL;DR added |
| 2026-11-24 | Plan | Create GitHub issues, labels, milestones (gh CLI) | GPT-6.2 Sol | Medium | Multi-step CLI work; must avoid duplicates and wrong labels | 13 issues created (#3–#15), no duplicates; issues.md linked |
| 2026-11-24 | Build | W1-2 history ingestion + candidate detection (#4) | GPT-6.2 Sol | Medium | Cross-file parsing + detection logic, test-first | Tests failed first (missing module), then 8 passed; ruff + mypy clean |
| 2026-11-24 | Test | Remove locked sandbox temp folders | GPT-6.2 Sol | Light | Narrow cleanup task, no design | Folders removed; prevented with `testpaths` + AGENTS.md rule |