ALTER TABLE ext_maestro_workspace_overlays
    ADD COLUMN commit_policy TEXT NOT NULL DEFAULT 'after_validated_story';

ALTER TABLE ext_maestro_workspace_overlays
    ADD COLUMN push_policy TEXT NOT NULL DEFAULT 'ask_before_push';

ALTER TABLE ext_maestro_workspace_overlays
    ADD COLUMN worklog_policy TEXT NOT NULL DEFAULT 'meaningful_milestones';

ALTER TABLE ext_maestro_workspace_overlays
    ADD COLUMN documentation_detail_policy TEXT NOT NULL DEFAULT 'smallest_coherent_surface';

ALTER TABLE ext_maestro_workspace_overlays
    ADD COLUMN branch_policy TEXT NOT NULL DEFAULT 'project_default';

ALTER TABLE ext_maestro_workspace_overlays
    ADD COLUMN pr_policy TEXT NOT NULL DEFAULT 'project_default';
