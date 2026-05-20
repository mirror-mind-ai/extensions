# Ariad Extension

Ariad project adoption and readiness tooling for Mirror Mind.

This extension turns the manual Ariad adoption path into an operational Mirror capability. The first slice is deliberately read-only: it checks whether a target project has the minimum local Ariad surface needed for Builder Mode.

## Commands

### `adopt`

```bash
uv run python -m memory ext ariad adopt \
  --project-path /path/to/project \
  --ariad-root /path/to/ariad
```

If `--ariad-root` is omitted, the command resolves the canonical repository from `ARIAD_ROOT`, then `~/ariad`.

Or by journey:

```bash
uv run python -m memory ext ariad adopt \
  --journey diario \
  --ariad-root /path/to/ariad
```

Preview without writing:

```bash
uv run python -m memory ext ariad adopt \
  --journey diario \
  --ariad-root /path/to/ariad \
  --dry-run
```

Adopts Ariad by comparing the target project with canonical templates under:

```text
<ariad-root>/docs/project-templates/
```

In write mode, the command copies only missing templates. Existing files are never overwritten. With `--dry-run`, it reports what it would create and what it would preserve without writing files.

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

- `doctor` — read-only readiness check with `adopt --dry-run` next-step guidance
- `adopt` — copy missing templates without overwriting existing files
- `adopt --dry-run` — read-only adoption plan

Planned later:

- `init` — create a new Ariad-ready project
- `adopt` reconciliation mode — help merge/adapt existing local docs
- `update` — reconcile local Ariad instance with the canonical method
