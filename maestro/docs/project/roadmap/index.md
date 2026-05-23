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
| CV2 | Ariad/Maestro Visualization | Active |
| CV3 | Guided Reconciliation and Template Versioning | Planned |
| CV4 | Cross-Runtime Ariad Operation | Radar |

## Current Focus

The current focus is **CV2, Ariad/Maestro Visualization**: consolidate visualization as an operational product grammar while preserving the boundary between Ariad as method and Maestro as runtime implementation.

CV2 is complete when:

- the field-tested visualization patterns from Mirror Mind self-update are documented as a coherent Maestro grammar;
- method-level concepts and runtime-rendering choices are separated explicitly;
- the grammar distinguishes taxonomy, lifecycle state, flow state, release state, validation evidence, and health signals;
- Maestro has a first implementable slice that can render checkpoint-aware orientation without becoming a generic dashboard;
- product docs explain why visualization exists and when each view should appear;
- implementation has shipped in small validated stories.

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
- Raphael onboarding hardening.
- Actionable `update` drift report.

---

## CV2: Ariad/Maestro Visualization

**Status:** Active

CV2 turns visualization field notes from Mirror Mind self-update into a stable Maestro operational grammar.

### CV2.E1: Visualization Grammar and Boundary

**Status:** Active

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

**Status:** Next

Purpose: render the first checkpoint-aware textual view for Driver/Navigator orientation.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E2.S1 | Checkpoint Renderer | Done | Pure renderer for Bird's-Eye Map, Ariad Stage Ribbon, compact checkpoint sentence, optional release/story fields, and yellow Story cards. |
| CV2.E2.S2 | `checkpoint` Command | Done | Added `memory ext maestro checkpoint --journey <slug>` with explicit checkpoint, work-map, release, status sentence, and recommended-next flags. |
| CV2.E2.S3 | Checkpoint Smoke and Docs | Done | Validated in an isolated Mirror home; documented command usage and conscious limits. |

Candidate command:

```bash
uv run python -m memory ext maestro checkpoint --journey <slug>
```

Candidate flags:

```bash
--checkpoint plan|implement|validate|review|coherence|commit
--story "S18 Welcome and Status Bar Release Awareness"
--release "v0.9.1 - Welcome Release Awareness"
```

### CV2.E3: Validation Panel

**Status:** Next

Purpose: make validation evidence legible without flattening everything into pass/fail.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E3.S1 | Validation State Model | Done | Represent automated, manual, blocker, and risk states honestly; attention uses `⚠` to avoid conflict with yellow Story cards. |
| CV2.E3.S2 | Validation Panel Renderer | Done | Render passed, attention, blocked, not run, and unknown states without conflicting with Story taxonomy. |
| CV2.E3.S3 | Validation View Integration | Done | Integrated validation evidence into checkpoint output and CLI flags. |

### CV2.E4: Flow Board

**Status:** Planned

Purpose: render neighboring work in horizontal lanes.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E4.S1 | Flow Board Renderer | Done | Render `Backlog | Ready | Doing | Validate | Done` from explicit card state. |
| CV2.E4.S2 | Explicit Card Input | Done | Accept explicit lane cards through checkpoint command flags before roadmap parsing exists. |
| CV2.E4.S3 | Maestro Example Board | Done | Validated against Maestro's own visualization arc in an isolated smoke run. |

### CV2.E5: Coherence Matrix

**Status:** Active

Purpose: support the closeout checkpoint by showing which project memory surfaces were checked.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E5.S1 | Coherence Matrix Contract | Done | Define rows, states, unknown handling, and not-applicable handling. |
| CV2.E5.S2 | Coherence Matrix Renderer | Done | Render roadmap, docs, worklog, decisions, journey, release notes, and links without global ready state. |
| CV2.E5.S3 | Closeout View Integration | Next | Integrate matrix into the coherence checkpoint view. |

### CV2.E6: Roadmap Snapshot

**Status:** Planned

Purpose: show the hierarchical CV/Epic/Story roadmap state at the end of each story.

Stories:

| Code | Story | Status | Notes |
|------|-------|--------|-------|
| CV2.E6.S1 | Roadmap Snapshot Contract | Planned | Define roadmap item/status model, emoji legend, and explicit-input boundary. |
| CV2.E6.S2 | Roadmap Snapshot Renderer | Planned | Render CV/Epic/Story hierarchy with statuses and current next story. |
| CV2.E6.S3 | End-of-Story Integration | Planned | Show Roadmap Snapshot at story close or commit checkpoint. |

The first version should use explicit roadmap data rather than parsing arbitrary Markdown. Automatic roadmap parsing remains out of scope until the data model is justified.

---

## CV3: Guided Reconciliation and Template Versioning

**Status:** Planned

CV3 deepens Maestro's existing adoption/update path after visualization has stabilized.

Potential epics:

- Improve `update` with better diffs and risk classification.
- Support guided reconciliation without overwriting local truth.
- Add template version awareness.
- Improve not-ready reporting.
- Refine `ext-maestro` for natural-language adoption guidance.

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
- Validated readiness on Conjunto, Diário/SNA, Mirror Mind, and Maestro.
- Added `status` as the getting-started close-loop command for Maestro installations.
- Improved `update` into an actionable report-only drift report.
- Reoriented Maestro toward Ariad/Maestro visualization as the next product arc.
