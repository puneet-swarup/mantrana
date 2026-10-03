# Changelog

All notable changes to Mantrana are documented here. Format follows Keep a Changelog. Versioning follows Semantic Versioning.

## [Unreleased]

### Added
- Architecture, phases, and changelog documentation.
- mkdocs configuration for the documentation site.


## [0.0.1] - 2026-10-03

### Added
- Council orchestrator loop with bootstrap, route rounds, and forced synthesis.
- Router for the moderator protocol (@NAME, start and final blocks) with invariant enforcement.

- Shared conversation log with pinning and trimming.
- ChatAgent and ToolAgent, model-agnostic.
- FakeClient for deterministic, dependency-free runs.
- Config loader (Pydantic) and YAML-driven role/model/invariant definitions.

- Role catalog and per-role mandate prompts.
- Unit tests for router, log, and orchestrator.
