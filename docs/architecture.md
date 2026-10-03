# Architecture

Mantrana is an orchestration framework for **multi-agent deliberation**. A moderator model reads a shared conversation log and dynamically decides which role speaks next. This document explains how the pieces fit together.

## Design principle

> **Structure is code, behavior is config.**

If changing behavior requires editing Python, it belongs in a config file instead. The Python layer defines *how* the council runs. YAML and Markdown define *what* it runs: which roles exist, which model backs each role, which invariants are enforced, and what each role is told.

No model names, prompts, or DOM selectors appear in `src/mantrana/`.

## Component map

    main.py                 loads config, builds clients, calls run_council()
        |
        v
    orchestrator.py         the council loop - pure structure
        |
        +--> router.py       @NAME / start / final / invariants
        +--> agents.py       ChatAgent, ToolAgent
        +--> log.py          pinned entries, trimmed render
        +--> clients/        ModelClient protocol (external seam)

The council loop lives entirely in run_council() in orchestrator.py. It proceeds in three stages.

### 1. Bootstrap

The problem statement and the full role catalog are pinned to the log. Pinned entries are never trimmed.

The moderator is asked, via the bootstrap phase prompt, to select an opening panel of 3-5 roles using a start block of @NAME tags.

router.parse_start() extracts the tags. router.enforce_invariants() then unions those picks with any roles that must be present. Each selected role is invoked in order.

### 2. Route rounds

For each subsequent round the moderator reads the updated log and replies with either a routing line (an @NAME tag plus a question) or a final synthesis wrapped in final tags.

If the reply contains a final block, the loop ends and returns the synthesis. If it routes to @CODER, the council phase ends and control passes to the tool-calling phase (Phase 2). Otherwise each targeted role is invoked in turn.

### 3. Forced synthesis

If the round budget (loop.max_rounds) or turn budget (loop.max_turns) is exhausted before the moderator closes, the orchestrator appends a SYSTEM entry and asks the moderator one final time for a synthesis.

The council always terminates with a synthesis.

## Invariants

The moderator has judgment, but it is not trusted blindly. config/council.yaml defines invariants the router enforces on top of the moderator's choices.

- always_include: roles that must appear in every opening panel (e.g. CRITIC).
- per_domain: keyword-triggered rules. If the problem text matches any keyword, the listed roles are forced in (e.g. loan/payment/kyc implies COMPLIANCE).

This keeps structural guarantees in config while letting the moderator adapt the panel to the problem.

## The conversation log

log.py is the single source of truth for the session. Two kinds of entry:

- Pinned: the role catalog and the problem statement. Always rendered.
- Unpinned: moderator lines and agent responses. Trimmed to the most recent loop.log_trim_after entries when rendered.

render() shows everything (used for the final printed log). render_trimmed() is what gets fed to models, keeping prompts bounded while preserving the pinned context.

## The model seam

The entire dependency on an external model is one protocol:

    class ModelClient(Protocol):
        async def query(self, prompt: str) -> str: ...
        async def is_available(self) -> bool: ...
        async def close(self) -> None: ...

Phase 0 ships FakeClient, which returns scripted responses with no network access. This lets the whole loop be tested deterministically.

Later phases add real implementations behind the same protocol:

- Phase 1: an HTTP client (Google AI Studio free tier).
- Phase 2: a browser client driving DeepSeek/ChatGPT/Gemini via Playwright, consistent with config/sites selectors.

Because the orchestrator only depends on the protocol, no orchestration code changes when a real client is plugged in.

## Configuration

- config/council.yaml: roles, models, loop budget, invariants, alarms
- config/models.yaml: role to model binding (client kind + site)

- config/sites/*.yaml: per-site DOM selectors and streaming rules
- prompts/moderator.md: the moderator protocol
- prompts/role_catalog.md: the full panel shown to the moderator
- prompts/roles/*.md: one mandate per role

config.py loads council.yaml into Pydantic models and reads prompt files from disk. Adding a role is adding a Markdown file and a YAML stanza, with no Python changes.

## What lives where

- Loop control, phase transitions: orchestrator.py
- Protocol parsing, invariant enforcement: router.py
- Agent behavior, prompt assembly: agents.py
- Log storage, pinning, trimming: log.py

- Config schema and loading: config.py
- External model I/O: clients/
- Behavior (roles, models, prompts): config/, prompts/
