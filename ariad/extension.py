"""Entrypoint for the Ariad extension."""

from __future__ import annotations

from src.doctor import cmd_doctor

from memory.extensions.api import ExtensionAPI


def register(api: ExtensionAPI) -> None:
    api.register_cli(
        "doctor",
        cmd_doctor,
        summary="Inspect a project and report Ariad Builder Mode readiness.",
    )
