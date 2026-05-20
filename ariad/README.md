# Ariad Extension

Ariad project adoption and readiness tooling for Mirror Mind.

This extension turns the manual Ariad adoption path into an operational Mirror capability. The first slice is deliberately read-only: it checks whether a target project has the minimum local Ariad surface needed for Builder Mode.

## Commands

### `doctor`

```bash
uv run python -m memory ext ariad doctor --project-path /path/to/project
```

Checks for:

- `AGENTS.md` exists and mentions Ariad
- `docs/process/development-guide.md`
- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/index.md`
- `docs/product/principles.md`

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

First slice complete: read-only readiness check.

Planned later:

- `init` — create a new Ariad-ready project
- `adopt` — adopt Ariad in an existing project without blind overwrite
- `update` — reconcile local Ariad instance with the canonical method
