---
name: "ext-maestro"
description: Mirror extension that operates the Ariad method (init, adopt, doctor, update)
---

# Maestro Extension

Maestro is the Mirror Mind extension that operates the [Ariad](https://github.com/mirror-mind-ai/ariad) method.

Ariad is the canonical method (lives in its own repository). Maestro is how Mirror executes it: bootstrapping projects, adopting the method in existing ones, diagnosing readiness for Builder Mode, and comparing local instances against the canonical templates.

Use this skill when the user asks to inspect whether a project is ready for Builder Mode, adopt Ariad in a project, initialize Ariad project docs, or diagnose drift between a local Ariad instance and the canonical method.

Implemented commands are safe by default — they never overwrite existing files:

```bash
uv run python -m memory ext maestro doctor --project-path /path/to/project
uv run python -m memory ext maestro init --project-path /path/to/new-project
uv run python -m memory ext maestro adopt --project-path /path/to/project --ariad-root /path/to/ariad
uv run python -m memory ext maestro adopt --project-path /path/to/project --ariad-root /path/to/ariad --dry-run
uv run python -m memory ext maestro update --project-path /path/to/project
```

If the project is connected to a Mirror journey, prefer resolving it from the journey:

```bash
uv run python -m memory ext maestro doctor --journey <slug>
```

## Current commands

### `init`

Initializes a project with the canonical Ariad templates:

```bash
uv run python -m memory ext maestro init --project-path /path/to/new-project
```

Use `--dry-run` to preview. Existing files are preserved.

### `adopt`

Adopts the Ariad method by comparing a target project with the canonical Ariad templates:

```bash
uv run python -m memory ext maestro adopt \
  --journey <slug> \
  --ariad-root /path/to/ariad \
  --dry-run
```

Without `--dry-run`, the command copies only missing files. Existing files are never overwritten. With `--dry-run`, it reports what it would create and what it would preserve without writing files.

If `--ariad-root` is omitted, the command resolves the canonical repository from `ARIAD_ROOT`, then `~/ariad`.

### `update`

Compares a local Ariad instance with canonical templates:

```bash
uv run python -m memory ext maestro update --journey <slug>
```

The command is report-only. It does not overwrite or merge files.

### `doctor`

Checks whether a project has the minimum local Ariad surface needed for Builder Mode:

- `AGENTS.md` exists and mentions Ariad
- `docs/process/development-guide.md` exists
- `docs/project/briefing.md` exists
- `docs/project/decisions.md` exists
- `docs/project/roadmap/index.md` exists
- `docs/product/principles.md` exists

The command is read-only. It reports readiness, missing files, and warnings. When a project exists but is not ready, it suggests the corresponding `adopt --dry-run` next step.

## Driver behavior

The command layer provides deterministic inspection only. The Driver remains responsible for reading the project, interpreting the result, proposing reconciliation, and stopping for Navigator review before editing meaningful project content.
