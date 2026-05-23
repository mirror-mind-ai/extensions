"""Tests for Maestro roadmap snapshot model."""

from __future__ import annotations

import pytest

from src.roadmap import Progress, RoadmapItem, RoadmapSnapshot, nest_roadmap_items, render_roadmap_snapshot


def test_progress_computes_percent():
    progress = Progress(done=5, total=6)

    assert progress.percent == 83


def test_progress_rejects_invalid_values():
    with pytest.raises(ValueError, match="total"):
        Progress(done=0, total=0)
    with pytest.raises(ValueError, match="negative"):
        Progress(done=-1, total=3)
    with pytest.raises(ValueError, match="exceed"):
        Progress(done=4, total=3)


def test_roadmap_item_exposes_level_markers():
    assert RoadmapItem("cv", "CV2", "Ariad/Maestro Visualization", "active").level_marker == "🟪"
    assert RoadmapItem("epic", "E6", "Roadmap Snapshot", "next").level_marker == "🟦"
    assert RoadmapItem("story", "S1", "Roadmap Snapshot Contract", "planned").level_marker == "🟨"


def test_roadmap_item_exposes_status_markers():
    assert RoadmapItem("story", "S1", "Done Story", "done").status_marker == "✅"
    assert RoadmapItem("story", "S2", "Active Story", "active").status_marker == "🟡"
    assert RoadmapItem("story", "S3", "Next Story", "next").status_marker == "👉"
    assert RoadmapItem("story", "S4", "Planned Story", "planned").status_marker == "⚪"
    assert RoadmapItem("story", "S5", "Radar Story", "radar").status_marker == "🔭"
    assert RoadmapItem("story", "S6", "Blocked Story", "blocked").status_marker == "⛔"


def test_roadmap_item_rejects_unknown_level_or_status():
    with pytest.raises(ValueError, match="Unknown roadmap level"):
        RoadmapItem("theme", "T1", "Theme", "planned")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unknown roadmap status"):
        RoadmapItem("story", "S1", "Story", "green")  # type: ignore[arg-type]


def test_roadmap_snapshot_groups_items_without_parsing_markdown():
    item = RoadmapItem(
        level="cv",
        code="CV2",
        title="Ariad/Maestro Visualization",
        status="active",
        progress=Progress(done=5, total=6),
        children=(
            RoadmapItem(
                level="epic",
                code="E6",
                title="Roadmap Snapshot",
                status="next",
                progress=Progress(done=0, total=3),
                children=(RoadmapItem("story", "S1", "Roadmap Snapshot Contract", "next"),),
            ),
        ),
    )
    snapshot = RoadmapSnapshot(items=(item,))

    assert snapshot.items == (item,)
    assert snapshot.items[0].progress is not None
    assert snapshot.items[0].progress.percent == 83
    assert snapshot.items[0].children[0].status_marker == "👉"


def test_nest_roadmap_items_groups_epics_and_stories_under_nearest_parent():
    nested = nest_roadmap_items(
        (
            RoadmapItem("cv", "CV2", "Ariad/Maestro Visualization", "active"),
            RoadmapItem("epic", "E5", "Coherence Matrix", "done"),
            RoadmapItem("story", "S3", "Closeout View Integration", "done"),
            RoadmapItem("epic", "E6", "Roadmap Snapshot", "next"),
            RoadmapItem("story", "S2", "Roadmap Snapshot Renderer", "next"),
        )
    )

    assert len(nested) == 1
    assert nested[0].code == "CV2"
    assert [child.code for child in nested[0].children] == ["E5", "E6"]
    assert nested[0].children[0].children[0].code == "S3"
    assert nested[0].children[1].children[0].code == "S2"


def test_render_roadmap_snapshot_shows_hierarchy_status_and_progress():
    snapshot = RoadmapSnapshot(
        items=(
            RoadmapItem(
                level="cv",
                code="CV2",
                title="Ariad/Maestro Visualization",
                status="active",
                progress=Progress(done=5, total=6),
                children=(
                    RoadmapItem(
                        level="epic",
                        code="E5",
                        title="Coherence Matrix",
                        status="done",
                        progress=Progress(done=3, total=3),
                        children=(RoadmapItem("story", "S3", "Closeout View Integration", "done"),),
                    ),
                    RoadmapItem(
                        level="epic",
                        code="E6",
                        title="Roadmap Snapshot",
                        status="next",
                        progress=Progress(done=1, total=3),
                        children=(RoadmapItem("story", "S2", "Roadmap Snapshot Renderer", "next"),),
                    ),
                ),
            ),
        )
    )

    rendered = render_roadmap_snapshot(snapshot)

    assert "Roadmap Snapshot" in rendered
    assert "🟪 CV2  Ariad/Maestro Visualization  Epics: 5/6  ███████░ 83%  🟡 Active" in rendered
    assert "  🟦 E5  Coherence Matrix  Stories: 3/3  ████████ 100%  ✅ Done" in rendered
    assert "    🟨 S3  Closeout View Integration  ✅ Done" in rendered
    assert "  🟦 E6  Roadmap Snapshot  Stories: 1/3  ███░░░░░ 33%  👉 Next" in rendered
    assert "    🟨 S2  Roadmap Snapshot Renderer  👉 Next" in rendered


def test_render_roadmap_snapshot_handles_empty_snapshot_as_unknown():
    rendered = render_roadmap_snapshot(RoadmapSnapshot(items=()))

    assert "? No roadmap items provided" in rendered
