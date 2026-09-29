<div align="center">

# Mantrana

### मंत्रणा · _deliberation, counsel_

**A council of AI agents with moderator-driven dynamic routing.**

Multiple LLMs debate a problem from distinct roles — SME, Architect, Critic,
Compliance, Coder — guided by a moderator that decides who speaks next.

[![CI](https://github.com/puneet-swarup/mantrana/actions/workflows/ci.yml/badge.svg)](https://github.com/puneet-swarup/mantrana/actions/workflows/ci.yml)
[![CodeQL](https://github.com/puneet-swarup/mantrana/actions/workflows/security.yml/badge.svg)](https://github.com/puneet-swarup/mantrana/actions/workflows/security.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Status: Phase 0](https://img.shields.io/badge/status-phase%200%20·%20skeleton-yellow)](docs/phases.md)

</div>

---

## What is Mantrana?

Mantrana is an orchestration framework for **multi-agent deliberation**. It
routes a problem through a panel of AI roles where a moderator model reads
the conversation log and **dynamically decides who speaks next**.

Unlike batch multi-agent systems that collect independent opinions and merge
them once, Mantrana is **iterative**. Each agent sees the full conversation.
The moderator adapts the panel as the problem evolves. Roles can be invoked,
dropped, and re-invoked based on what the discussion reveals.

The name comes from Sanskrit — मंत्रणा, "deliberation" or "counsel" — a body
of advisors reasoning together toward a conclusion.

---

## Why?

Modern LLMs are strong individually but blind to their own framing. Ask one
model to design a loan system and it may never raise regulatory reporting
until you ask. Ask a different model the same question and you get a different
blind spot.

Mantrana makes the framing **explicit and reviewable**. A moderator reads the
problem, seeds a panel of roles with distinct mandates, and routes the
discussion. Every invocation is logged. Every role has permission to disagree.
The result is a design that has been challenged from multiple angles before
a single line of code is written.

It runs on **free web LLMs** via browser automation — no API keys, no
subscription, no per-token cost.

---

## How it works
```
┌─────────────────────────────────────────────────────────────┐
│ Moderator (any model) │
│ - reads the log │
│ - picks the next speaker │
│ - decides when the council is done │
└──────────────────────────┬──────────────────────────────────┘
│ @NAME routing
▼
┌─────────────────────────────────────────────────────────────┐
│ Council Orchestrator (Python) │
│ - shared conversation log │
│ - role dispatch │
│ - invariant enforcement │
│ - config-driven: no model names in code │
└──────────┬──────────────────────────┬───────────────────────┘
│ │
▼ ▼
┌─────────────────────┐ ┌─────────────────────────┐
│ Chat Agents │ │ Tool Agents │
│ SME · ARCHITECT │ │ CODER │
│ CRITIC · COMPLIANCE│ │ (file I/O, shell, │
│ ADVOCATE · PM │ │ alarms via MCP) │
└─────────────────────┘ └─────────────────────────┘
```


**The loop, in one pass:**

1. The **problem statement** is pinned to the log.
2. The **moderator** reads the catalog of available roles and emits a
   `<start>` block selecting 3–5 roles to begin with.
3. Each selected role **responds** with a bounded message (≤150 words).
4. The moderator reads the updated log and emits `@NAME` for the next
   speaker, or `<final>` to close the session.
5. If the moderator selects **@CODER**, the council phase ends and a
   tool-calling loop begins (file writes, shell commands, alarms).

The moderator has **full visibility** of the role catalog. It is not handed
a shortlist. Quality of deliberation depends on the moderator knowing what
panel is available.

---

## Role catalog

Mantrana ships with **~35 named roles** plus **3 parametric patterns**,
organized by mandate:

| Group | Roles |
|---|---|
| **Core** | SME, Architect, Coder, Critic, PM, Compliance, Advocate |
| **Technical** | Security, Performance, Data, QA, Platform, Integration |
| **Commercial** | Finance, Sales, Marketing, Operations, Support |
| **Governance** | Legal, Privacy, Ethics, Risk |
| **Experience** | UX, Visual, Content, Accessibility, Localization |
| **Adversarial** | RedTeam, Competitor, Regulator |
| **Strategic** | Researcher, Futurist, Systems, Historian |
| **Parametric** | `@SME-{domain}`, `@REGION-{geo}`, `@INDUSTRY-{vertical}` |

Roles are defined by **prompt files**, not code. Adding a role is adding a
markdown file.

---

## Roadmap

| Phase | Status | What |
|:---:|:---:|---|
| **0** | ✅ **Done** | Orchestrator skeleton, fake client, full loop validation |
| **1** | 🔄 **Next** | Real LLM via HTTP API (Google AI Studio free tier) |
| **2** | 📋 Planned | Browser automation (Playwright), calibration, health checks |
| **3** | 📋 Planned | Multi-model diversity — Qwen, Gemini, Claude |
| **4** | 📋 Planned | Codex-like features — file tree, diff view, plan mode |

See [`docs/phases.md`](docs/phases.md) for details on each phase.

---

## Quick start

**Phase 0 runs with fake clients** — no browser, no LLM, no API keys.
Full council loop executes in under a second.

```bash
git clone https://github.com/puneet-swarup/mantrana.git
cd mantrana

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"

# Run the council with canned responses
python main.py

# Run the test suite
pytest -v
```

Expected output:
```
======================================================================
COUNCIL LOG
======================================================================
[CATALOG]: # ROLE CATALOG ...
[PROBLEM]: Design a loan management system with audit trail.
[MODERATOR]: <start>
@ARCHITECT — design the system
@CRITIC — challenge the design
</start>
[ARCHITECT]: ARCHITECT: Separate domain into three aggregates...
[CRITIC]: CRITIC: Event sourcing adds replay cost...
[MODERATOR]: @SME — what are the domain invariants I should not get wrong?
[SME]: SME: Invariants — each transaction is atomic...
[MODERATOR]: <final>Council converged on a modular, event-sourced design...
======================================================================
```
## Project layout
```text
mantrana/
├── config/              # Everything configurable lives here
│   ├── council.yaml     # Roles, loop budget, invariants
│   ├── models.yaml      # Role → model binding
│   └── sites/           # Browser DOM selectors per site
├── prompts/             # Role mandates and moderator protocol
│   ├── role_catalog.md
│   ├── moderator.md
│   └── roles/
├── src/mantrana/        # Orchestration code — no model names, no prompts
│   ├── config.py        # Config loader (Pydantic)
│   ├── log.py           # Shared conversation log
│   ├── router.py        # @NAME parsing, invariant enforcement
│   ├── agents.py        # ChatAgent, ToolAgent
│   ├── orchestrator.py  # The council loop
│   └── clients/         # ModelClient protocol + implementations
├── tests/               # Unit tests
├── docs/                # Architecture, phases, ADRs
└── main.py              # Entry point
```
## Design principles
1. **Structure is code, behavior is config.**

    If changing behavior requires editing Python, it's in the wrong place.

2. **Prove logic on fakes. Then plug in reality.**
    
    Phase 0 validates the loop with canned responses before any external
dependency enters the system.

3. **Moderator has full panel visibility.**

    No shortlisting. Quality of role selection depends on seeing all options.

4. **Adopt the commodity, build the unique.**

    MCP for tool protocols. Pre-built servers for file I/O and browser
automation. Custom logic only for council orchestration.

5. **Transparency over autonomy.**

    Every agent invocation is injected into the visible chat window. The
human can interrupt, correct, or redirect at any turn.

## Engineering practices
- CI: lint (ruff), type-check (mypy), test matrix (Python 3.10–3.12)

- Security: CodeQL static analysis, secret scanning with push protection,
Dependabot alerts, dependency review on every PR

- Governance: branch ruleset on main, CODEOWNERS, PR templates,
structured issue forms, Conventional Commits

- Testing: unit tests for router, log, orchestrator; deterministic
fake clients for the model layer

## Documentation
- [Architecture](docs/architecture.md) — how the pieces fit together
- [Phases](docs/phases.md) — roadmap and current status
- [Contributing](contributing.md) — setup, commit conventions, PR process
- [Security Policy](.github/SECURITY.md) — vulnerability disclosure
- [Changelog](changelog.md) — release history

## Contributing
Contributions are welcome. Please read [CONTRIBUTING.md](contributing.md)
and the [Code of Conduct](code_of_conduct.md) before opening a PR.

Good first issues are tagged good first issue.
Issues are grouped by phase — pick the phase that matches your interest.

## License
Licensed under the Apache License, Version 2.0.

The patent grant clause matters for AI infrastructure. Use it freely,
including commercially.

<div align="center">
मंत्रणा · A body of advisors reasoning together toward a conclusion.

</div> ```