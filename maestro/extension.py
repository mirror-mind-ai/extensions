"""Entrypoint for the Ariad extension."""

from __future__ import annotations

from src.adopt import cmd_adopt
from src.doctor import cmd_doctor
from src.init import cmd_init
from src.update import cmd_update

from memory.extensions.api import ExtensionAPI


def register(api: ExtensionAPI) -> None:
    api.register_cli(
        "doctor",
        cmd_doctor,
        summary="Inspect a project and report Ariad Builder Mode readiness.",
    )
    api.register_cli(
        "adopt",
        cmd_adopt,
        summary="Adopt Ariad in a project by copying missing templates safely.",
    )
    api.register_cli(
        "init",
        cmd_init,
        summary="Initialize a project with Ariad templates.",
    )
    api.register_cli(
        "update",
        cmd_update,
        summary="Compare a local Ariad instance to canonical templates.",
    )
