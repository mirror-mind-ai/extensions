---
name: "ext-ariad"
description: Ariad project readiness and adoption support
---

# Ariad Extension

Use this skill when the user asks to inspect whether a project is ready for Ariad Builder Mode, adopt Ariad in a project, initialize Ariad project docs, or diagnose drift between a local Ariad instance and the canonical method.

The first implemented command is a non-destructive readiness check:

```bash
uv run python -m memory ext ariad doctor --project-path /path/to/project
```

## Current command

### `doctor`

Checks whether a project has the minimum local Ariad surface needed for Builder Mode:

- `AGENTS.md` exists and mentions Ariad
- `docs/process/development-guide.md` exists
- `docs/project/briefing.md` exists
- `docs/project/decisions.md` exists
- `docs/project/roadmap/index.md` exists
- `docs/product/principles.md` exists

The command is read-only. It reports readiness, missing files, and warnings.

## Driver behavior

The command layer provides deterministic inspection only. The Driver remains responsible for reading the project, interpreting the result, proposing reconciliation, and stopping for Navigator review before editing meaningful project content.
