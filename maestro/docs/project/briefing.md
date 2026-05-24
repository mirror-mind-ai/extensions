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
- closing install and update flows with an executable status check;
- rendering checkpoint-oriented views for Driver/Navigator work.

The completed CV2 product arc extended the operational base into Ariad/Maestro visualization: helping the Driver and Navigator see where work is, which checkpoint is active, what evidence exists, what remains unresolved, which roadmap movement just happened, and which next movement preserves coherence.

## Current Objective

The current objective is CV5 Maestro Simulation Harness and Builder Mode visual integration: exercise Maestro across synthetic and manual sandbox journeys, then make checkpoint visuals appear naturally during real Driver/Navigator work.

CV2 consolidated visualization learnings produced while developing Mirror Mind and turned them into a stable Maestro runtime surface. CV5 now creates deterministic and manual fields for dogfooding that surface safely.

Implemented visual components:

- Bird's-Eye Map for locating CV, Epic, and Story;
- Ariad Stage Ribbon for checkpoint state;
- compact checkpoint sentence for story/checkpoint orientation;
- Release Intent for known or emergent release context;
- Validation Panel for automated evidence, manual validation, blockers, and risk posture;
- Horizontal Flow Board for Backlog, Ready, Doing, Validate, and Done lanes;
- Coherence Matrix for closeout surfaces without a false global ready state;
- Roadmap Snapshot for end-of-story CV/Epic/Story orientation with progress bars.

The first implementation is intentionally explicit. It accepts CLI flags such as `--checkpoint`, `--story`, `--automated`, `--manual`, `--coherence`, `--roadmap`, and flow-card lane flags. It does not parse arbitrary roadmap Markdown and does not infer validation or coherence status without evidence.

## Current State

The first operational foundation is implemented and published in the `mirror-mind-ai/extensions` monorepo.

Implemented commands:

- `status` — end-to-end install, source clone, Ariad root, migration, and readiness check;
- `doctor` — readiness check for projects and journeys;
- `init` — safe project initialization from Ariad templates;
- `adopt` — safe adoption into existing projects, with `--dry-run`;
- `update` — report-only comparison against canonical templates;
- `overlay` — local Ariad workspace overlay for Mirror journeys;
- `checkpoint` — explicit Ariad/Maestro checkpoint view renderer.

The extension has been validated against public and private real projects, including Mirror Mind and Maestro itself. CV2 visualization work has test coverage and isolated smoke validation through temporary Mirror homes.

The current slice is Builder Mode visual integration for Maestro checkpoints. The synthetic simulation harness exists, but the manual Sandbox Pet Store test showed the important gap: Ariad lifecycle behavior can work while Maestro visuals remain invisible. The next work is making compact checkpoint visuals appear naturally in real Driver/Navigator sessions through Maestro context guidance.

## Architecture Premises

- Maestro is a Mirror extension, not a standalone CLI.
- Ariad canonical templates live outside this repository, normally resolved from `--ariad-root`, `ARIAD_ROOT`, or `~/ariad`.
- Target projects are resolved from `--project-path` or from Mirror journey metadata via `--journey`.
- Existing project files must not be overwritten by adoption commands.
- Workspace overlay is local Mirror extension state and must not imply repository adoption.
- Visualization should be derived from Ariad lifecycle state, project files, journey context, command results, or explicit user input. It should not invent project truth.
- The first visualization implementation uses explicit input over inference. Automatic parsing of arbitrary roadmap Markdown remains out of scope until the data model is justified.
- The simulation harness is a deterministic synthetic field. It may generate explicit checkpoint inputs, but it must not pretend to be evidence from a real project.
- Builder Mode integration should make Maestro visuals visible without forcing fake state. Drivers should render only explicit known state and leave unknowns unknown.
- The extension lives inside the monorepo at `maestro/`, with source under `maestro/src/` and tests under `maestro/tests/`.

## Product Premises

Maestro serves people using Mirror Mind Builder Mode who want to adopt and operate Ariad in real projects.

Its behavior should be:

- safe by default;
- explicit about what it will write or infer;
- readable for humans;
- deterministic where possible;
- deferential to local project docs when they already exist;
- visual enough to orient the Navigator without becoming a generic dashboard;
- checkpoint-aware rather than one-size-fits-all;
- honest about unknown state.

## Boundaries

- Do not vendor canonical Ariad docs into consumer projects.
- Do not overwrite existing project documentation.
- Keep Ariad and Maestro conceptually separate: Ariad is method, Maestro is Mirror implementation.
- Preserve compatibility with Mirror extension loading and validation.
- Avoid introducing user-specific pilot data into the public extension repository.
- Do not move methodological authority from Ariad into Maestro. If a change defines the method itself, route it to Ariad.
- Do not implement visualization as decoration. Every component must help the Driver/Navigator decide, validate, review, orient, or close work.
- Do not claim validation, coherence, roadmap progress, or release state without explicit evidence.

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
uv run python -m memory ext maestro simulate --story-index 0 --transcript --report
```

Checkpoint smoke example:

```bash
uv run python -m memory ext maestro checkpoint \
  --checkpoint commit \
  --story "S3 End-of-Story Integration" \
  --roadmap "cv:CV2:Ariad/Maestro Visualization:done:6/6" \
  --roadmap "epic:E6:Roadmap Snapshot:done:3/3" \
  --roadmap "story:S3:End-of-Story Integration:done"
```

## Glossary

- **Ariad** — canonical method and template repository.
- **Maestro** — Mirror extension that operates Ariad.
- **Local Ariad instance** — the `AGENTS.md` and project docs installed into a consumer project.
- **Canonical templates** — templates under `docs/project-templates/` in the Ariad repository.
- **Workspace overlay** — local Mirror extension state that applies Ariad to a journey without changing repository files.
- **Visualization grammar** — the set of Ariad/Maestro views and signals that orient Driver/Navigator work across checkpoints.
- **Roadmap Snapshot** — end-of-story CV/Epic/Story view with status markers and optional progress bars.
- **Simulation harness** — synthetic Maestro exercise surface that generates checkpoint views from public-safe fake roadmaps without mutating real projects.
