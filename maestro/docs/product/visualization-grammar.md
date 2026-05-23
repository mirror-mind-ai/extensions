# Ariad/Maestro Visualization Grammar

This document consolidates visualization patterns discovered during Mirror Mind self-update work and turns them into a product contract for Maestro.

Maestro visualization exists to orient Driver/Navigator work. It should show where the work is, what checkpoint is active, what evidence exists, what remains unresolved, and which next movement preserves coherence.

It is not a dashboard for its own sake.

## Boundary with Ariad

Ariad defines the method. Maestro materializes the method in operation.

Use this rule:

```text
If it defines how human-agent work should happen, it belongs in Ariad.
If it renders, stores, executes, reads, or guides that work inside Mirror, it belongs in Maestro.
If it is still being discovered, keep it in Maestro as an operational experiment.
Promote to Ariad only after the concept stabilizes as method.
```

This document is therefore a Maestro product document. It may contain candidate method ideas, but it does not make them canonical Ariad until they are promoted into the Ariad repository.

## Classification Vocabulary

Each visualization component can be classified as:

- **Ariad method** — canonical lifecycle or rule that any Ariad implementation should respect;
- **Maestro rendering** — textual/terminal/runtime presentation inside Mirror;
- **Maestro experiment** — useful field pattern not yet stable enough to promote;
- **Candidate upstream** — likely Ariad method concept after more dogfooding.

## Principles

### Orientation before detail

Every view should help the Navigator answer: where are we, what changed, what remains, and what decision is needed now.

Classification: Maestro rendering.

### Taxonomy is not state

Roadmap level and method state use different visual languages.

Taxonomy cards:

```text
🟪[CV9]  Capability Value
🟦[E3]   Epic
🟨[S18]  Story
```

Method state:

```text
✓ done
◉ current
○ pending
✕ blocked
```

Do not use taxonomy color to express lifecycle state.

Classification: Maestro rendering, candidate upstream if Ariad later formalizes visual notation.

### Checkpoints curate components

A single universal board is weaker than checkpoint-specific views.

The same components can be reused, but each checkpoint should select the components that support that moment.

Classification: Maestro experiment, candidate upstream.

### Signal before report

Compact surfaces should signal state, not explain everything. Detailed explanation belongs in the larger view.

Example:

```text
◇ alisson-vale · ✓
◇ alisson-vale · ⬆ v0.9.1
◇ alisson-vale · ⚠ attention
◇ alisson-vale · ✕ action required
◇ alisson-vale · ? unknown
```

Classification: Maestro rendering.

### Honesty over false green

When Maestro does not know something, it should say so. Unknown is better than invented readiness.

Classification: Ariad method principle already aligned with Maestro product behavior; runtime representation belongs in Maestro.

## Component Classification Review

This table is the boundary review for CV2.E1.S3. It keeps Maestro from becoming the accidental authority for Ariad method.

| Component | Classification | Boundary note |
|---|---|---|
| Driver/Navigator lifecycle | Ariad method | Ariad owns the lifecycle and checkpoint semantics. Maestro can render current state. |
| Checkpoint names | Ariad method | Names such as Plan, Implement, Validate, Review, Coherence, and Commit belong to Ariad. |
| Taxonomy cards | Maestro rendering | `🟪[CV]`, `🟦[E]`, and `🟨[S]` are a Maestro notation for roadmap location. |
| Method-state symbols | Maestro rendering | `✓`, `◉`, `○`, and `✕` are rendering choices, not method law. |
| Bird's-Eye Map | Maestro rendering | Nested work exists in Ariad; this map is a Maestro presentation. |
| Ariad Stage Ribbon | Mixed | Lifecycle belongs to Ariad; ribbon layout and symbols belong to Maestro. |
| Horizontal Flow Board | Maestro experiment | Useful for movement visibility, but not yet stable enough to promote. |
| Transition View | Maestro experiment, candidate upstream | The discipline of transition may become method-level; current shape remains a Maestro experiment. |
| Release Intent | Mixed, candidate upstream | Release awareness may belong to Ariad process; current card and labels remain Maestro rendering. |
| Validation Panel | Mixed | Ariad requires validation evidence; Maestro renders evidence states. |
| Coherence Matrix | Mixed | Ariad owns coherence check; Maestro renders project-specific surfaces and state. |
| Compact Checkpoint Sentence | Maestro rendering, candidate upstream | Useful checkpoint phrase; may promote if it becomes canonical transition language. |
| Status/health signals | Maestro rendering | Compact runtime signals belong to Maestro and Mirror integration. |
| Checkpoint-specific views | Maestro experiment, candidate upstream | The principle may prove method-level; current composition stays in Maestro. |

