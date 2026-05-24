# Worklog

Operational progress for Maestro.

## Done

### 2026-05-24 — Pi structured checkpoint tool officialized

Sandbox Pet Store testing showed that overlay guidance and `checkpoint quick` improved compliance but still depended on prompt interpretation. A local Pi hook spike proved two things: runtime injection is possible, but parsing assistant prose is still probabilistic and can misclassify checkpoints such as "advance without commit" as commit checkpoints.

Officialized the structured path by adding `pi/maestro-visibility.ts` to the Maestro source distribution. The Pi extension registers `maestro_checkpoint`, a structured tool that calls the Maestro checkpoint renderer from explicit data. Earlier parse-fallback and missing-tool guardrail experiments were removed because natural product conversation can mention validation/review language without reaching an Ariad checkpoint. The official Pi path is intentionally simple: provide the structured tool and checkpoint protocol instruction, but do not infer checkpoints from assistant prose.

The Pi renderer now uses `renderShell: "self"` and a custom result renderer so Pi's default blue/green/red tool background does not obscure Maestro visuals. It also uses a single title in the tool call row, for example `Maestro checkpoint: Coherence · CV1.E2.S1 Show cart`, and suppresses the duplicate `Maestro checkpoint` title inside the result body.

Additional hardening from the sandbox:

- evidence is only passed to the CLI for validation and commit checkpoints;
- coherence entries accept natural strings and normalize to `SURFACE:STATE[:DETAIL]`;
- the system instruction says not to hand-draw Maestro visuals;
- story close uses `checkpoint=commit` even when no git commit will be created, with the no-git/no-commit reason carried in `statusSentence`;
- the Pi tool accepts roadmap items so Roadmap Snapshot can render at story close;
- `/maestro on|off|status [journey]` controls whether checkpoint-protocol guidance is injected;
- the Pi status line uses `♪ Maestro · on` / `♪ Maestro · off` for low-noise runtime visibility.

This matters because Maestro visibility is now a structured runtime protocol for Pi, not merely a prompt convention or a manually invoked bash command.

### 2026-05-23 — Builder Mode checkpoint visual guidance added

Manual Sandbox Pet Store testing showed that the Driver can follow Ariad correctly while Maestro remains visually invisible. The Driver planned, implemented, validated, reviewed, documented, and closed a story, but did not naturally render Bird's-Eye Map, Ariad Stage Ribbon, Validation Panel, Coherence Matrix, Roadmap Snapshot, or call `memory ext maestro checkpoint`.

Updated the `ariad_workspace` context provider to make checkpoint visualization explicit in Builder Mode overlay context. The provider now tells Drivers to use a command-first rule for non-trivial checkpoints: run `memory ext maestro checkpoint` when explicit state is available, and otherwise use Maestro's exact fallback grammar rather than inventing a new visual language.

A second manual sandbox pass showed the guidance worked partially: Maestro orientation appeared, but the Driver invented a custom Stage Ribbon with labels such as Read and Orient, Test and Validate, Document, and Record History. Tightened the overlay context again to require the canonical ribbon vocabulary: Plan, Implement, Validate, Review, Coherence, Commit with `✓`, `◉`, and `○` markers.

A third observation showed another partial success: the Driver used the canonical ribbon, but rendered no other checkpoint visual surfaces. Tightened the overlay again so the context says a ribbon alone is not enough for non-trivial checkpoints and lists checkpoint-specific minimums: Bird's-Eye Map for plan, Validation Panel for validate, Coherence Matrix for coherence, and Roadmap Snapshot for story close. Added fallback templates for those surfaces when the checkpoint command is not practical.

The stronger prompt guidance still leaves too much discretion, so Maestro now has a lower-friction deterministic command: `memory ext maestro checkpoint quick`. The quick form renders checkpoint-specific minimum surfaces with safe unknown defaults: Validation Panel for validate, Coherence Matrix for coherence, and Validation Panel plus Coherence Matrix plus Roadmap Snapshot for commit. The overlay now points Drivers to `checkpoint quick` examples instead of asking them to hand-compose every visual.

