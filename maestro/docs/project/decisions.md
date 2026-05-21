# Decisions

Incremental decisions made as the Maestro extension evolves.

## Completed Decisions

### Ariad preferences are defaults, not method invariants

**Date:** 2026-05-21
**Status:** Decided

Decision: Maestro should preserve the distinction between Ariad's method contract and Navigator preference defaults.

Rationale: Ariad needs an opinionated out-of-the-box posture, but not every recommended habit should become a universal law. Commit frequency, push rhythm, checkpoint compression, worklog detail, branch habits, and pull request rules depend on the Navigator, team, or project.

Consequences:

- Ariad defaults should be treated as recommended starting preferences.
- Maestro overlay configuration should make preferences explicit when possible.
- A personal process habit should not be promoted to repository contract unless explicitly requested.
- Future overlay work may add commit, push, worklog, documentation detail, branch, and PR policies.

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

`update` is report-only and `adopt` is safe-write only. A future reconciliation mode could propose patches, produce diffs, or guide the Driver through local adaptation. This should be informed by real adoption friction, especially the Raphael pilot.
