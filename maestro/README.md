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

## Product Docs

- `docs/product/principles.md` — product behavior principles for Maestro.
- `docs/product/visualization-grammar.md` — Ariad/Maestro visualization grammar for Driver/Navigator orientation.

## Commands

### `checkpoint`

```bash
uv run python -m memory ext maestro checkpoint \
  --journey maestro \
  --checkpoint validate \
  --cv-code CV2 \
  --cv-title "Ariad/Maestro Visualization" \
  --epic-code E2 \
  --epic-title "Checkpoint View MVP" \
  --epic-progress 1/3 \
  --story "S2 checkpoint Command" \
  --release-kind emergent \
  --status-sentence "S2 implemented and validated. We are at the validation checkpoint." \
  --automated "Automated checks:passed:79 tests passed" \
  --manual "Manual validation:not_run" \
  --blocker "none" \
  --risk "Risk posture:attention:manual validation pending" \
  --doing "S2:checkpoint Command" \
  --done "S1:Checkpoint Renderer" \
  --coherence "Roadmap:checked:CV2.E5.S3 updated" \
  --coherence "Release notes:not_applicable:No release boundary" \
  --roadmap "cv:CV2:Ariad/Maestro Visualization:active:5/6" \
  --roadmap "epic:E6:Roadmap Snapshot:next:1/3" \
  --roadmap "story:S2:Roadmap Snapshot Renderer:next" \
  --recommended-next "Prepare the manual smoke route."
```

Renders a compact Ariad/Maestro checkpoint orientation view. The full form is intentionally explicit: it does not infer roadmap state from project files yet. It exists to make the visualization grammar usable before richer state discovery is added.

For lower-friction Builder Mode use, `quick` renders checkpoint-specific minimum surfaces with safe unknown defaults:

```bash
uv run python -m memory ext maestro checkpoint quick \
  --journey sandbox-pet-store \
  --checkpoint validate \
  --story "S1 Add item to cart"
```

`quick` always renders the Bird's-Eye Map and canonical Ariad Stage Ribbon. It also adds Validation Panel for `validate`, Coherence Matrix for `coherence`, and Validation Panel, Coherence Matrix, and Roadmap Snapshot for `commit`.

### Pi structured checkpoint tool

Maestro also ships a Pi extension source at `pi/maestro-visibility.ts`. When loaded by Pi, it registers a structured `maestro_checkpoint` tool. The tool lets the Driver emit checkpoint state as data instead of hand-drawing Maestro visuals or relying on bash command strings.

The Pi renderer uses a single compact title, for example:

```text
Maestro checkpoint: Coherence · CV1.E2.S1 Show cart
```

and renders the Maestro view with its own shell so Pi's default success/error background does not obscure the visual grammar. The structured tool path is the intended protocol; the Pi extension does not infer checkpoints by parsing assistant prose.

For story close, the Pi tool uses `checkpoint=commit` even when no git commit will be created. The Driver should explain the reason in `statusSentence` (for example, no `.git` repository or Navigator requested no commit). When known, pass `roadmap` items so the `Roadmap Snapshot` appears at story close.

Use the Pi command to control the protocol in a session:

```text
/maestro on
/maestro off
/maestro status
/maestro on sandbox-pet-store
```

When enabled, the Pi status line shows:

```text
♪ Maestro · on
```

When disabled, the tool remains available but Maestro stops injecting the checkpoint-protocol instruction into the system prompt.

The Pi tool silently skips rendering when the Driver calls it without a complete work map (`cvCode`, `cvTitle`, `epicCode`, `epicTitle`, and `story`). This avoids noisy Maestro blocks in meta-conversations or incomplete flow contexts.

Evidence flags use `LABEL:STATE[:DETAIL]`. Valid states are `passed`, `attention`, `blocked`, `not_run`, and `unknown`.

Flow card flags use `CODE:TITLE`. Available lane flags are `--backlog`, `--ready`, `--doing`, `--validate-card`, and `--done`. Repeat a flag to add multiple cards to the same lane.

Coherence flags use `SURFACE:STATE[:DETAIL]`. Valid states are `checked`, `attention`, `missing`, `not_applicable`, and `unknown`. Repeat `--coherence` for multiple rows.

Roadmap flags use `LEVEL:CODE:TITLE:STATUS[:DONE/TOTAL]`. Valid levels are `cv`, `epic`, and `story`. Valid statuses are `done`, `active`, `next`, `planned`, `radar`, and `blocked`. Progress is optional and should only be supplied when the counts are trustworthy.

### `simulate`

```bash
uv run python -m memory ext maestro simulate --all
```

Renders a synthetic Maestro checkpoint run over a public-safe Sandbox Pet Store roadmap. This is a deterministic exercise surface for visualization: it generates explicit synthetic state for plan, implement, validate, coherence, and commit checkpoints without mutating project files, parsing roadmap Markdown, or using private pilot data.

Use `--story-index N` to render a single zero-based story and `--all` to render every synthetic story. Add `--transcript` to wrap checkpoint views in a synthetic Driver/Navigator conversation, and `--report` to append a final traversal report.

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

The overlay context also instructs Builder Mode to make Maestro visuals present at non-trivial checkpoints. Drivers should follow a command-first rule: run `memory ext maestro checkpoint` when explicit state is available, and use Maestro's exact fallback grammar when a command is not practical. The Ariad Stage Ribbon uses only `Plan`, `Implement`, `Validate`, `Review`, `Coherence`, and `Commit` with `✓`, `◉`, and `○` markers. A ribbon alone is not enough for non-trivial checkpoints: plan should include Bird's-Eye Map, validate should include Validation Panel, coherence should include Coherence Matrix, and story close should include Roadmap Snapshot. Unknown state should stay unknown rather than being invented for display.

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

Compares a local Ariad instance with the canonical templates and renders an actionable drift report.

The report classifies:

- missing local template files;
- files that differ from canonical Ariad;
- local-only Ariad files under `AGENTS.md`, `docs/process/`, `docs/product/`, and `docs/project/`;
- files already up to date.

The command is report-only. It does not overwrite, merge, or apply patches. For missing files, use `adopt --dry-run` before writing. For different files, preserve local project truth by default and reconcile through Driver/Navigator review.

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

- `checkpoint` — textual Ariad/Maestro checkpoint orientation view
- `simulate` — synthetic checkpoint simulation over a public-safe roadmap
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
