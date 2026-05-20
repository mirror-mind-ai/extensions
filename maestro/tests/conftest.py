"""Shared fixtures for the Ariad extension tests."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_EXTENSION_ROOT = Path(__file__).resolve().parents[1]
if str(_EXTENSION_ROOT) not in sys.path:
    sys.path.insert(0, str(_EXTENSION_ROOT))

from memory.db.schema import SCHEMA  # noqa: E402
from memory.extensions.api import ExtensionAPI  # noqa: E402


@pytest.fixture
def ariad_api():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    yield ExtensionAPI(extension_id="maestro", connection=conn)
    conn.close()


@pytest.fixture
def ready_project(tmp_path: Path) -> Path:
    (tmp_path / "AGENTS.md").write_text(
        "This project uses Ariad. This repository contains a local Ariad instance.\n",
        encoding="utf-8",
    )
    for rel_path in (
        "docs/process/development-guide.md",
        "docs/project/briefing.md",
        "docs/project/decisions.md",
        "docs/project/roadmap/index.md",
        "docs/product/principles.md",
    ):
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {path.stem}\n", encoding="utf-8")
    return tmp_path


def seed_journey(api: ExtensionAPI, journey_id: str, project_path: Path | None = None) -> None:
    metadata = {}
    if project_path is not None:
        metadata["project_path"] = str(project_path)
    now = datetime.now(timezone.utc).isoformat()
    api.db.execute(
        """
        INSERT INTO identity (id, layer, key, content, created_at, updated_at, metadata)
        VALUES (?, 'journey', ?, ?, ?, ?, ?)
        """,
        (
            f"journey-{journey_id}",
            journey_id,
            f"Journey {journey_id}",
            now,
            now,
            json.dumps(metadata) if metadata else None,
        ),
    )
    api.db.commit()
