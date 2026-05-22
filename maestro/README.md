# Maestro Extension

Maestro is the Mirror extension that operates the [Ariad](https://github.com/mirror-mind-ai/ariad) method.

Ariad is a method for integral agentic development: human-agent development that keeps the work whole over time. Maestro is how Mirror Mind executes that method. The method lives in its own canonical repository; this extension turns it into operational Mirror capabilities.

## Contract Modes

Maestro distinguishes how Ariad is present in work and where its authority comes from.

### Repository adoption

Repository adoption means the project itself declares Ariad as part of its public agent contract. The repository normally contains `AGENTS.md` plus the local project docs that make up a local Ariad instance.

Use repository adoption when everyone who works in that repository should see Ariad as part of the project contract.

Repository adoption may write missing template files, but never overwrites existing files.

### Navigator preference defaults

Ariad ships with opinionated Navigator preference defaults. These are recommended starting behaviors, not method invariants.

Examples include full checkpoints for non-trivial work, ask-before-push, descriptive commit messages, small reviewable changes, and documentation updates when project truth changes.

Advanced Navigators and projects can override these preferences explicitly.

### Workspace overlay

Workspace overlay means Ariad guides a local Mirror journey without changing the repository contract.

Use workspace overlay when a developer wants Ariad to govern local Builder Mode conduct, checkpoints, validation, and coherence review, but the project should not publicly declare Ariad in `AGENTS.md`, `CLAUDE.md`, or equivalent files.

Workspace overlay is stored in Maestro's local extension tables and injected into Mirror context through the `ariad_workspace` capability. Changing overlay properties changes the next loaded context immediately; no project files need to change.

A useful boundary:

> Ariad may govern local conduct. Project docs should record only truths about the project. Repository contract files should change only when repository adoption is explicitly desired.

## Commands

### `status`

```bash
uv run python -m memory ext maestro status --journey <slug>
```

Checks whether Maestro is operational end to end: installed extension copy, source clone, Ariad root, migrations, and optional project or journey readiness.

Useful after first install or after updating local clones:

```bash
cd ~/mirror-extensions && git pull
cd ~/ariad && git pull
cd ~/mirror
uv run python -m memory extensions install maestro \
  --extensions-root ~/mirror-extensions \
  --mirror-home ~/.mirror-minds/<user>
uv run python -m memory ext maestro migrate
uv run python -m memory ext maestro status --journey <slug>
```

A healthy installation ends with:

```text
Status: ready
```

If the installed copy contains stale files from an older Maestro version, `status` reports `Installed copy: stale installed files` and suggests removing the installed extension directory before reinstalling.

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

### `overlay`

Configure Ariad as a local workspace overlay for a Mirror journey, without modifying the target repository.

```bash
uv run python -m memory ext maestro overlay enable \
  --journey mirror-mind \
  --ariad-root /path/to/ariad
```

Then bind the context capability to the journey:

```bash
uv run python -m memory ext maestro bind ariad_workspace --journey mirror-mind
```

Check status:

```bash
uv run python -m memory ext maestro overlay status --journey mirror-mind
```

Change contract properties:

```bash
uv run python -m memory ext maestro overlay set \
  --journey mirror-mind \
  --repo-contract-policy ask_before_change \
  --checkpoint-policy compressed_for_trivial \
  --commit-policy after_any_codebase_change \
  --push-policy epic_boundary
```

Disable the overlay configuration:

```bash
uv run python -m memory ext maestro overlay disable --journey mirror-mind
```

Unbind the context capability when you no longer want it injected:

```bash
uv run python -m memory ext maestro unbind ariad_workspace --journey mirror-mind
```

Overlay policies:

| Policy | Values | Default |
|---|---|---|
| `repo-contract-policy` | `do_not_modify`, `ask_before_change`, `allow_if_explicit` | `do_not_modify` |
| `doc-update-policy` | `project_relevant_only`, `ariad_required`, `manual_only` | `project_relevant_only` |
| `checkpoint-policy` | `ariad_full`, `compressed_for_trivial`, `manual` | `ariad_full` |
| `validation-policy` | `required`, `when_user_visible`, `manual` | `required` |
| `commit-policy` | `after_validated_story`, `after_any_codebase_change`, `manual_only` | `after_validated_story` |
| `push-policy` | `ask_before_push`, `after_accepted_story`, `epic_boundary`, `manual_only` | `ask_before_push` |
| `worklog-policy` | `meaningful_milestones`, `every_story`, `manual_only` | `meaningful_milestones` |
| `documentation-detail-policy` | `smallest_coherent_surface`, `detailed`, `manual_only` | `smallest_coherent_surface` |
| `branch-policy` | `project_default`, `ask_before_branch`, `dedicated_branch_per_story` | `project_default` |
| `pr-policy` | `project_default`, `ask_before_pr`, `pr_per_story`, `no_pr` | `project_default` |

When active, `memory build load <journey>` already receives the overlay instructions because Mirror's extension context mechanism injects capabilities bound to the active journey.

### `doctor`

```bash
uv run python -m memory ext maestro doctor --project-path /path/to/project
```

Or resolve the project from a Mirror journey's `project_path`:

```bash
uv run python -m memory ext maestro doctor --journey diario
```

Checks both dimensions:

- **Repository adoption**: whether the project has a local Ariad instance in its files.
- **Workspace overlay**: whether Maestro has a local Ariad overlay configured and bound to the journey.

Possible statuses include:

- `ready`: repository adoption is complete.
- `workspace overlay`: Ariad is active locally through a bound workspace overlay, even if the repo is not adopted.
- `canonical`: the target appears to be the canonical Ariad repository.
- `not ready`: neither repository adoption nor active workspace overlay is present.

The command is read-only. It reports readiness, missing files, overlay state, and next steps.

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

Run pending migrations after updating an installed extension:

```bash
uv run python -m memory ext maestro migrate
```

## Status

Implemented:

- `status` — end-to-end install, source clone, Ariad root, migration, and readiness check
- `doctor` — read-only readiness check across repository adoption and workspace overlay
- `adopt` — copy missing templates without overwriting existing files
- `adopt --dry-run` — read-only adoption plan
- `init` — create a new Ariad-ready project safely
- `update` — report-only comparison against canonical templates
- `overlay` — local Ariad workspace overlay for Mirror journeys
- `ariad_workspace` — Mirror context capability for overlay injection

Planned later:

- `adopt` reconciliation mode — help merge/adapt existing local docs
- `update` reconciliation mode — propose safe local updates without blind overwrite
- template version awareness

## Relationship to Ariad

| Surface | Lives in | Role |
|---|---|---|
| **Ariad** | `~/Code/ariad` (canonical repo) | The method: docs, templates, principles |
| **Maestro** | This extension | The Mirror runtime that operates the method |
| **Repository adoption** | Target project files | Public project contract |
| **Navigator preference defaults** | Ariad and Maestro defaults | Opinionated starting posture |
| **Workspace overlay** | Local Mirror extension state | Local runtime contract plus configured preferences |

Ariad does not depend on Mirror Mind. Maestro depends on both.
