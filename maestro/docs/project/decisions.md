# Decisions

Incremental decisions made as the Maestro extension evolves.

## Completed Decisions

### Checkpoint visualization starts with explicit input

**Date:** 2026-05-23
**Status:** Decided

Decision: The first `checkpoint` visualization command accepts explicit input instead of inferring roadmap, validation, coherence, release, or progress state from project files.

Rationale: Maestro must orient Driver/Navigator work without inventing project truth. Automatic parsing of arbitrary roadmap Markdown and implicit validation state would create false confidence before the data model is stable. Explicit input keeps the visualization useful while preserving Ariad's honesty principle: unknown state should remain unknown.

Consequences:

- `memory ext maestro checkpoint` renders supplied data and safe defaults only.
- Roadmap Snapshot items use explicit `LEVEL:CODE:TITLE:STATUS[:DONE/TOTAL]` flags.
- Validation evidence, flow-board cards, and coherence rows are supplied through explicit flags.
- Future persistence or parsing should be added only after repeated dogfooding proves the model and failure modes.

### Visualization grammar starts in Maestro as operational rendering

**Date:** 2026-05-23
**Status:** Decided

Decision: Ariad/Maestro visualization starts in Maestro as operational rendering and dogfooding, not as canonical Ariad method.

Rationale: Ariad defines the method. Maestro materializes the method in operation. The visualization components discovered during Mirror Mind self-update work are real and useful, but they are still field-tested operational patterns rather than stable method law. Moving them into Ariad too early would freeze the method before enough usage has clarified what belongs to every Ariad implementation.

Consequences:

- Maestro may document and implement Bird's-Eye Map, Horizontal Flow Board, Transition View, Release Intent, Validation Panel, Coherence Matrix, compact checkpoint sentence, and health signals as runtime surfaces.
- Ariad remains the authority for lifecycle concepts such as Driver/Navigator, checkpoints, validation, coherence, review, and record-history discipline.
- Each visualization component should be classified as Ariad method, Maestro rendering, Maestro experiment, or candidate upstream before implementation.
- Concepts are promoted to Ariad only after dogfooding shows they are method-level and runtime-independent.
- Maestro docs must avoid implying that experimental rendering grammar is canonical Ariad.

Routing rule: if a concept defines how human-agent work should happen regardless of runtime, it belongs in Ariad. If a behavior renders, stores, executes, reads, or guides Ariad inside Mirror, it belongs in Maestro. If the concept is still being discovered, keep it in Maestro as an operational experiment.

### Update remains report-only while reconciliation is guided

**Date:** 2026-05-22
**Status:** Decided

Decision: `maestro update` should become more actionable without writing, merging, or patching local project files.

Rationale: Local Ariad instances intentionally diverge from canonical templates because they contain project truth. Treating divergence as an error would violate the Ariad contract. The right next step is to classify drift and guide Driver/Navigator review, not automate reconciliation prematurely.

Consequences:

- `update` reports missing, different, local-only, and up-to-date Ariad files.
- Missing files point toward `adopt --dry-run` and explicit Navigator approval before writing.
- Different files are reviewed manually, preserving local truth by default.
- Local-only files stay local unless their idea is generalizable enough to promote into canonical Ariad.
- Patch generation or automated reconciliation remains future work.

### Maestro status is the getting-started close-loop command

**Date:** 2026-05-21
**Status:** Decided

Decision: Maestro should provide a `status` command that closes install and update flows with an executable diagnostic.

Rationale: Getting started should not end with an assumption that installation worked. Private onboarding rehearsals showed that real users need one final command that verifies the installed extension copy, source clone, Ariad root, migrations, and target journey readiness. They also revealed that reinstalling an extension over an older copy can leave stale files in the installed extension directory.

Consequences:

- `status` reports installed copy, source clone, sync state, Ariad root, migration state, and optional journey readiness.
- Documentation should use `status` as the final validation command after installing or updating Maestro.
- Stale installed files are treated as not ready and reported separately from normal source drift.
- A separate Mirror core follow-up should consider clean extension reinstall support.

### Ariad preferences are defaults, not method invariants

**Date:** 2026-05-21
**Status:** Decided

Decision: Maestro should preserve the distinction between Ariad's method contract and Navigator preference defaults.

Rationale: Ariad needs an opinionated out-of-the-box posture, but not every recommended habit should become a universal law. Commit frequency, push rhythm, checkpoint compression, worklog detail, branch habits, and pull request rules depend on the Navigator, team, or project.

