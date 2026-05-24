# Roadmap

The roadmap describes meaningful progress for the Maestro extension using the Ariad taxonomy: Capability Value, Epic, and Story.

## Taxonomy

- **Capability Value, CV**: a major user-visible or operator-visible capability.
- **Epic**: a cohesive block of work inside a CV.
- **Story**: an atomic delivery that can be verified end to end.

## Capability Values

| Code | Capability Value | Status |
|------|------------------|--------|
| CV1 | Ariad Operational Foundation | Done |
| CV2 | Ariad/Maestro Visualization | Done |
| CV3 | Guided Reconciliation and Template Versioning | Planned |
| CV4 | Cross-Runtime Ariad Operation | Radar |
| CV5 | Maestro Simulation Harness | Active |

## Current Focus

The current focus is selecting the next arc after **CV2, Ariad/Maestro Visualization**.

CV2 is complete: Maestro has a checkpoint-oriented visualization surface, explicit validation evidence, flow-board cards, coherence rows, and Roadmap Snapshot rendering.

The current active arc is **CV5, Maestro Simulation Harness**: exercise Maestro across synthetic roadmap stories without opening a real project development cycle. This lets Maestro dogfood checkpoint visualization deterministically and safely.

## Boundary Rule

Ariad defines the method. Maestro materializes the method in operation.

Use this routing rule during the visualization arc:

- If a concept defines how human-agent work should happen regardless of runtime, it belongs in Ariad.
- If a behavior renders, stores, executes, reads, or guides Ariad inside Mirror, it belongs in Maestro.
- If the concept is still being discovered, keep it in Maestro as an operational experiment and promote it to Ariad only after it stabilizes.

---

## CV1: Ariad Operational Foundation

**Status:** Done

Maestro became the Mirror extension that operates Ariad in real projects.

### CV1.E1: Extension rename and publication

**Status:** Done

Stories delivered:

- Move the Ariad executor extension under the Maestro name.
- Publish the extension under `mirror-mind-ai/extensions`.
- Preserve Ariad as the method and Maestro as the Mirror implementation.

### CV1.E2: Repository adoption executor

**Status:** Done

Stories delivered:

- `doctor`: readiness check for projects and journeys.
- `init`: safe project initialization from Ariad templates.
- `adopt`: safe adoption into existing projects, with `--dry-run`.
- `update`: report-only comparison against canonical templates.

### CV1.E3: Workspace overlay

**Status:** Done

Stories delivered:

- Local journey-level Ariad operation via `overlay`.
- `ariad_workspace` context capability.
- Navigator preference policies for commit, push, worklog, documentation detail, branch, and PR behavior.

### CV1.E4: Pilot hardening

**Status:** Done

Stories delivered:

- `status`: end-to-end install, source clone, Ariad root, migration, and readiness check.
- Private onboarding hardening.
- Actionable `update` drift report.

---

## CV2: Ariad/Maestro Visualization

**Status:** Done

CV2 turns visualization field notes from Mirror Mind self-update into a stable Maestro operational grammar.

### CV2.E1: Visualization Grammar and Boundary

**Status:** Done

Purpose: define what Maestro may render, what Ariad owns as method, and what remains experimental.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E1.S1 | Visual Grammar Document | Done | Created `docs/product/visualization-grammar.md` and consolidated the field-tested components. |
| CV2.E1.S2 | Ariad/Maestro Boundary Record | Done | Recorded the decision that visualization starts in Maestro as operational rendering and promotes to Ariad only after stabilization. |
| CV2.E1.S3 | Component Classification Review | Done | Classified each component as Ariad method, Maestro rendering, Maestro experiment, or candidate upstream. |

Done condition:

- visualization grammar exists;
- decision log records the boundary;
- each component has a boundary classification;
- first runtime slice has explicit exclusions.

### CV2.E2: Checkpoint View MVP

**Status:** Done

Purpose: render the first checkpoint-aware textual view for Driver/Navigator orientation.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E2.S1 | Checkpoint Renderer | Done | Pure renderer for Bird's-Eye Map, Ariad Stage Ribbon, compact checkpoint sentence, optional release/story fields, and yellow Story cards. |
| CV2.E2.S2 | `checkpoint` Command | Done | Added `memory ext maestro checkpoint --journey <slug>` with explicit checkpoint, work-map, release, status sentence, and recommended-next flags. |
| CV2.E2.S3 | Checkpoint Smoke and Docs | Done | Validated in an isolated Mirror home; documented command usage and conscious limits. |

Implemented command:

```bash
uv run python -m memory ext maestro checkpoint --journey <slug>
```

Core flags:

```bash
--checkpoint plan|implement|validate|review|coherence|commit
--story "S18 Welcome and Status Bar Release Awareness"
--release "v0.9.1 - Welcome Release Awareness"
```

### CV2.E3: Validation Panel

**Status:** Done

Purpose: make validation evidence legible without flattening everything into pass/fail.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E3.S1 | Validation State Model | Done | Represent automated, manual, blocker, and risk states honestly; attention uses `⚠` to avoid conflict with yellow Story cards. |
| CV2.E3.S2 | Validation Panel Renderer | Done | Render passed, attention, blocked, not run, and unknown states without conflicting with Story taxonomy. |
| CV2.E3.S3 | Validation View Integration | Done | Integrated validation evidence into checkpoint output and CLI flags. |

### CV2.E4: Flow Board

**Status:** Done

