# Maestro Extension

Maestro is the Mirror extension that operates the [Ariad](https://github.com/mirror-mind-ai/ariad) method.

Ariad is a method for integral agentic development: human-agent development that keeps the work whole over time. Maestro is how Mirror Mind executes that method. The method lives in its own canonical repository; this extension turns it into operational Mirror capabilities.

## Commands

### `init`

```bash
uv run python -m memory ext maestro init \
  --project-path /path/to/new-project
```

Initializes a project with the canonical Ariad templates. If the target directory does not exist, it is created. Existing files are preserved. Use `--dry-run` to preview without writing.

### `adopt`

```bash
uv run python -m memory ext maestro adopt \
  --project-path /path/to/project \
  --ariad-root /path/to/ariad
```

If `--ariad-root` is omitted, the command resolves the canonical repository from `ARIAD_ROOT`, then `~/ariad`.

Or by journey:

```bash
uv run python -m memory ext maestro adopt \
  --journey diario \
  --ariad-root /path/to/ariad
```

Preview without writing:

```bash
uv run python -m memory ext maestro adopt \
  --journey diario \
  --ariad-root /path/to/ariad \
  --dry-run
```

Adopts the Ariad method by comparing the target project with canonical templates under:

```text
<ariad-root>/docs/project-templates/
```

In write mode, the command copies only missing templates. Existing files are never overwritten. With `--dry-run`, it reports what it would create and what it would preserve without writing files.

### `doctor`

```bash
uv run python -m memory ext maestro doctor --project-path /path/to/project
```

Or resolve the project from a Mirror journey's `project_path`:

```bash
uv run python -m memory ext maestro doctor --journey diario
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

The command is read-only. It reports readiness, missing files, and warnings. When a project exists but is not ready, it suggests the corresponding `adopt --dry-run` next step.

### `update`

```bash
uv run python -m memory ext maestro update --journey diario
```

Compares a local Ariad instance with the canonical templates. This command is report-only: it lists missing local files, files that differ from canonical, and files that are up to date. It does not overwrite or merge.

## Install

```bash
uv run python -m memory extensions install maestro \
  --extensions-root /path/to/mirror-extensions \
  --mirror-home ~/.mirror-minds/<user>
```

## Status

Implemented:

- `doctor` — read-only readiness check with `adopt --dry-run` next-step guidance
- `adopt` — copy missing templates without overwriting existing files
- `adopt --dry-run` — read-only adoption plan
- `init` — create a new Ariad-ready project safely
- `update` — report-only comparison against canonical templates

Planned later:

- `adopt` reconciliation mode — help merge/adapt existing local docs
- `update` reconciliation mode — propose safe local updates without blind overwrite

## Relationship to Ariad

| Surface | Lives in | Role |
|---|---|---|
| **Ariad** | `~/Code/ariad` (canonical repo) | The method: docs, templates, principles |
| **Maestro** | This extension | The Mirror runtime that operates the method |

Ariad does not depend on Mirror Mind. Maestro depends on both.