This matters because a CLI command alone is not enough if it is too cumbersome to call. Maestro must be present in the conduct of Builder Mode sessions through a command that is easier than improvising the visual language.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/test_context.py
```

Result: 4 tests passed.

### 2026-05-23 — Maestro simulation harness started

Started CV5 Maestro Simulation Harness with a pure Python synthetic checkpoint runner, an extension command smoke surface, transcript rendering, and a final traversal report.

Added `src/simulation.py` with public-safe Sandbox Pet Store simulation data, story-run generation, roadmap-run generation, rendered simulation frames, and `memory ext maestro simulate`. The harness produces real `CheckpointView` objects across plan, implement, validate, coherence, and commit checkpoints, including Validation Panel, Flow Board, Coherence Matrix, and Roadmap Snapshot data where appropriate.

The command now supports `--transcript` to wrap Maestro checkpoints in a synthetic Driver/Navigator conversation, and `--report` to append a final traversal report with story outcomes, checkpoint coverage, evidence, flow, final state, and open questions.

This matters because Maestro can now be exercised across multiple synthetic roadmap stories without opening real project development, mutating project files, or leaking private pilot data. The harness preserves the explicit-input design: it generates supplied state for visualization instead of inferring truth from Markdown.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
uv run python -m memory extensions validate --extensions-root /Users/alissonvale/Code/mirror-extensions
```

Result: 126 tests passed and 3 extensions validated.

### 2026-05-23 — Maestro briefing pivoted toward Ariad visualization

Reoriented Maestro's project briefing and journey path around the next product arc: consolidating Ariad/Maestro visualization learnings from the recent Mirror Mind self-update and release work.

This matters because Maestro is no longer only the deterministic operator for Ariad adoption and update. The next coherent movement is to turn field-tested components such as Bird's-Eye Map, Horizontal Flow Board, Transition View, Release Intent, checkpoint-specific views, Validation Panel, Coherence Matrix, compact checkpoint sentence, and status/health signals into a stable operational grammar for Driver/Navigator work.

No runtime behavior changed. This was a context and direction update.

### 2026-05-23 — Ariad visualization implementation arc planned

Updated the roadmap and product principles for Maestro's next arc: turning Mirror Mind self-update visualization field notes into a stable Ariad/Maestro product grammar.

Created `docs/product/visualization-grammar.md` with the initial contract for Bird's-Eye Map, Ariad Stage Ribbon, Horizontal Flow Board, Transition View, Release Intent, Validation Panel, Coherence Matrix, compact checkpoint sentence, checkpoint-specific view composition, and first runtime slice exclusions.

Planned the implementation sequence: visual grammar document, method boundary review, checkpoint view command, validation panel, flow board, and coherence matrix. Added the new product doc to README discovery.

Recorded the Ariad/Maestro boundary decision: visualization starts in Maestro as operational rendering and dogfooding; method-level concepts promote to Ariad only after stabilization.

Reworked the roadmap into explicit CV/Epic/Story taxonomy: CV1 Ariad Operational Foundation is done, CV2 Ariad/Maestro Visualization is active, CV3 Guided Reconciliation and Template Versioning is planned, and CV4 Cross-Runtime Ariad Operation stays on radar.

No runtime behavior changed. This closes the planning slice before implementation.

### 2026-05-23 — CV2.E1 visualization boundary review completed

Completed CV2.E1.S3 by adding a component classification table to `docs/product/visualization-grammar.md`. Each visualization component is now explicitly classified as Ariad method, Maestro rendering, Maestro experiment, candidate upstream, or a mixed boundary.

Updated the roadmap to mark CV2.E1.S1, S2, and S3 done and set CV2.E2 Checkpoint View MVP as the next implementation epic. This gives the runtime work a safe boundary: Maestro can render and dogfood visualizations without becoming the canonical method authority.

No runtime behavior changed.

### 2026-05-23 — Checkpoint renderer implemented

Implemented CV2.E2.S1 with a pure checkpoint renderer in `src/checkpoint.py` and unit coverage in `tests/test_checkpoint.py`.

The renderer supports Bird's-Eye Map, yellow Story cards, Ariad Stage Ribbon, compact checkpoint sentence, optional known or emergent Release Intent, optional Recommended Next, and epic progress. It remains storage-free and CLI-free so the grammar is testable before runtime integration.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 70 tests passed.

Also updated current development commands in briefing and development guide to use the Mirror dev clone at `/Users/alissonvale/Code/mirror-dev` instead of the personal production clone.

### 2026-05-23 — Checkpoint command added

