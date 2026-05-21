# Project Briefing

Maestro is the Mirror Mind extension that operates the Ariad method.

Ariad is the canonical method for human-agent software development. Maestro is the Mirror runtime implementation that makes Ariad operational inside projects and journeys.

## Purpose

Maestro exists to make Ariad adoption repeatable inside Mirror Mind.

It gives a Mirror user deterministic commands for:

- diagnosing whether a project has a local Ariad instance;
- initializing new Ariad-ready projects;
- adopting Ariad in existing projects without overwriting local files;
- comparing local Ariad instances against canonical templates.

The extension should reduce adoption friction without hiding the method. The user should still understand that Ariad is the method and Maestro is the operator.

## Current State

The first operational slice is implemented and published in the `mirror-mind-ai/extensions` monorepo.

Implemented commands:

- `doctor` — readiness check for projects and journeys;
- `init` — safe project initialization from Ariad templates;
- `adopt` — safe adoption into existing projects, with `--dry-run`;
- `update` — report-only comparison against canonical templates.

The extension has been validated against real projects: Conjunto, Mirror Mind, Maestro itself, and the Diário/Raphael pilot.

## Architecture Premises

- Maestro is a Mirror extension, not a standalone CLI.
- Ariad canonical templates live outside this repository, normally resolved from `--ariad-root`, `ARIAD_ROOT`, or `~/ariad`.
- Target projects are resolved from `--project-path` or from Mirror journey metadata via `--journey`.
- Existing project files must not be overwritten by adoption commands.
- The extension lives inside the monorepo at `maestro/`, with source under `maestro/src/` and tests under `maestro/tests/`.

## Product Premises

Maestro serves people using Mirror Mind Builder Mode who want to adopt Ariad in real projects.

Its behavior should be:

- safe by default;
- explicit about what it will write;
- readable for humans;
- deterministic where possible;
- deferential to local project docs when they already exist.

## Constraints

- Do not vendor canonical Ariad docs into consumer projects.
- Do not overwrite existing project documentation.
- Keep Ariad and Maestro conceptually separate: Ariad is method, Maestro is Mirror implementation.
- Preserve compatibility with Mirror extension loading and validation.
- Avoid introducing user-specific pilot data into the public extension repository.

## Operating Notes

Run tests from the Mirror Mind repository with Mirror's source on `PYTHONPATH`:

```bash
cd /Users/alissonvale/mirror
PYTHONPATH=/Users/alissonvale/mirror/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Validate the extension monorepo when extension metadata changes:

```bash
cd /Users/alissonvale/mirror
uv run python -m memory extensions validate --extensions-root /Users/alissonvale/Code/mirror-extensions
```

Useful smoke checks:

```bash
cd /Users/alissonvale/mirror
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro doctor --journey maestro
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro adopt --journey maestro --dry-run
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro update --journey maestro
```

## Glossary

- **Ariad** — canonical method and template repository.
- **Maestro** — Mirror extension that operates Ariad.
- **Local Ariad instance** — the `AGENTS.md` and project docs installed into a consumer project.
- **Canonical templates** — templates under `docs/project-templates/` in the Ariad repository.
