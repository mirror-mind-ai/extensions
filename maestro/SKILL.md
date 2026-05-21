---
name: "ext-maestro"
description: Mirror extension that operates the Ariad method (init, adopt, overlay, doctor, update)
---

# Maestro Extension

Maestro is the Mirror Mind extension that operates the [Ariad](https://github.com/mirror-mind-ai/ariad) method.

Ariad is the canonical method. Maestro is how Mirror executes it: bootstrapping projects, adopting the method in existing ones, configuring local workspace overlays, diagnosing readiness for Builder Mode, and comparing local instances against canonical templates.

Use this skill when the user asks to inspect whether a project is ready for Builder Mode, adopt Ariad in a project, initialize Ariad project docs, configure Ariad locally for a journey, or diagnose drift between a local Ariad instance and the canonical method.

## Contract Modes

Maestro distinguishes two contract modes.

**Repository adoption** means the repository declares Ariad as part of its public agent contract. This is the mode that writes missing templates such as `AGENTS.md` and local project docs. Existing files are never overwritten.

**Workspace overlay** means Ariad guides a local Mirror journey without changing the repository contract. This is the right mode when the user wants Ariad to govern local Builder Mode conduct, but does not want to impose Ariad on every contributor to the repo.

The important boundary:

- Ariad may govern local conduct.
- Project docs should record truths about the project.
- Repository contract files (`AGENTS.md`, `CLAUDE.md`, etc.) should change only when repository adoption is explicitly desired.

## Current commands

### `init`

Initializes a project with the canonical Ariad templates:

```bash
uv run python -m memory ext maestro init --project-path /path/to/new-project
```

Use `--dry-run` to preview. Existing files are preserved.

### `adopt`

Adopts Ariad at the repository level by comparing a target project with canonical Ariad templates:

```bash
uv run python -m memory ext maestro adopt \
  --journey <slug> \
  --ariad-root /path/to/ariad \
  --dry-run
```

Without `--dry-run`, the command copies only missing files. Existing files are never overwritten. With `--dry-run`, it reports what it would create and what it would preserve without writing files.

If `--ariad-root` is omitted, the command resolves the canonical repository from `ARIAD_ROOT`, then `~/ariad`.

### `overlay`

Configures Ariad as a local workspace overlay for a Mirror journey, without modifying the target repository:

```bash
uv run python -m memory ext maestro overlay enable \
  --journey <slug> \
  --ariad-root /path/to/ariad
```

Bind the context capability so Builder Mode receives the overlay:

```bash
uv run python -m memory ext maestro bind ariad_workspace --journey <slug>
```

Check status:

```bash
uv run python -m memory ext maestro overlay status --journey <slug>
```

Change behavior immediately for future context loads:

```bash
uv run python -m memory ext maestro overlay set \
  --journey <slug> \
  --repo-contract-policy ask_before_change \
  --checkpoint-policy compressed_for_trivial
```

The context provider reads overlay properties every time Mirror context is loaded, so changes are reflected on the next `memory build load <slug>` or Mirror Mode load.

### `update`

Compares a local Ariad instance with canonical templates:

```bash
uv run python -m memory ext maestro update --journey <slug>
```

The command is report-only. It does not overwrite or merge files.

### `doctor`

Checks both Ariad dimensions for a project or journey:

```bash
uv run python -m memory ext maestro doctor --journey <slug>
```

It reports:

- repository adoption: whether the project has a local Ariad instance in its files;
- workspace overlay: whether the journey has a local Ariad overlay configured and bound.

Possible statuses:

- `ready`: repository adoption is complete;
- `workspace overlay`: Ariad is active locally through Maestro context;
- `canonical`: target is the Ariad canonical repo;
- `not ready`: neither adoption nor active overlay exists.

## Driver behavior

The command layer provides deterministic inspection and configuration. The Driver remains responsible for reading the project, interpreting the result, proposing reconciliation, and stopping for Navigator review before editing meaningful project content.

When the user asks for local Ariad behavior without imposing Ariad on the repo, prefer `overlay`, not `adopt`.
