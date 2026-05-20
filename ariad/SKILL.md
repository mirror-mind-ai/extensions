---
name: "ext-ariad"
description: Ariad project readiness and adoption support
---

# Ariad Extension

Use this skill when the user asks to inspect whether a project is ready for Ariad Builder Mode, adopt Ariad in a project, initialize Ariad project docs, or diagnose drift between a local Ariad instance and the canonical method.

Implemented commands are non-destructive:

```bash
uv run python -m memory ext ariad doctor --project-path /path/to/project
uv run python -m memory ext ariad adopt --project-path /path/to/project --ariad-root /path/to/ariad
uv run python -m memory ext ariad adopt --project-path /path/to/project --ariad-root /path/to/ariad --dry-run
```

If the project is connected to a Mirror journey, prefer resolving it from the journey:

```bash
uv run python -m memory ext ariad doctor --journey <slug>
```

## Current commands

### `adopt`

Adopts Ariad by comparing a target project with the canonical Ariad templates:

```bash
uv run python -m memory ext ariad adopt \
  --journey <slug> \
  --ariad-root /path/to/ariad \
  --dry-run
```

Without `--dry-run`, the command copies only missing files. Existing files are never overwritten. With `--dry-run`, it reports what it would create and what it would preserve without writing files.

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