Purpose: render neighboring work in horizontal lanes.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E4.S1 | Flow Board Renderer | Done | Render `Backlog | Ready | Doing | Validate | Done` from explicit card state. |
| CV2.E4.S2 | Explicit Card Input | Done | Accept explicit lane cards through checkpoint command flags before roadmap parsing exists. |
| CV2.E4.S3 | Maestro Example Board | Done | Validated against Maestro's own visualization arc in an isolated smoke run. |

### CV2.E5: Coherence Matrix

**Status:** Done

Purpose: support the closeout checkpoint by showing which project memory surfaces were checked.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E5.S1 | Coherence Matrix Contract | Done | Define rows, states, unknown handling, and not-applicable handling. |
| CV2.E5.S2 | Coherence Matrix Renderer | Done | Render roadmap, docs, worklog, decisions, journey, release notes, and links without global ready state. |
| CV2.E5.S3 | Closeout View Integration | Done | Integrated matrix into checkpoint output and CLI flags. |

### CV2.E6: Roadmap Snapshot

**Status:** Done

Purpose: show the hierarchical CV/Epic/Story roadmap state at the end of each story.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E6.S1 | Roadmap Snapshot Contract | Done | Define roadmap item/status model, emoji legend, progress model, and explicit-input boundary. |
| CV2.E6.S2 | Roadmap Snapshot Renderer | Done | Render CV/Epic/Story hierarchy with progress bars, statuses, and current next story. |
| CV2.E6.S3 | End-of-Story Integration | Done | Show Roadmap Snapshot at story close or commit checkpoint through `checkpoint --roadmap`. |

The implemented version uses explicit roadmap data rather than parsing arbitrary Markdown. Automatic roadmap parsing remains out of scope until the data model is justified.

---

## CV3: Guided Reconciliation and Template Versioning

**Status:** Planned

CV3 deepens Maestro's existing adoption/update path after the first visualization capability.

Potential epics:

- Improve `update` with better diffs and risk classification.
- Support guided reconciliation without overwriting local truth.
- Add template version awareness.
- Improve not-ready reporting.
- Refine `ext-maestro` for natural-language adoption guidance.

---

## CV5: Maestro Simulation Harness

**Status:** Active

CV5 provides a deterministic synthetic field for exercising Maestro without depending on a real project.

### CV5.E1: Synthetic Checkpoint Runner

**Status:** Done

Purpose: generate explicit Maestro checkpoint views for a synthetic roadmap over multiple stories.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV5.E1.S1 | Python Simulation Harness | Done | Added pure simulation models and a Sandbox Pet Store roadmap that generate real `CheckpointView` objects across plan, implement, validate, coherence, and commit checkpoints. |
| CV5.E1.S2 | CLI Simulation Smoke | Done | Added `memory ext maestro simulate` to render one synthetic story or the full Sandbox Pet Store sequence through the extension command surface. |
| CV5.E1.S3 | Driver/Navigator Transcript Simulation | Done | Added `--transcript` to wrap synthetic checkpoint views in a Driver/Navigator conversation. |
| CV5.E1.S4 | Traversal Report | Done | Added `--report` to append a final project traversal summary with story outcomes, checkpoint coverage, evidence, flow, final state, and open questions. |
| CV5.E1.S5 | Synthetic Project Fixture | Deferred | The manual sandbox produced more useful evidence than a generated fixture for now. |

### CV5.E2: Builder Mode Visual Integration

**Status:** Active

Purpose: make Maestro visuals appear naturally during real Builder Mode checkpoints, not only through manual CLI use.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV5.E2.S1 | Overlay Checkpoint Visual Guidance | Done | Updated the `ariad_workspace` context provider to instruct Drivers to include compact Maestro visual orientation blocks at non-trivial checkpoints and prefer `memory ext maestro checkpoint` when explicit state is available. |
| CV5.E2.S2 | Canonical Ribbon Guidance | Done | Tightened overlay context after sandbox retest so Drivers use the canonical Maestro ribbon vocabulary instead of inventing alternate lifecycle labels. |
| CV5.E2.S3 | Checkpoint-Specific Visual Minimums | Done | Tightened overlay context after retest so Drivers know a ribbon alone is insufficient and must include checkpoint-specific surfaces. |
| CV5.E2.S4 | Quick Checkpoint Command | Done | Added `memory ext maestro checkpoint quick` to render checkpoint-specific minimum visual surfaces with safe unknown defaults. |
| CV5.E2.S5 | Manual Sandbox Retest | Next | Re-run the Sandbox Pet Store manual session and observe whether Drivers call `checkpoint quick` instead of hand-composing unreliable visuals. |

Boundaries:

- no real project mutation;
- no private pilot data;
- no roadmap Markdown parsing;
- no generated commits or pushes.

---

## CV4: Cross-Runtime Ariad Operation

**Status:** Radar

Ariad should not require Mirror forever, even though Mirror is the reference runtime.

Trigger: a real non-Mirror runtime asks for first-class Ariad support.

Potential directions:

- non-Mirror Ariad executor;
- hosted canonical source discovery;
- portable visualization grammar outside Mirror.

## Done Summary

- Created Ariad executor extension under Maestro.
- Replaced old Maestro hello-world/coherence slice.
- Published the extension under `mirror-mind-ai/extensions`.
- Installed and validated locally.
- Validated readiness on public and private real projects, including Mirror Mind and Maestro.
- Added `status` as the getting-started close-loop command for Maestro installations.
- Improved `update` into an actionable report-only drift report.
- Reoriented Maestro toward Ariad/Maestro visualization as the next product arc.