Promotion rule: a Maestro experiment can become a candidate upstream only after repeated dogfooding shows that the concept applies beyond Mirror/Maestro rendering. Candidate upstream items still require an Ariad repository change before becoming canonical method.

## Core Components

### Bird's-Eye Map

Purpose: locate the active work in the larger structure.

Example:

```text
🟪[CV9]  Mirror Mind 1.0
  🟦[E3]   Distribution & Tooling  Stories: 17/18  ███████░ 94%
    🟨[S18]  Welcome and Status Bar Release Awareness
```

Use when:

- planning a story;
- transitioning between stories;
- explaining why a next movement is coherent.

Data requirements:

- value, epic, and story labels when known;
- progress only when story counts are trustworthy.

If progress is approximate, label it as narrative rather than authoritative.

Classification: Maestro rendering. The underlying idea that work has nested progress belongs to Ariad; this notation belongs to Maestro.

### Ariad Stage Ribbon

Purpose: show where the work is in the Ariad lifecycle.

Example:

```text
Ariad: ✓ Plan | ✓ Implement | ✓ Validate | ◉ Review | ○ Coherence | ○ Commit
```

Use when:

- stopping at a checkpoint;
- resuming a session;
- reporting completion state.

Checkpoint vocabulary:

```text
Plan
Implement
Validate
Review
Coherence
Commit
```

Classification: mixed. Checkpoint names and lifecycle belong to Ariad. Ribbon notation belongs to Maestro.

### Horizontal Flow Board

Purpose: show motion between work states.

Example:

```text
+---------+--------+--------------------------------+----------+--------------------------------+
| Backlog | Ready  | Doing                          | Validate | Done                           |
+---------+--------+--------------------------------+----------+--------------------------------+
| 🟨[S19] |        | 🟨[S18] Welcome/Status Release |          | 🟨[S17] Fresh User Smoke       |
+---------+--------+--------------------------------+----------+--------------------------------+
```

Use when:

- showing neighboring stories;
- communicating motion;
- choosing the next card.

The board should not pretend to know backlog state unless that state is available or explicitly supplied.

Classification: Maestro experiment. It may become candidate upstream if Ariad formalizes flow-state visualization.

### Transition View

Purpose: show what was completed, where it was absorbed, what it unlocked, and why the next movement is coherent.

Example:

```text
Completed
🟨[S17] Fresh User Stable Update Smoke
Status: Done
Release: v0.9.0 - Self-Update Done

Integrated into
🟦[E3] Distribution & Tooling

Unlocked
- Stable self-update works from v0.8.0 to v0.9.0 in a fresh-user-shaped clone.
- Dogfooding exposed the opening UX gap.

Moving next
🟨[S17] Fresh User Smoke  --reveals-->  🟨[S18] Welcome and Status Bar Release Awareness
```

Use when:

- closing a story;
- choosing the next story;
- explaining why work moved from one card to another.

Classification: Maestro experiment, candidate upstream. The underlying transition discipline may belong in Ariad if it proves method-level.

### Release Intent

Purpose: make release context visible.

Known release:

```text
Release Intent
[known] v0.9.0 - Self-Update Done
Scope: 🟨[S13] + 🟨[S14] + 🟨[S15] + 🟨[S16] + 🟨[S17]
State: building
```

Emergent release:

```text
Release Intent
[emergent] no version selected yet
Likely boundary: story patch, epic minor, or CV major after coherence review
Decision point: transition or close
```

