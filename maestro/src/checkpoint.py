"""Checkpoint view rendering for Ariad/Maestro visualization."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Literal

CheckpointName = Literal["plan", "implement", "validate", "review", "coherence", "commit"]
ReleaseIntentKind = Literal["known", "emergent"]
ValidationState = Literal["passed", "attention", "blocked", "not_run", "unknown"]

_CHECKPOINTS: tuple[CheckpointName, ...] = (
    "plan",
    "implement",
    "validate",
    "review",
    "coherence",
    "commit",
)
_CHECKPOINT_LABELS: dict[CheckpointName, str] = {
    "plan": "Plan",
    "implement": "Implement",
    "validate": "Validate",
    "review": "Review",
    "coherence": "Coherence",
    "commit": "Commit",
}
_VALIDATION_STATE_MARKERS: dict[ValidationState, str] = {
    "passed": "✅",
    "attention": "⚠",
    "blocked": "⛔",
    "not_run": "○",
    "unknown": "?",
}


@dataclass(frozen=True)
class EvidenceItem:
    """One validation evidence line."""

    label: str
    state: ValidationState
    detail: str | None = None

    def __post_init__(self) -> None:
        if self.state not in _VALIDATION_STATE_MARKERS:
            raise ValueError(f"Unknown validation state: {self.state}")

    @property
    def marker(self) -> str:
        return _VALIDATION_STATE_MARKERS[self.state]


@dataclass(frozen=True)
class ValidationEvidence:
    """Validation evidence grouped by source and risk."""

    automated: EvidenceItem | None = None
    manual: EvidenceItem | None = None
    blocker: str | None = None
    risk: EvidenceItem | None = None


@dataclass(frozen=True)
class EpicProgress:
    """Progress metadata for the active epic."""

    done: int
    total: int

    def __post_init__(self) -> None:
        if self.total <= 0:
            raise ValueError("Epic progress total must be greater than zero")
        if self.done < 0:
            raise ValueError("Epic progress done count cannot be negative")
        if self.done > self.total:
            raise ValueError("Epic progress done count cannot exceed total")


@dataclass(frozen=True)
class WorkMap:
    """Roadmap location for the active work."""

    cv_code: str
    cv_title: str
    epic_code: str
    epic_title: str
    story_code: str
    story_title: str
    epic_progress: EpicProgress | None = None


@dataclass(frozen=True)
class ReleaseIntent:
    """Release context shown when it matters for the checkpoint."""

    kind: ReleaseIntentKind
    title: str | None = None
    scope: str | None = None
    state: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class CheckpointView:
    """Data needed to render a compact checkpoint view."""

    checkpoint: CheckpointName
    work_map: WorkMap
    status_sentence: str | None = None
    release_intent: ReleaseIntent | None = None
    validation_evidence: ValidationEvidence | None = None
    recommended_next: str | None = None


def _progress_bar(progress: EpicProgress, *, width: int = 8) -> str:
    filled = round((progress.done / progress.total) * width)
    return "█" * filled + "░" * (width - filled)


def _render_work_map(work_map: WorkMap) -> list[str]:
    epic_line = f"  🟦[{work_map.epic_code}]   {work_map.epic_title}"
    if work_map.epic_progress is not None:
        progress = work_map.epic_progress
        percent = round((progress.done / progress.total) * 100)
        epic_line += f"  Stories: {progress.done}/{progress.total}  {_progress_bar(progress)} {percent}%"

    return [
        f"🟪[{work_map.cv_code}]  {work_map.cv_title}",
        epic_line,
        f"    🟨[{work_map.story_code}]  {work_map.story_title}",
    ]


def _render_stage_ribbon(current: CheckpointName) -> str:
    current_index = _CHECKPOINTS.index(current)
    parts: list[str] = []
    for index, checkpoint in enumerate(_CHECKPOINTS):
        if index < current_index:
            marker = "✓"
        elif index == current_index:
            marker = "◉"
        else:
            marker = "○"
        parts.append(f"{marker} {_CHECKPOINT_LABELS[checkpoint]}")
    return "Ariad: " + " | ".join(parts)


def _render_evidence_item(item: EvidenceItem) -> str:
    line = f"{item.label}: {item.marker} {item.state.replace('_', ' ')}"
    if item.detail:
        line += f" - {item.detail}"
    return line


def render_validation_panel(evidence: ValidationEvidence) -> str:
    """Render validation evidence as a compact panel."""

    lines = ["Validation Panel"]
    if evidence.automated:
        lines.append(_render_evidence_item(evidence.automated))
    else:
        lines.append("Automated checks: ? unknown")

    if evidence.manual:
        lines.append(_render_evidence_item(evidence.manual))
    else:
        lines.append("Manual validation: ? unknown")

    lines.append(f"Blocker: {evidence.blocker or 'none'}")

    if evidence.risk:
        lines.append(_render_evidence_item(evidence.risk))
    else:
        lines.append("Risk posture: ? unknown")

    return "\n".join(lines) + "\n"


def _render_release_intent(release: ReleaseIntent) -> list[str]:
    lines = ["Release Intent"]
    if release.kind == "known":
        title = release.title or "unnamed release"
        lines.append(f"[known] {title}")
    else:
        title = release.title or "no version selected yet"
        lines.append(f"[emergent] {title}")

    if release.scope:
        lines.append(f"Scope: {release.scope}")
    if release.state:
        lines.append(f"State: {release.state}")
    if release.note:
        lines.append(release.note)
    return lines


def render_checkpoint_view(view: CheckpointView) -> str:
    """Render a textual checkpoint view."""

    lines: list[str] = ["Maestro checkpoint", ""]
    lines.extend(_render_work_map(view.work_map))
    lines.append("")
    lines.append(_render_stage_ribbon(view.checkpoint))

    if view.status_sentence:
        lines.append("")
        lines.append(view.status_sentence)

    if view.release_intent:
        lines.append("")
        lines.extend(_render_release_intent(view.release_intent))

    if view.validation_evidence:
        lines.append("")
        lines.extend(render_validation_panel(view.validation_evidence).rstrip().splitlines())

    if view.recommended_next:
        lines.append("")
        lines.append("Recommended next")
        lines.append(view.recommended_next)

    return "\n".join(lines) + "\n"


def _split_code_and_title(value: str, *, default_code: str) -> tuple[str, str]:
    stripped = value.strip()
    if not stripped:
        return default_code, "Current work"
    parts = stripped.split(maxsplit=1)
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], parts[1]


def _parse_epic_progress(value: str | None) -> EpicProgress | None:
    if value is None:
        return None
    try:
        done_text, total_text = value.split("/", maxsplit=1)
        return EpicProgress(done=int(done_text), total=int(total_text))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Epic progress must use DONE/TOTAL, for example 1/3") from exc


def build_checkpoint_view_from_args(args: argparse.Namespace) -> CheckpointView:
    story_code, story_title = _split_code_and_title(args.story, default_code="S?")
    release_intent = None
    if args.release or args.release_kind:
        release_intent = ReleaseIntent(
            kind=args.release_kind or "known",
            title=args.release,
            scope=args.release_scope,
            state=args.release_state,
            note=args.release_note,
        )

    validation_evidence = None
    if any((args.automated, args.manual, args.blocker, args.risk)):
        validation_evidence = ValidationEvidence(
            automated=args.automated,
            manual=args.manual,
            blocker=args.blocker,
            risk=args.risk,
        )

    return CheckpointView(
        checkpoint=args.checkpoint,
        work_map=WorkMap(
            cv_code=args.cv_code,
            cv_title=args.cv_title,
            epic_code=args.epic_code,
            epic_title=args.epic_title,
            story_code=story_code,
            story_title=story_title,
            epic_progress=args.epic_progress,
        ),
        status_sentence=args.status_sentence,
        release_intent=release_intent,
        validation_evidence=validation_evidence,
        recommended_next=args.recommended_next,
    )


def _parse_evidence_item(value: str) -> EvidenceItem:
    try:
        label, state, *detail = value.split(":", maxsplit=2)
        return EvidenceItem(label=label.strip(), state=state.strip(), detail=detail[0].strip() if detail else None)  # type: ignore[arg-type]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Evidence must use LABEL:STATE[:DETAIL]") from exc


def cmd_checkpoint(api, argv: list[str]) -> int:
    """Render an Ariad/Maestro checkpoint orientation view."""
    parser = argparse.ArgumentParser(description="Render an Ariad/Maestro checkpoint view")
    parser.add_argument("--journey", help="Mirror journey slug. Reserved for future context lookup.")
    parser.add_argument("--checkpoint", choices=_CHECKPOINTS, required=True)
    parser.add_argument("--cv-code", default="CV?")
    parser.add_argument("--cv-title", default="Current Capability Value")
    parser.add_argument("--epic-code", default="E?")
    parser.add_argument("--epic-title", default="Current Epic")
    parser.add_argument("--epic-progress", type=_parse_epic_progress, help="Epic progress as DONE/TOTAL, for example 1/3")
    parser.add_argument("--story", default="S? Current Story", help='Story code and title, for example "S1 Checkpoint Renderer"')
    parser.add_argument("--status-sentence")
    parser.add_argument("--recommended-next")
    parser.add_argument("--release-kind", choices=("known", "emergent"))
    parser.add_argument("--release", help="Release title or emergent release note")
    parser.add_argument("--release-scope")
    parser.add_argument("--release-state")
    parser.add_argument("--release-note")
    parser.add_argument("--automated", type=_parse_evidence_item, help="Automated evidence as LABEL:STATE[:DETAIL]")
    parser.add_argument("--manual", type=_parse_evidence_item, help="Manual evidence as LABEL:STATE[:DETAIL]")
    parser.add_argument("--blocker", help="Validation blocker text")
    parser.add_argument("--risk", type=_parse_evidence_item, help="Risk posture as LABEL:STATE[:DETAIL]")
    args = parser.parse_args(argv)

    view = build_checkpoint_view_from_args(args)
    sys.stdout.write(render_checkpoint_view(view))
    return 0