Completed CV2.E2.S2 and CV2.E2.S3 by registering `memory ext maestro checkpoint` and documenting it in README. The command renders the checkpoint view from explicit inputs: checkpoint, work-map fields, optional epic progress, story, release intent, status sentence, and recommended next action.

The first version is intentionally explicit and does not infer roadmap state from project files. This keeps the runtime surface useful while preserving the boundary established in CV2.E1.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 72 tests passed.

Manual smoke installed the updated extension into an isolated temporary Mirror home, ran migrations, and executed `memory ext maestro checkpoint --journey maestro`. The command rendered Bird's-Eye Map, yellow Story card, Ariad Stage Ribbon, emergent Release Intent, and Recommended Next without touching production state.

### 2026-05-23 — Validation state model added

Completed CV2.E3.S1 with `EvidenceItem` and `ValidationEvidence` models in `src/checkpoint.py`. The model separates automated evidence, manual evidence, blockers, and risk posture before rendering the full Validation Panel.

Validation states now have explicit markers: `passed` uses `✅`, `attention` uses `⚠`, `blocked` uses `⛔`, `not_run` uses `○`, and `unknown` uses `?`. The attention marker deliberately avoids the yellow square so it does not conflict with the yellow Story taxonomy card `🟨[S]`.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 76 tests passed.

### 2026-05-23 — Validation panel renderer added

Completed CV2.E3.S2 with `render_validation_panel()`. The panel renders automated checks, manual validation, blocker, and risk posture while using explicit unknown states when evidence is absent.

Attention uses `⚠`, preserving yellow `🟨` for Story taxonomy only.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 79 tests passed.

### 2026-05-23 — Validation panel integrated into checkpoint view

Completed CV2.E3.S3 by adding validation evidence to `CheckpointView` and exposing evidence flags in `memory ext maestro checkpoint`.

The command now accepts `--automated`, `--manual`, `--blocker`, and `--risk`. Evidence flags use `LABEL:STATE[:DETAIL]`, preserving the current explicit-input design while making the Validation Panel available in runtime output.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 81 tests passed.

Manual smoke installed the updated extension into an isolated temporary Mirror home, ran migrations, and executed `memory ext maestro checkpoint --checkpoint validate ...` with validation evidence. The command rendered Automated checks, Manual validation, Blocker, and Risk posture without touching production state.

### 2026-05-23 — Flow board renderer added

Completed CV2.E4.S1 with a pure flow board renderer in `src/flow.py` and unit coverage in `tests/test_flow.py`.

The renderer supports explicit lanes for Backlog, Ready, Doing, Validate, and Done, multiple cards per lane, empty lanes, and yellow Story cards. It remains CLI-free and inference-free so the board does not pretend to know roadmap state before explicit card input exists.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 87 tests passed.

### 2026-05-23 — Flow board integrated into checkpoint command

Completed CV2.E4.S2 and CV2.E4.S3 by adding explicit flow-card input to `memory ext maestro checkpoint` and validating the board against Maestro's own visualization arc.

The command now accepts `--backlog`, `--ready`, `--doing`, `--validate-card`, and `--done`, each using `CODE:TITLE`. Cards render in a horizontal board with yellow Story cards. The implementation remains explicit and does not infer roadmap state.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 92 tests passed.

Manual smoke installed the updated extension into an isolated temporary Mirror home, ran migrations, and executed `memory ext maestro checkpoint --checkpoint implement ...` with `--doing` and repeated `--done` cards. The command rendered the horizontal flow board without touching production state.

### 2026-05-23 — Coherence matrix contract added

Completed CV2.E5.S1 with `CoherenceItem` and `CoherenceMatrix` models in `src/coherence.py`.

The contract represents coherence-check surfaces without computing a global ready state. States are explicit: `checked` uses `✓`, `attention` uses `⚠`, `missing` uses `✕`, `not_applicable` uses `-`, and `unknown` uses `?`. This keeps closeout honest and prevents false green when Maestro does not know whether a surface was checked.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 99 tests passed.

### 2026-05-23 — Roadmap Snapshot added to visualization plan

Added Roadmap Snapshot as a first-class Maestro visualization component and planned CV2.E6 for implementation after the Coherence Matrix arc.

Roadmap Snapshot is the hierarchical CV/Epic/Story view shown at story close or commit checkpoint. It complements Flow Board: Flow Board shows local movement between lanes, while Roadmap Snapshot shows the broader map and next story.

