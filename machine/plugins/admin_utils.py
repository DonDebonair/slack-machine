from __future__ import annotations

from typing import cast
from enum import Enum

from machine.plugins.base import MachineBasePlugin


class RoleCombinator(Enum):
    ANY = "any"
    ALL = "all"


async def role_assignments_by_role(plugin: MachineBasePlugin, role: str) -> dict[str, int]:
    if role == "root":
        users_with_role = {plugin.settings["ROOT_USER"]: 1}
    else:
        users_with_role_payload = await plugin.storage.get(f"rbac:role:{role}", shared=True)
        if users_with_role_payload is not None:
            users_with_role = cast(dict[str, int], users_with_role_payload)
        else:
            users_with_role = {}
    return users_with_role


async def matching_roles_by_user_id(plugin: MachineBasePlugin, user_id: str, roles: list[str]) -> int:
    matching_roles = 0
    for role in roles:
        assigned_roles = await role_assignments_by_role(plugin, role)
        if assigned_roles and user_id in assigned_roles:
            matching_roles += 1

    return matching_roles