Use when:

- a release arc is known;
- dogfooding reveals follow-up work;
- deciding whether a story is a patch, epic release, or CV boundary.

Classification: mixed. Release intent as lifecycle awareness may be Ariad method. Rendering and state labels belong in Maestro until stabilized.

### Validation Panel

Purpose: distinguish forms of evidence.

Example:

```text
Automated checks: ✅ passed
Manual smoke:     🟨 blocked by release-state / local scenario
Risk posture:     ✅ expected, no production mutation
```

Use when:

- automated tests are done;
- manual validation is pending, waived, or blocked;
- environmental state affects validation.

Validation states should include at least:

```text
passed
attention
blocked
not run
unknown
```

Classification: mixed. Ariad requires validation and Navigator evidence. The panel and state rendering belong in Maestro.

### Coherence Matrix

Purpose: support closeout by showing which memory surfaces have been checked.

Example:

```text
Coherence Matrix
✓ Roadmap
✓ Story docs
✓ Worklog
○ Decisions
○ Journey context
○ Release notes
```

Use when:

- closing a story;
- preparing a commit;
- checking whether project memory is coherent.

The matrix should allow `not applicable` and `unknown`. Not every story updates every surface.

Classification: mixed. Coherence check belongs to Ariad. Matrix rendering and project-specific row discovery belong in Maestro.

### Compact Checkpoint Sentence

Purpose: give the Navigator a short orientation sentence at checkpoint boundaries.

Pattern:

```text
<Story> implemented and validated. We are at the <checkpoint> checkpoint.
```

Example:

```text
S15 implemented and validated. We are at the commit checkpoint.
```

Use when:

- pausing for Navigator confirmation;
- transitioning between lifecycle stages.

Classification: Maestro rendering, candidate upstream if Ariad formalizes checkpoint transition language.

## Checkpoint View Composition

### Plan View

Recommended components:

- Bird's-Eye Map;
- Transition View when previous work exists;
- Release Intent when known or relevant;
- scope boundary;
- risks;
- validation route.

Classification: Maestro experiment, candidate upstream.

### Implement View

Recommended components:

- active story or work item;
- Horizontal Flow Board when neighboring work matters;
- changed files;
- blockers.

Classification: Maestro experiment.

### Validate View

Recommended components:

- Validation Panel;
- commands run;
- expected and actual results;
- manual validation route;
- residual risk.

Classification: Maestro rendering over Ariad validation discipline.

### Review View

Recommended components:

- change map;
- refactoring done;
- refactoring deferred;
- design debt;
- documentation pending.

Classification: Maestro rendering over Ariad review discipline.

### Coherence View

Recommended components:

- Coherence Matrix;
- affected docs;
- journey context state;
- release-note needs;
- follow-up work.

Classification: Maestro rendering over Ariad coherence discipline.

### Commit View

Recommended components:

- compact checkpoint sentence;
- final diff summary;
- validation evidence;
- proposed commit message;
- push or CI policy.

Classification: Maestro rendering over Ariad record-history discipline.

## First Runtime Slice

The first implementation should be a small textual checkpoint view, not a full dashboard.

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

The first version may rely on explicit inputs. It should not require Maestro to parse every project's roadmap before producing useful orientation.

## Conscious Exclusions

Not in the first slice:

- full roadmap parser;
- automatic extraction of CV, epic, and story from arbitrary docs;
- persistent visual work item database;
- rich TUI or web UI;
- automatic commit, push, or release decisions;
- claiming validation or coherence status without evidence;
- promoting experimental visual grammar into Ariad before dogfooding.

## Open Questions

- Should the first command be `checkpoint`, `board`, or a mode of `status`?
- Where should explicit story/checkpoint state be stored if it needs to persist?
- Should visualization be a command only, a context provider, or both?
- Which parts belong in Ariad as method vocabulary and which belong in Maestro as runtime rendering?
- How much should the natural-language `ext-maestro` skill compose these views before deterministic commands exist?