Updated the visualization grammar, roadmap, and commit-view composition. The first implementation should use explicit roadmap data rather than parsing arbitrary Markdown.

### 2026-05-23 — Coherence matrix renderer added

Completed CV2.E5.S2 with `render_coherence_matrix()` in `src/coherence.py`.

The renderer shows each coherence surface with its explicit state marker and optional detail, handles empty matrices as unknown, and deliberately avoids rendering a global ready status.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 103 tests passed.

### 2026-05-23 — Coherence matrix integrated into checkpoint view

Completed CV2.E5.S3 by adding `coherence_matrix` to `CheckpointView` and exposing repeated `--coherence SURFACE:STATE[:DETAIL]` flags in `memory ext maestro checkpoint`.

The command now renders Coherence Matrix in the coherence checkpoint while preserving the no-global-ready-state rule.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 105 tests passed.

Manual smoke installed the updated extension into an isolated temporary Mirror home, ran migrations, and executed `memory ext maestro checkpoint --checkpoint coherence ...` with repeated coherence rows. The command rendered checked, not-applicable, and unknown surfaces without touching production state.

### 2026-05-23 — Roadmap Snapshot contract added

Completed CV2.E6.S1 with `Progress`, `RoadmapItem`, and `RoadmapSnapshot` models in `src/roadmap.py`.

The contract defines CV/Epic/Story levels, status markers (`✅`, `🟡`, `👉`, `⚪`, `🔭`, `⛔`), optional trustworthy progress, and an explicit-input boundary. Progress is represented only when done/total counts are known, avoiding invented precision.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 111 tests passed.

### 2026-05-23 — Roadmap Snapshot rendered and integrated into checkpoint view

Completed CV2.E6.S2 and CV2.E6.S3 by adding `render_roadmap_snapshot()`, explicit `--roadmap LEVEL:CODE:TITLE:STATUS[:DONE/TOTAL]` flags, and Roadmap Snapshot integration into `memory ext maestro checkpoint`.

The renderer supports CV/Epic/Story hierarchy, status markers, optional progress bars, and story-close orientation. Explicit flat CLI input is nested by nearest preceding parent so the runtime can render a readable hierarchy without parsing arbitrary Markdown.

Validation:

```bash
cd /Users/alissonvale/Code/mirror-dev
PYTHONPATH=/Users/alissonvale/Code/mirror-dev/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
```

Result: 116 tests passed.

Manual smoke installed the updated extension into an isolated temporary Mirror home, ran migrations, and executed `memory ext maestro checkpoint --checkpoint commit ...` with Roadmap Snapshot data. The command rendered CV2 with E5 done and E6 next, including progress bars.

### 2026-05-23 — CV2 visualization documentation closeout completed

Aligned Maestro's roadmap statuses, project briefing, skill instructions, development guide, decisions log, and visualization grammar after completing the implemented CV2 visualization components.

CV2 is now documented as done: visualization grammar and boundary, checkpoint view, validation panel, flow board, coherence matrix, and Roadmap Snapshot are all implemented. The docs now describe `checkpoint` as the implemented runtime slice, record the explicit-input decision, and route future work toward visualization polish, Ariad promotion review, or CV3 guided reconciliation/versioning.

Also scrubbed private pilot-specific names from public project documentation. Public docs may mention private pilots only generically when the learning matters.

### 2026-05-22 — Update command improved into actionable drift report

`maestro update` now reports Ariad drift with a summary, missing local files, different files, local-only Ariad files, up-to-date files, recommended next actions, and a final status.

This matters because update/reconciliation is the next bridge toward developing Mirror Mind under Ariad. The command still writes nothing, but its output now tells the Driver/Navigator what kind of review is needed: adopt missing files safely, reconcile differences without overwriting local truth, and keep or promote local-only ideas deliberately.

Verification:

```bash
cd /Users/alissonvale/mirror
PYTHONPATH=/Users/alissonvale/mirror/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
ARIAD_ROOT=/Users/alissonvale/Code/ariad uv run python -m memory ext maestro update --journey maestro
```

Result: 62 tests passed and `update --journey maestro` reported `Status: drift detected` with actionable next steps.

### 2026-05-21 — Maestro status command closes getting-started loop

Maestro now has a `status` command that verifies the installed extension copy, source clone, Ariad root, migrations, and optional journey readiness.

