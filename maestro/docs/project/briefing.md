# Project Briefing

Maestro is the Mirror Mind extension that operates the Ariad method.

Ariad is the canonical method for human-agent software development. Maestro is the Mirror runtime implementation that makes Ariad operational inside projects and journeys.

## Purpose

Maestro exists to make Ariad adoption, operation, and visualization repeatable inside Mirror Mind.

It gives a Mirror user deterministic commands for:

- diagnosing whether a project has a local Ariad instance or workspace overlay;
- initializing new Ariad-ready projects;
- adopting Ariad in existing projects without overwriting local files;
- comparing local Ariad instances against canonical templates;
- configuring Ariad as a local workspace overlay for a Mirror journey;
- closing install and update flows with an executable status check.

The next product arc extends this operational base into Ariad/Maestro visualization: helping the Driver and Navigator see where work is, which checkpoint is active, what evidence exists, what remains unresolved, and which next movement preserves coherence.

## Current Objective

The current objective is to consolidate the visualization learnings produced while developing Mirror Mind and implement them in Maestro as a stable product grammar.

Recent Mirror Mind self-update and release work produced a set of useful Ariad/Maestro components:

- Bird's-Eye Map for locating CV, Epic, and Story;
- Horizontal Flow Board for showing work moving across states;
- Transition View for showing the next coherent movement;
- Release Intent for making release regime explicit;
- checkpoint-specific views for plan, implementation, validation, review, coherence, and commit moments;
- Coherence Matrix for checking roadmap, docs, worklog, decisions, journey, and release notes;
- compact checkpoint sentence for naming story state and checkpoint state together;
- status and health signals for compressing runtime state into actionable indicators.

Maestro should turn these field notes into an operational surface. The goal is not decorative reporting. The goal is to make Ariad easier to navigate without hiding the Driver/Navigator method.

## Current State

The first operational slice is implemented and published in the `mirror-mind-ai/extensions` monorepo.

Implemented commands:

- `status` — end-to-end install, source clone, Ariad root, migration, and readiness check;
- `doctor` — readiness check for projects and journeys;
- `init` — safe project initialization from Ariad templates;
- `adopt` — safe adoption into existing projects, with `--dry-run`;
- `update` — report-only comparison against canonical templates;
- `overlay` — local Ariad workspace overlay for Mirror journeys.

The extension has been validated against real projects: Conjunto, Mirror Mind, Maestro itself, and the Diário/Raphael pilot.

The next slice should be discovery and consolidation of the visualization grammar before behavior expands.

## Architecture Premises

- Maestro is a Mirror extension, not a standalone CLI.
- Ariad canonical templates live outside this repository, normally resolved from `--ariad-root`, `ARIAD_ROOT`, or `~/ariad`.
- Target projects are resolved from `--project-path` or from Mirror journey metadata via `--journey`.
- Existing project files must not be overwritten by adoption commands.
- Workspace overlay is local Mirror extension state and must not imply repository adoption.
- Visualization should be derived from Ariad lifecycle state, project files, journey context, command results, or explicit user input. It should not invent project truth.
- The extension lives inside the monorepo at `maestro/`, with source under `maestro/src/` and tests under `maestro/tests/`.

## Product Premises

Maestro serves people using Mirror Mind Builder Mode who want to adopt and operate Ariad in real projects.

Its behavior should be:

- safe by default;
- explicit about what it will write;
- readable for humans;
- deterministic where possible;
- deferential to local project docs when they already exist;
- visual enough to orient the Navigator without becoming a generic dashboard;
- checkpoint-aware rather than one-size-fits-all.

## Boundaries

- Do not vendor canonical Ariad docs into consumer projects.
- Do not overwrite existing project documentation.
- Keep Ariad and Maestro conceptually separate: Ariad is method, Maestro is Mirror implementation.
- Preserve compatibility with Mirror extension loading and validation.
- Avoid introducing user-specific pilot data into the public extension repository.
- Do not move methodological authority from Ariad into Maestro. If a change defines the method itself, route it to Ariad.
- Do not implement visualization as decoration. Every component must help the Driver/Navigator decide, validate, review, or close work.

## Operating Notes

Run tests from the Mirror Mind repository with Mirror's source on `PYTHONPATH`:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Validate the extension monorepo when extension metadata changes:

```bash
cd /Users/alissonvale/Code/mirror-dev
uv run python -m memory extensions validate --extensions-root /Users/alissonvale/Code/mirror-extensions
```

Useful smoke checks:

```bash
cd /Users/alissonvale/Code/mirror-dev
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro status --journey maestro
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro doctor --journey maestro
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro adopt --journey maestro --dry-run
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro update --journey maestro
```

## Glossary

- **Ariad** — canonical method and template repository.
- **Maestro** — Mirror extension that operates Ariad.
- **Local Ariad instance** — the `AGENTS.md` and project docs installed into a consumer project.
- **Canonical templates** — templates under `docs/project-templates/` in the Ariad repository.
- **Workspace overlay** — local Mirror extension state that applies Ariad to a journey without changing repository files.
- **Visualization grammar** — the set of Ariad/Maestro views and signals that orient Driver/Navigator work across checkpoints.
