# Ariad Extension

Ariad project adoption and readiness tooling for Mirror Mind.

This extension turns the manual Ariad adoption path into an operational Mirror capability. The first slice is deliberately read-only: it checks whether a target project has the minimum local Ariad surface needed for Builder Mode.

## Commands

### `adopt --dry-run`

```bash
uv run python -m memory ext ariad adopt \
  --project-path /path/to/project \
  --ariad-root /path/to/ariad \
  --dry-run
```

Or by journey:

```bash
uv run python -m memory ext ariad adopt \
  --journey diario \
  --ariad-root /path/to/ariad \
  --dry-run
```

Plans adoption by comparing the target project with canonical templates under:

```text
<ariad-root>/docs/project-templates/
```

The command is read-only in this first slice. It reports what it would create and what it would not overwrite.

### `doctor`

```bash
uv run python -m memory ext ariad doctor --project-path /path/to/project
```

Or resolve the project from a Mirror journey's `project_path`:

```bash
uv run python -m memory ext ariad doctor --journey diario
```

Checks for:

- consumer projects with a local Ariad instance:
  - `AGENTS.md` exists and mentions Ariad
  - `docs/process/development-guide.md`
  - `docs/project/briefing.md`
  - `docs/project/decisions.md`
  - `docs/project/roadmap/index.md`
  - `docs/product/principles.md`
- canonical Ariad repositories, detected by method docs and project templates

Example output:

```text
Ariad readiness report

Project: /path/to/project

✅ AGENTS.md — exists and mentions Ariad
✅ docs/process/development-guide.md — exists
✅ docs/project/briefing.md — exists
✅ docs/project/decisions.md — exists
✅ docs/project/roadmap/index.md — exists
✅ docs/product/principles.md — exists

Status: ready
```

## Install

```bash
uv run python -m memory extensions install ariad \
  --extensions-root /path/to/mirror-extensions \
  --mirror-home ~/.mirror-minds/<user>
```

## Status

Implemented:

- `doctor` — read-only readiness check
- `adopt --dry-run` — read-only adoption plan

Planned later:

- `init` — create a new Ariad-ready project
- `adopt` write mode — copy missing templates without blind overwrite
- `update` — reconcile local Ariad instance with the canonical method