Consequences:

- Ariad defaults should be treated as recommended starting preferences.
- Maestro overlay configuration should make preferences explicit when possible.
- A personal process habit should not be promoted to repository contract unless explicitly requested.
- Overlay configuration supports repository contract, documentation update, checkpoint, validation, commit, push, worklog, documentation detail, branch, and PR policies.

### Ariad has repository adoption and workspace overlay modes

**Date:** 2026-05-20
**Status:** Decided

Decision: Maestro distinguishes **repository adoption** from **workspace overlay**.

Repository adoption means the project declares Ariad in its public agent contract and carries a local Ariad instance in repo files. Workspace overlay means Ariad guides a local Mirror journey through extension context without modifying the repository contract.

Rationale: Ariad-generated work can be important to the project, but the authority differs by surface. Local conduct can be chosen by the developer, project docs should record truths about the project, and repository contract files should change only when project governance explicitly adopts Ariad.

Consequences:

- `adopt` remains repository-level adoption and may create missing templates safely.
- `overlay` configures local Ariad operation for a journey without writing project files.
- `ariad_workspace` is the Mirror context capability used to inject overlay instructions.
- `doctor` reports both repository adoption and workspace overlay state.
- Projects like Mirror Mind can be operated locally with Ariad without forcing Ariad onto all repo users.

### Maestro is the Mirror implementation of Ariad

**Date:** 2026-05-20
**Status:** Decided

Decision: Use **Ariad** for the method and **Maestro** for the Mirror extension that operates the method.

Rationale: The method and the runtime implementation need different names. Ariad is the canonical repository of docs, templates, and principles. Maestro is how Mirror Mind discovers, installs, diagnoses, and updates Ariad instances in projects.

Consequences:

- Commands live under `memory ext maestro ...`.
- Extension metadata uses `id: maestro` and `table_prefix: ext_maestro_`.
- User-facing docs must avoid calling the extension Ariad.
- Ariad docs may reference Maestro as the reference Mirror implementation.

### Preserve existing files during adoption

**Date:** 2026-05-20
**Status:** Decided

Decision: `adopt` and `init` must not overwrite existing files.

Rationale: Ariad adoption often happens inside mature projects. Local project docs are already a source of truth and should not be replaced by canonical templates. Adoption should create missing surfaces and ask the Driver/Navigator to reconcile existing ones.

Consequences:

- `adopt --dry-run` must show planned writes before write mode.
- Write mode skips existing files.
- Reconciliation should be a future guided workflow, not blind overwrite.

### Canonical Ariad is discovered, not vendored

**Date:** 2026-05-20
**Status:** Decided

Decision: Maestro resolves the canonical Ariad repository from `--ariad-root`, `ARIAD_ROOT`, or `~/ariad`; it does not vendor the canonical method inside the extension.

Rationale: Ariad has its own repository, lifecycle, and license. Maestro should operate it, not duplicate it.

Consequences:

- Commands that need templates must resolve Ariad root explicitly or by convention.
- Consumer projects receive local Ariad instances, not full canonical docs.
- Update/version-awareness belongs to Maestro, but source-of-truth content belongs to Ariad.

## Open Discussions

### Template versioning

**Status:** Open
**Raised:** 2026-05-20

Maestro can compare local files against canonical templates, but does not yet track which Ariad template version a project adopted. Decide after more pilot feedback whether to store template versions, commit SHAs, checksums, or a lightweight marker file.

### Reconciliation workflow

**Status:** Open
**Raised:** 2026-05-20

`update` is report-only and `adopt` is safe-write only. A future reconciliation mode could propose patches, produce diffs, or guide the Driver through local adaptation. This should be informed by real adoption friction from private pilots and public dogfooding.

### Extract shared overlay/project helpers

**Status:** Open
**Raised:** 2026-05-21

`doctor.py` currently reads workspace overlay rows directly instead of reusing `get_overlay()` from `overlay.py`. This avoids an import cycle because `overlay.py` imports `project_path_for_journey()` from `doctor.py`.

This is acceptable for the current slice, but the duplication should be revisited if overlay status grows further. A likely cleanup is extracting project and overlay helper functions into a neutral module such as `src/project.py` or `src/workspace.py`, allowing `doctor.py`, `overlay.py`, and context providers to share the same read model without cycles.
