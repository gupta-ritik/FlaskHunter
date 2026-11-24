# Architecture decisions

**Status.** These ADRs describe proposed v1 and v1.1 decisions. **VERIFIED** marks documented capabilities. **ASSUMPTION** marks a tradeoff still to validate. **PLAN** marks intended work.

## ADR-001 · Use LangGraph for the investigation state machine

| Item | Record |
| --- | --- |
| Context | Experiments repeat until evidence or budget permits a terminal decision. Judges need to trace each branch back to inputs and results. **VERIFIED:** LangGraph supports typed state and conditional edges. [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) |
| Decision | **PLAN:** Define a Pydantic investigation state and explicit conditional edges for execution, abstention, verification, and publication. Test routing with fake nodes. |
| Alternatives | Plain Python state machine with an explicit loop. Linear workflow with an embedded retry loop. |
| Consequences | **ASSUMPTION:** Explicit transitions make branching easier to inspect and test. LangGraph adds a dependency and schema integration work. Export traces independently so orchestration can be revisited if it consumes the demo budget. |

## ADR-002 · Benchmark two local coder models through Ollama

| Item | Record |
| --- | --- |
| Context | The target is a laptop with an RTX 5050 and 8 GB VRAM. **VERIFIED:** Ollama offers local coder models. [Ollama coder model example](https://ollama.com/library/qwen2.5-coder:7b) |
| Decision | **PLAN.** Benchmark two candidate coder models that fit 8 GB VRAM behind `LLMClient`. Limit them to hypothesis ranking and patch drafting. Use the same cases, context and request budgets, and verification gate. Choose by gate pass rate, using latency to break ties. Score the rules-only path separately. |
| Alternatives | Hosted model, one local model, or rules only. |
| Consequences | **ASSUMPTION.** Two candidates fit the device budget and at least one yields a verified patch within budget. Measure peak VRAM, latency, gate pass rate, and draft rejection reasons. Use rules-only diagnosis and quarantine-only publishing when no patch passes the gate. |

## ADR-003 · Execute pytest in a Docker sandbox

| Item | Record |
| --- | --- |
| Context | Replaying tests executes repository code. **VERIFIED.** Docker's none driver provides loopback-only networking. Docker Desktop supports a WSL 2 backend for Linux containers on Windows. [Docker none network](https://docs.docker.com/engine/network/drivers/none/) · [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) |
| Decision | **PLAN.** v1 uses `--network=none`, a non-root, resource-limited container, and an ephemeral checkout with no secrets or Docker socket. Use loopback only for the runner-owned network stub. Keep the PR step and model outside the sandbox. v1.1 pins the sandbox image by digest. |
| Alternatives | Host subprocess with a clean environment, or a disposable VM per job. |
| Consequences | **ASSUMPTION.** Docker Desktop with WSL 2 works on the reference Windows laptop. **PLAN.** Verify the backend, Linux container startup, and a smoke run without a default route on Day 1. If blocked, use a Linux runner for sandbox work while the fixture-based Week 1 slice proceeds. Verify no egress or credentials at runtime. |

## ADR-004 · Require an observed reproduction and 50 stress passes

| Item | Record |
| --- | --- |
| Context | A patch can appear to work when the trigger did not occur or the test never ran. **VERIFIED:** Empirical Python flakiness research found that many repeats can be needed to observe failures. [Python flakiness study](https://arxiv.org/abs/2101.09077) |
| Decision | **PLAN.** v1 requires matching base failures, passing controls, 50 passing predeclared candidate stress runs with the target executed, and a passing relevant suite. Record the exact candidate and runner results in the same workflow run. Route unsuccessful or incomplete verification to quarantine review. v1.1 adds receipt digests and a full patch-policy checker. |
| Alternatives | One suite pass, adaptive sampling, or deterministic reproduction only. |
| Consequences | **ASSUMPTION:** The fixed stress budget gives usable evidence within ten minutes for the benchmark. Rare flakes may survive. Report the sampled conditions, elapsed time, and outcomes for human review. |

## ADR-005 · Deliver through GitHub Actions

| Item | Record |
| --- | --- |
| Context | GitHub Actions is the v1 history source and CI surface. **VERIFIED:** Its REST API exposes artifacts and workflows can run on a schedule. [Artifacts API](https://docs.github.com/en/rest/actions/artifacts) · [Schedule event](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) |
| Decision | **PLAN.** v1 ships a versioned Action wrapping the Python CLI, read-only scheduled and PR evaluations, dry-run reports, and opt-in draft fix and quarantine PRs. Only the PR step receives the publish token. Publish the CLI as a separately installable package. v1.1 moves publishing to a separate trusted job. |
| Alternatives | Local CLI only, hosted GitHub App service, or self-hosted scheduler. |
| Consequences | **ASSUMPTION:** Actions provides enough retained history and test artifacts for early adopters. Document the data contract and token scopes. Use local history fixtures and dry-run reports when artifacts or publishing access are unavailable. |
