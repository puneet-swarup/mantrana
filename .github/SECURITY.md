# Security Policy

## Reporting a vulnerability

Please do not open a public issue for security problems. Instead, use GitHub's
private vulnerability reporting (Security tab, "Report a vulnerability") or
email the maintainer. We aim to acknowledge reports within a few days.

## Supported versions

Mantrana is pre-1.0. Only the `main` branch is supported.

## Automated scanning

This repository uses **GitHub CodeQL default setup** for static analysis of
Python. Default setup runs automatically on pushes to the default branch and
on pull requests, and is configured in the repository settings under
Settings, Code security, Code scanning.

### Why not an advanced (workflow) setup?

CodeQL rejects a repository that has *both* default setup and an advanced
workflow enabled, with the error:

> CodeQL analyses from advanced configurations cannot be processed when the
> default setup is enabled

We therefore do not ship a `codeql` job in `.github/workflows/`. If you need
advanced setup instead (custom queries, extra languages, or a bespoke
schedule), disable default setup in repository settings first, then add a
workflow based on `github/codeql-action/init` and `github/codeql-action/analyze`.
