# Local Development Guide

This repository uses Ariad as its human-agent development method. This file is the local Ariad instance for the Maestro extension.

## Relationship to Ariad

Ariad is the canonical method. Maestro is the Mirror extension that operates Ariad.

When canonical Ariad guidance and this local guide differ, follow this local guide for extension-specific work and surface the difference during the coherence check.

## Driver and Navigator

The agent is the **Driver**. The human is the **Navigator**.

The Driver should read the local project docs before meaningful work, propose a plan, implement narrowly, run tests, prepare validation, update docs, and stop at checkpoints.

The Navigator holds product judgment: what Maestro should automate, what should remain explicit, and which adoption friction is worth solving.

## Project Commands

Run Maestro tests from the Mirror Mind repository so imports resolve against the current Mirror source:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Validate the extension monorepo after metadata, skill, or runtime changes:

```bash
cd /Users/alissonvale/Code/mirror-dev
uv run python -m memory extensions validate --extensions-root /Users/alissonvale/Code/mirror-extensions
```

After Pi extension changes, reload Pi and smoke the runtime control surface:

```text
/reload
/maestro status
/maestro off
/maestro on sandbox-pet-store
```

Expected status-line states are `♪ Maestro · on` and `♪ Maestro · off`.

Smoke-test readiness, adoption, overlay, and visualization flows:

```bash
cd /Users/alissonvale/Code/mirror-dev
ARIAD_ROOT=/Users/alissonvale/Code/ariad \
MIRROR_EXTENSIONS_ROOT=/Users/alissonvale/Code/mirror-extensions \
uv run python -m memory ext maestro status --journey maestro
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro doctor --journey maestro
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro adopt --journey maestro --dry-run
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro update --journey maestro
uv run python -m memory ext maestro overlay status --journey mirror-mind
uv run python -m memory ext maestro checkpoint \
  --checkpoint commit \
  --story "S3 End-of-Story Integration" \
  --roadmap "cv:CV2:Ariad/Maestro Visualization:done:6/6" \
  --roadmap "epic:E6:Roadmap Snapshot:done:3/3" \
  --roadmap "story:S3:End-of-Story Integration:done"
uv run python -m memory ext maestro simulate --story-index 0 --transcript --report
```

## Verification

For behavior changes, automated tests are required.

For command output changes, include at least one manual validation route showing:

- command invoked;
- target project or journey;
- expected status/output;
- whether files should or should not be written.

For adoption behavior, validate both dry-run and write mode when practical. Existing files must remain preserved.

For workspace overlay behavior, validate that context changes are stored in `ext_maestro_*` tables, that the `ariad_workspace` binding controls injection, and that no target project files are written.

## Documentation Rules

Update documentation in the same cycle as the change when commands, behavior, install instructions, or conceptual boundaries change.

Relevant surfaces:

- `README.md` for user-facing extension behavior;
- `SKILL.md` for agent-facing skill behavior;
- `skill.yaml` for extension metadata and command routing;
- `docs/project/decisions.md` for decisions that future sessions must not reopen;
- `docs/process/worklog.md` for meaningful milestones.

## Story Lifecycle

For non-trivial work, follow the Ariad lifecycle:

1. read and orient;
2. plan;
3. implement;
4. test and validate;
5. review and refactoring assessment;
6. document and coherence check;
7. record project history according to the configured commit policy.

## Checkpoints

Stop for Navigator confirmation:

- after the plan;
- after tests and manual validation route;
- after review/refactoring assessment;
- before recording project history unless the local commit policy says otherwise.

Small mechanical fixes may compress the lifecycle, but should still report validation and changed files.

## Navigator Preferences

Use Ariad defaults unless this local guide or the Navigator says otherwise.

- **Commit policy:** commit after a coherent story or meaningful change is validated and accepted.
- **Push policy:** push only after Navigator authorization unless the session has explicitly authorized push.
- **Checkpoint compression:** use compressed checkpoints only for trivial low-risk changes.
- **Documentation detail:** update the smallest documentation surface that keeps the extension coherent.
- **Worklog policy:** record meaningful milestones, not every edit.
- **Branch/PR habits:** work on `main` for local extension development unless a review boundary needs a branch.

## Commit and Release Rules

Use descriptive English commit messages explaining the why.

Prefer small commits scoped to one extension behavior or documentation concern.

## Local Exceptions

Maestro intentionally copies templates without tailoring them. The agent-assisted tailoring of a project-specific local Ariad instance remains a Driver/Navigator workflow, not a deterministic command behavior.
