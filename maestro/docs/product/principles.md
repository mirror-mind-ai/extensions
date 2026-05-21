# Product Principles

Product behavior principles for Maestro.

## Principles

### Safety before convenience

Maestro should never surprise a project by overwriting local documentation or source files.

Dry-run, explicit reporting, and preserved existing files matter more than reducing one command flag. The user must be able to trust Maestro in mature repositories.

### Ariad remains visible

Maestro should not hide Ariad behind automation.

The user should understand that Ariad is the method, the project has a local Ariad instance, and Maestro is operating that relationship. Automation should make the method easier to use, not obscure the Driver/Navigator contract.

### Local context wins

A consumer project's local docs are part of its identity.

When canonical Ariad templates and local project docs differ, Maestro should preserve the local files and help surface the difference. It should not treat local divergence as an error by default.

### Deterministic core, guided judgment

Commands should be deterministic where the operation is mechanical: inspect files, copy missing templates, compare content.

Judgment-shaped work — interpreting a project, drafting local docs, reconciling divergent process guidance — should remain a guided Driver/Navigator workflow until proven safe to automate.

### Small operational surface

Maestro should stay small enough to explain.

A few clear commands that reliably support adoption are better than a broad automation surface that users cannot predict.

## Questions to Answer

- What exact metadata should identify the Ariad version a project adopted?
- How much reconciliation should happen through command output versus skill-guided workflow?
- Should Maestro ever write updates to existing docs, or only generate proposed patches?
- What should a non-technical Navigator see when Maestro reports readiness or drift?
