---
name: "ext-maestro"
description: Mirror extension that operates the Ariad method (init, adopt, overlay, doctor, update, checkpoint)
---

# Maestro Extension

Maestro is the Mirror Mind extension that operates the [Ariad](https://github.com/mirror-mind-ai/ariad) method.

Ariad is the canonical method. Maestro is how Mirror executes it: bootstrapping projects, adopting the method in existing ones, configuring local workspace overlays, diagnosing readiness for Builder Mode, comparing local instances against canonical templates, and rendering checkpoint-oriented views for Driver/Navigator work.

Use this skill when the user asks to inspect whether a project is ready for Builder Mode, adopt Ariad in a project, initialize Ariad project docs, configure Ariad locally for a journey, diagnose drift between a local Ariad instance and the canonical method, or render Ariad/Maestro checkpoint orientation.

## Contract Modes

Maestro distinguishes Ariad's method contract, repository contract, and Navigator preferences.

Ariad has opinionated Navigator preference defaults. These defaults are recommended starting behaviors, not universal laws. Advanced Navigators may override preferences such as checkpoint compression, validation strictness, documentation detail, commit frequency, or push policy.

Maestro currently supports overlay preference policies directly: repository contract, documentation update, checkpoint, validation, commit, push, worklog, documentation detail, branch, and pull request policies.

Maestro distinguishes two contract modes.

**Repository adoption** means the repository declares Ariad as part of its public agent contract. This is the mode that writes missing templates such as `AGENTS.md` and local project docs. Existing files are never overwritten.

**Workspace overlay** means Ariad guides a local Mirror journey without changing the repository contract. This is the right mode when the user wants Ariad to govern local Builder Mode conduct, but does not want to impose Ariad on every contributor to the repo.

The important boundary:

- Ariad may govern local conduct.
- Project docs should record truths about the project.
- Repository contract files (`AGENTS.md`, `CLAUDE.md`, etc.) should change only when repository adoption is explicitly desired.

## Current commands

### `checkpoint`

Renders a compact Ariad/Maestro checkpoint orientation view from explicit input:

```bash
uv run python -m memory ext maestro checkpoint \
  --journey <slug> \
  --checkpoint validate \
  --story "S2 Checkpoint Command" \
  --automated "Automated checks:passed:tests passed" \
  --manual "Manual validation:not_run" \
  --recommended-next "Prepare the manual smoke route."
```

The command is intentionally explicit. It does not infer roadmap, validation, coherence, or release state without evidence.

### `status`

Checks whether Maestro is installed coherently and whether an optional journey or project is ready:

```bash
uv run python -m memory ext maestro status --journey <slug>
```

Use this as the final getting-started check after cloning/updating Mirror, Ariad, and Mirror Extensions, reinstalling Maestro, and running migrations. A healthy result ends with `Status: ready`.

If `status` reports `Installed copy: stale installed files`, remove the installed extension directory and reinstall Maestro from the source clone.

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
  --checkpoint-policy compressed_for_trivial \
  --commit-policy after_any_codebase_change \
  --push-policy epic_boundary
```

The context provider reads overlay properties every time Mirror context is loaded, so changes are reflected on the next `memory build load <slug>` or Mirror Mode load.

### `update`

Compares a local Ariad instance with canonical templates:

```bash
uv run python -m memory ext maestro update --journey <slug>
```

The command is report-only. It does not overwrite or merge files.

Use the output as a guided drift review. Missing files can be handled through `adopt --dry-run` and then `adopt` after Navigator approval. Different files should be reconciled by Driver/Navigator review, preserving local project truth by default. Local-only Ariad files should stay local unless the idea is generalizable enough to promote into Ariad itself.

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

When the user asks whether Maestro is installed correctly, whether onboarding finished cleanly, or what command closes the getting-started loop, use `status`.

When the user asks for local Ariad behavior without imposing Ariad on the repo, prefer `overlay`, not `adopt`.

When the user states a personal process habit, treat it as a Navigator preference unless they explicitly say it is a repository rule. Examples: commit frequency, push frequency, checkpoint compression, worklog detail, branch habits, and pull request habits.
