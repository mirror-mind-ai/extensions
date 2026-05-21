CREATE TABLE IF NOT EXISTS ext_maestro_workspace_overlays (
    journey_id TEXT PRIMARY KEY,
    ariad_root TEXT NOT NULL,
    contract_mode TEXT NOT NULL DEFAULT 'workspace_overlay',
    repo_contract_policy TEXT NOT NULL DEFAULT 'do_not_modify',
    doc_update_policy TEXT NOT NULL DEFAULT 'project_relevant_only',
    checkpoint_policy TEXT NOT NULL DEFAULT 'ariad_full',
    validation_policy TEXT NOT NULL DEFAULT 'required',
    project_path_snapshot TEXT,
    notes TEXT,
    enabled_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