This matters because onboarding and update guides should end with a concrete diagnostic, not an implicit assumption that setup worked. Private onboarding rehearsals showed that clone-based updates need a final command that says whether Maestro is coherent end to end.

The command also detects stale installed files left behind by reinstalling over an older extension copy and suggests a clean removal plus reinstall when needed.

Verification:

```bash
cd /Users/alissonvale/mirror
PYTHONPATH=/Users/alissonvale/mirror/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
uv run python -m memory extensions validate --extensions-root /Users/alissonvale/Code/mirror-extensions
ARIAD_ROOT=/Users/alissonvale/Code/ariad MIRROR_EXTENSIONS_ROOT=/Users/alissonvale/Code/mirror-extensions uv run python -m memory ext maestro status --journey maestro
```

Result: 59 tests passed, 3 extensions validated, and `status` reported `Status: ready`.

### 2026-05-21 — Navigator preference policies implemented

Workspace overlay now carries explicit Navigator preference policies for commit, push, worklog, documentation detail, branch, and pull request behavior.

This matters because Ariad can now ship with opinionated defaults while Maestro gives advanced Navigators a concrete way to override local conduct without changing repository contract files.

Verification:

```bash
cd /Users/alissonvale/mirror
PYTHONPATH=/Users/alissonvale/mirror/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
uv run python -m memory extensions validate --extensions-root /Users/alissonvale/Code/mirror-extensions
```

### 2026-05-21 — Method contract and Navigator preferences clarified

The Maestro docs now distinguish Ariad's method contract from Navigator preference defaults and local overrides.

This matters because Maestro should not treat every good habit as a universal Ariad invariant. Ariad can ship with opinionated defaults while still allowing advanced Navigators to customize local behavior.

Follow-up: make preference configuration easier to drive through natural language and surface which values are Ariad defaults versus local overrides.

### 2026-05-20 — Workspace overlay implemented

Maestro now distinguishes repository adoption from workspace overlay.

Repository adoption means Ariad is declared in project files. Workspace overlay means Ariad guides a local Mirror journey through extension context without changing repository contract files.

Implemented:

- `overlay enable/status/set/disable`;
- `ariad_workspace` Mirror context capability;
- `doctor` reporting both repository adoption and workspace overlay;
- local overlay properties that affect the next context load immediately.

This matters because projects like Mirror Mind can be operated locally through Ariad without forcing all repository users or contributors to adopt Ariad publicly.

Verification:

```bash
cd /Users/alissonvale/mirror
PYTHONPATH=/Users/alissonvale/mirror/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
uv run python -m memory extensions validate --extensions-root /Users/alissonvale/Code/mirror-extensions
```

### 2026-05-20 — Maestro adopted Ariad locally

Maestro now has its own local Ariad instance:

- `AGENTS.md`;
- `docs/process/development-guide.md`;
- `docs/process/worklog.md`;
- `docs/product/principles.md`;
- `docs/project/briefing.md`;
- `docs/project/decisions.md`;
- `docs/project/roadmap/index.md`.

This matters because Maestro is itself an Ariad-operated project: the extension that installs Ariad should also be developed under Ariad's Driver/Navigator lifecycle.

Verification:

```bash
cd /Users/alissonvale/mirror
PYTHONPATH=/Users/alissonvale/mirror/src uv run pytest /Users/alissonvale/Code/mirror-extensions/maestro/tests/
uv run python -m memory ext maestro doctor --journey maestro
```

Result: tests passed and `doctor` reported `Status: ready`.

### 2026-05-20 — Maestro renamed and published as Ariad operator

The previous `ariad/` extension was consolidated into `maestro/`, replacing the old Maestro hello-world/coherence-engine slice.

The repository was transferred to:

```text
https://github.com/mirror-mind-ai/extensions
```

This matters because the naming is now coherent:

- Ariad is the method;
- Maestro is the Mirror extension that operates the method.

## Next

CV5 Maestro Simulation Harness is active. Next likely movements:

- bind and enable the Ariad workspace overlay for the Sandbox Pet Store journey;
- restart the manual sandbox session and observe whether Maestro visuals appear organically at checkpoints;
- inspect `simulate --all --transcript --report` as a product artifact and identify visualization polish;
- decide whether simulation should remain a developer/dogfooding command or become part of the public demo story.
