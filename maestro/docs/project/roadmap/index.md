# Roadmap

The roadmap describes meaningful progress for the Maestro extension.

## Current Focus

The current focus is to make the first Ariad adoption flow reliable enough for real Mirror Mind users.

This focus is complete when:

- readiness checks are clear;
- adoption never overwrites existing project files;
- project resolution works through journeys and explicit paths;
- canonical Ariad discovery is predictable;
- the Raphael onboarding can use Maestro without bespoke intervention.

## Active Work

| Item | Status | Notes |
|------|--------|-------|
| Ariad adoption executor | Done | `doctor`, `init`, `adopt`, and `update` implemented. |
| Workspace overlay | Done | Local journey-level Ariad operation via `overlay` and `ariad_workspace` context capability. |
| Mirror/org restructuring | Done | Extension lives at `mirror-mind-ai/extensions/tree/main/maestro`. |
| Self-adoption | Done | Maestro now has a local Ariad instance. |
| Pilot hardening | Done | Raphael onboarding exposed the need for an end-to-end install status command and clone-based updates. |
| Getting-started close loop | Done | `status` checks installed copy, source clone, Ariad root, migrations, and optional journey readiness. |

## Planned Work

### Improve `update`

Move beyond report-only comparison when the right safe behavior is clear. Possible directions:

- show better diffs;
- classify differences by risk;
- propose patch files;
- support a guided reconciliation workflow.

### Navigator preference policies

Workspace overlay now supports commit, push, worklog, documentation detail, branch, and pull request policies.

Future work should focus on making these preferences easier to inspect, explain, and configure through natural language.

The goal is to preserve Ariad's opinionated defaults while letting advanced Navigators customize behavior without altering the repository contract.

### Template version awareness

Track which canonical Ariad template state a project adopted. Candidate mechanisms:

- Ariad commit SHA;
- template checksums;
- local metadata file;
- Mirror database state.

### Better readiness reporting

`status` now closes the install/update loop by checking Maestro's installed copy, source clone, Ariad root, migrations, and optional journey readiness.

Future reporting work can still make `doctor` output more actionable for not-ready projects, including clearer explanation of repository adoption, workspace overlay, local Ariad instance requirements, and next commands.

### Skill-guided adoption

Refine `ext-maestro` so natural-language adoption can guide the Driver through interpretation, local doc drafting, and Navigator review.

## Done

- Created Ariad executor extension under Maestro.
- Replaced old Maestro hello-world/coherence slice.
- Published the extension under `mirror-mind-ai/extensions`.
- Installed and validated locally.
- Validated readiness on Conjunto, Diário/SNA, Mirror Mind, and Maestro.
- Added `status` as the getting-started close-loop command for Maestro installations.

## Radar

### Cross-runtime Ariad executors

Problem: Ariad should not require Mirror forever, even though Mirror is the reference runtime.

Trigger: a real non-Mirror runtime asks for first-class Ariad support.

### Hosted canonical source discovery

Problem: local `ARIAD_ROOT` works for pilots, but broader adoption may need a more discoverable source.

Trigger: multiple users adopting Ariad without a local canonical checkout.
