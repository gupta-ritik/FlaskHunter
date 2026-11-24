# FlakeHunter issue drafts

**VERIFIED.** The repository has a Python 3.12 CLI scaffold, pytest smoke test, and CI workflow. **PLAN.** Each heading is an issue title. Acceptance criteria are future checks. Effort is a suggested Codex tier. Milestone IDs match [the plan](PLAN.md#10-four-week-milestones).

**PLAN.** Weeks 1–4 cover v1. The v1.1 backlog follows Week 4.

## Week 1 · Rules-only vertical slice

### W1-1 · Validate the problem and define judge evidence · [#3](https://github.com/gupta-ritik/FlaskHunter/issues/3)

**Lifecycle** `lifecycle:understand` · **Codex effort** Light

**Description.** Compare current flaky-test workflows and establish the build and judging references.

- [ ] Record two maintainer interviews and one anonymized incident. If access is unavailable, mark adoption as an assumption and record the evidence gap.
- [ ] Link the sourced comparison, plan, ADRs, and issue drafts from `EVIDENCE.md`.
- [ ] Add real Codex task records to `MODEL_LOG.md` with settings, rationale, checks, and evidence links.
- [ ] On Day 1, confirm Docker Desktop uses the WSL 2 backend with Linux containers. Record `wsl --version`, `wsl --list --verbose`, `docker info`, and the result of `docker run --rm --network=none alpine ip route` with a cached image. Expect no default route. If blocked, record the cause and use a Linux runner for sandbox work. [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)

### W1-2 · Ingest comparable GitHub Actions test results · [#4](https://github.com/gupta-ritik/FlaskHunter/issues/4)

**Lifecycle** `lifecycle:build` · **Codex effort** Medium

**Description.** Normalize JUnit observations and identify flakes across distinct attempts of comparable jobs.

- [ ] Preserve SHA, workflow/job, environment key, run/attempt, full pytest node ID, outcome, signature where available, and artifact URL.
- [ ] A captured pass/fail pair on the same SHA and environment produces one candidate after deduplication.
- [ ] Fixture tests cover duplicate uploads, missing artifacts, incompatible environments, and stable failures. Unit tests use local fixtures.

### W1-3 · Report one benchmark flake end to end · [#5](https://github.com/gupta-ritik/FlaskHunter/issues/5)

**Lifecycle** `lifecycle:build` · **Codex effort** Medium

**Description.** Take one synthetic benchmark flake from captured history through rules-only diagnosis to a report.

- [ ] Replay the local trigger and passing control, classify the candidate with deterministic rules, and report the node ID, signature, cause, and replay evidence.
- [ ] Run the full slice with local fixtures and without Docker, an LLM, or PRs.

## Week 2 · Diagnosis

### W2-1 · Run controlled probes in the Docker sandbox · [#6](https://github.com/gupta-ritik/FlaskHunter/issues/6)

**Lifecycle** `lifecycle:build` · **Codex effort** High

**Description.** Implement the runner-owned probe catalog and the isolated test harness.

- [ ] Provide replay commands and structured test, control, and failure records for the five benchmark families.
- [ ] Validate argv and environment, enforce resource limits, and terminate timed-out subprocesses.
- [ ] Run the probes with Docker `--network=none`. Demonstrate that egress and host credentials are unavailable and the runner-owned loopback stub works only for network experiments.
- [ ] Leave concurrency as stretch. Log the sandbox invariants and test results.

### W2-2 · Implement bounded LangGraph diagnosis and a Codex replay skill · [#7](https://github.com/gupta-ritik/FlaskHunter/issues/7)

**Lifecycle** `lifecycle:build` · **Codex effort** Medium

**Description.** Drive experiments, classification, abstention, and evidence capture through the typed graph.

- [ ] Tests cover the confidence rule, tied scores, a missing signature, six-experiment cap, and timeout.
- [ ] A report links the observed signature, paired outcomes, chosen cause or unknown, elapsed time, and replay commands.
- [ ] Store `.agents/skills/flake-investigation/SKILL.md` at the repository root and link a Codex invocation and its replay output from `EVIDENCE.md`. **VERIFIED.** Codex discovers repo-local skills under the root `.agents/skills/` directory. [Codex skill discovery](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

### W2-3 · Add the Ollama model adapter and measure the laptop profile · [#8](https://github.com/gupta-ritik/FlaskHunter/issues/8)

**Lifecycle** `lifecycle:build` · **Codex effort** Medium

**Description.** Add a swappable `LLMClient` for hypothesis ranking and patch drafting.

- [ ] A fake client exercises timeout and invalid-output paths. Rules-only reports work with the model disabled.
- [ ] Screen two candidate coder models on the RTX 5050 and record their identifiers, configurations, context cap, and measured peak VRAM. Both must fit within 8 GB VRAM for the Week 3 comparison.
- [ ] Programmatic rules own classification and verification regardless of model output.

### W2-4 · Complete the 20-case benchmark and separate scorer · [#9](https://github.com/gupta-ritik/FlaskHunter/issues/9)

**Lifecycle** `lifecycle:test` · **Codex effort** Medium

**Description.** Expand the Week 1 slice to ten synthetic flakes across five families and ten stable controls in `demo_repo`.

- [ ] Each family has two flakes. The isolation pair covers order dependence and direct shared state.
- [ ] Each flake has a benchmark-maintainer replay and a passing control for validating the label.
- [ ] Diagnosis runs from a snapshot without `benchmark/labels.json` or answer metadata. The scorer reads frozen predictions and labels separately.
- [ ] Missing, unknown, and timed-out predictions lower exact-label accuracy. False positives on controls are separately counted.

## Week 3 · Verified PRs and demo

### W3-1 · Gate candidate patches on base reproduction and 50 stress runs · [#10](https://github.com/gupta-ritik/FlaskHunter/issues/10)

**Lifecycle** `lifecycle:test` · **Codex effort** High

**Description.** Verify the exact candidate with a predeclared stress matrix and record runner evidence for that candidate in the same workflow run.

- [ ] Capture at least two base failures matching the original signature and two clean controls.
- [ ] Require 50 clean candidate trials in fresh pytest processes (35 trigger and 15 control) and a passing relevant suite.
- [ ] Tests reject failed, missing, skipped, xfailed, timed-out, or incomplete trials and cases where the target did not execute.

### W3-2 · Open evidence-backed fix or quarantine draft PRs · [#11](https://github.com/gupta-ritik/FlaskHunter/issues/11)

**Lifecycle** `lifecycle:review` · **Codex effort** High

**Description.** Add an opt-in PR step that consumes the runner's verified candidate and evidence in the same workflow run.

- [ ] A passing gate for the exact base and patch opens one fix draft PR. A rejected or unresolved flake produces a metadata-only quarantine draft PR with owner and expiry.
- [ ] Verify that only the PR step receives the publish token, with no exposure through the job-wide environment, checkout credentials, sandbox, or model.
- [ ] Dry-run reports match draft PR evidence. Permission failure stops publication, retries deduplicate, and the PR step has no merge or force-push path.
- [ ] Request `@codex review` on each PR and link or record the review outcome. Keep the required test checks active.

### W3-3 · Rehearse and document the end-to-end demo · [#12](https://github.com/gupta-ritik/FlaskHunter/issues/12)

**Lifecycle** `lifecycle:document` · **Codex effort** Medium

**Description.** Make both demo paths reproducible from history input to final report.

- [ ] Link one verified fix draft PR and one quarantine draft PR after failed verification in the demo repo.
- [ ] Include exact replay commands, baseline and candidate counts, checks, per-case timing, and any gaps in the README or sample report.
- [ ] Record a walkthrough a judge can follow without private credentials.
- [ ] Run both 8 GB coder candidates on the same cases and verification gate. Record pass rates, latency, and rejected drafts or timeouts. Select by gate pass rate and use latency to break ties.

## Week 4 · Automation, release, evidence

### W4-1 · Automate benchmark scoring on PRs and nightly · [#13](https://github.com/gupta-ritik/FlaskHunter/issues/13)

**Lifecycle** `lifecycle:automate` · **Codex effort** Medium

**Description.** Run deterministic evaluation on GitHub Actions and retain comparable results.

- [ ] PR and scheduled default-branch runs produce JSON artifacts and Markdown summaries with counts, timings, commit, image, and model/config identifiers.
- [ ] Link a real scheduled run and a comparison with an earlier run from `EVIDENCE.md`.
- [ ] Keep write credentials out of PR and benchmark jobs. Record a repeat execution of the Codex replay skill.

### W4-2 · Release the Python package and GitHub Action · [#14](https://github.com/gupta-ritik/FlaskHunter/issues/14)

**Lifecycle** `lifecycle:ship` · **Codex effort** Medium

**Description.** Publish a tagged release and document how to run or opt in to the action.

- [ ] Publish a GitHub release, versioned Action, and PyPI package from a maintainer-approved release workflow.
- [ ] A clean Python 3.12 environment installs the published package and runs `flakehunter --version` and a local dry-run smoke test.
- [ ] Link the release, PyPI artifact, and smoke results. Record any access blocker and its impact on delivery.

### W4-3 · Audit the judge evidence pack · [#15](https://github.com/gupta-ritik/FlaskHunter/issues/15)

**Lifecycle** `lifecycle:document` · **Codex effort** Light

**Description.** Check that each of the five rubric rows can be verified independently.

- [ ] `EVIDENCE.md` links a concrete artifact and result for all eight lifecycle stages, with any missing evidence marked.
- [ ] `MODEL_LOG.md` covers all Codex tasks and includes actual settings or an explicit unavailable value.
- [ ] Summarize accuracy, stable false positives, maximum investigation time, gate failures, and verified PR outcomes with raw evidence links.
- [ ] Reproduce at least two real flaky tests from open-source repositories. Report upstream repo, revision, node ID, replay command, matching failure, and passing control separately from the synthetic benchmark scores.

## v1.1 · Verification and publishing

### V1.1-1 · Strengthen verification and publishing

- [ ] Add receipt digests that bind the base, exact candidate patch, and verification evidence.
- [ ] Move draft PR writes to a separate trusted publisher job that validates the receipt before writing.
- [ ] Pin the sandbox image by digest and record it in verification evidence.
- [ ] Implement the full patch-policy checker and test that it rejects weakened assertions and reduced test selection.
