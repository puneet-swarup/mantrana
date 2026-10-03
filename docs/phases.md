# Phases

Mantrana is built in phases. Each phase is independently testable and leaves the system runnable. The guiding rule: prove logic on fakes, then plug in reality.

| Phase | Status | What |
|:---:|:---:|---|
| 0 | Done | Orchestrator skeleton, fake client, full loop validation |
| 1 | Next | Real LLM via HTTP API |
| 2 | Planned | Browser automation, calibration, health checks, CODER tool loop |

| 3 | Planned | Multi-model diversity: Qwen, Gemini, Claude |
| 4 | Planned | Codex-like features: file tree, diff view, plan mode |

## Phase 0: Skeleton (Done)

Goal: validate the full council loop with zero external dependencies.

- Shared conversation log with pinning and trimming.
- Router that parses the moderator protocol and enforces invariants.

- ChatAgent and ToolAgent, both model-agnostic.
- Orchestrator running bootstrap, route rounds, and forced synthesis.
- FakeClient returning scripted responses, so the loop runs in under a second with no network.

Exit criteria met: python main.py prints a full council log and a synthesis; the unit tests for router, log, and orchestrator pass.

## Phase 1: Real LLM via HTTP (Next)

Goal: replace FakeClient with a real model behind the same ModelClient protocol.

- An HTTPModelClient using a free-tier API (e.g. Google AI Studio).
- A client factory that reads config/models.yaml and maps model names to client classes.
- Wiring so role-to-model bindings in YAML are actually honored.

Exit criteria: the council runs end-to-end against a real model with no changes to orchestrator.py.

## Phase 2: Browser Automation and CODER (Planned)

Goal: run on free web LLMs with no API key, and make @CODER real.

- A BrowserModelClient driving DeepSeek/ChatGPT/Gemini via Playwright, using config/sites selectors.
- Streaming stability detection (stable_interval_ms, stable_checks) so responses are read when complete.
- Selector health checks and calibration to survive DOM drift.

- The CODER tool loop: parse tool_call blocks from the model, dispatch to a tool registry (write_file, read_file, run_shell, raise_alarm), loop until a final block.

Exit criteria: the council deliberates on free web LLMs; @CODER writes files and runs commands for real.

## Phase 3: Multi-Model Diversity (Planned)

Goal: bind different roles to different models so the council is diverse by construction.

- Add adapters for Qwen, Gemini, and Claude.
- Route each role to a model via config/models.yaml.

- Optional per-role fallback models when a primary is unavailable.

Exit criteria: a single council run spans at least two distinct model backends.

## Phase 4: Codex-like Features (Planned)

Goal: a richer operator experience around the council.

- A file tree and diff view for CODER edits.
- A plan mode where the council drafts a plan before execution.
- Session replay from the pinned and unpinned log.

Exit criteria: a human can watch, inspect, and steer a council session turn by turn.

## Phase summary

Phase 0 proves the loop. Phase 1 proves the seam. Phase 2 removes the API key and makes the coder real.

Phases 3 and 4 add diversity and ergonomics. Each phase keeps the previous phases green.