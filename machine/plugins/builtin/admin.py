import logging
from datetime import datetime

from machine.plugins.base import MachineBasePlugin, Message
from machine.plugins.admin_utils import role_assignments_by_role, RoleCombinator
from machine.plugins.decorators import respond_to, required_settings, require_any_role, on
from slack_sdk.models.blocks import MarkdownTextObject, SectionBlock, ImageElement

logger = logging.getLogger(__name__)


@required_settings(["ROOT_USER"])
class RBACPlugin(MachineBasePlugin):
    """Role based access control"""

    @respond_to(regex=r"^grant\s+role\s+(?P<role>\w+)\s+to\s+<@(?P<user_id>\w+)>$")
    @require_any_role(["root", "admin"])
    async def grant_role_to_user(self, msg: Message, role: str, user_id: str) -> None:
        """grant role <role> to <user>: Grant role"""
        if role == "root":
            await msg.say("Sorry, role `root` can only be granted via static configuration")
            return
        users_with_role = await role_assignments_by_role(self, role)
        users_with_role[user_id] = 1
        await self.storage.set(f"rbac:role:{role}", users_with_role, shared=True)
        await msg.say(f"Role `{role}` has been granted to <@{user_id}>")

    @respond_to(regex=r"^revoke\s+role\s+(?P<role>\w+)\s+from\s+<@(?P<user_id>\w+)>$")
    @require_any_role(["root", "admin"])
    async def revoke_role_from_user(self, msg: Message, role: str, user_id: str) -> None:
        """revoke role <role> from <user>: Revoke role"""
        users_with_role = await role_assignments_by_role(self, role)
        if user_id in users_with_role:
            del users_with_role[user_id]
            await self.storage.set(f"rbac:role:{role}", users_with_role, shared=True)
            await msg.say(f"Role `{role}` has been revoked from <@{user_id}>")
        else:
            await msg.say(f"Role <@{user_id}> does not have role `{role}`")

    @respond_to(regex=r"^who\s+has\s+role\s+(?P<role>\w+)")
    @require_any_role(["root", "admin"])
    async def who_has_role(self, msg: Message, role: str) -> None:
        """who has role <role>: List users with role"""
        users_with_role = await role_assignments_by_role(self, role)
        if len(users_with_role):
            users_string = ", ".join([f"<@{user_id}>" for user_id in users_with_role.keys()])
            await msg.say(f"Role `{role}` has been granted to {users_string}")
        else:
            await msg.say(f"No one have been assigned role `{role}`")

    @on("unauthorized-access")
    async def notify_admins(self, message: Message, required_roles: list[str], combinator: RoleCombinator) -> None:
        now = datetime.now().isoformat()
        roots = await role_assignments_by_role(self, "root")
        admins = await role_assignments_by_role(self, "admin")
        title = "*Attempt to execute unauthorized command*"
        role_string = ", ".join([f"`{role}`" for role in required_roles])
        full_message = (
            f"*User*: {message.at_sender}\n\n*Command:*\n```{message.text}```\n\n*When:*\n{now}\n\n*Missing"
            f" roles:*\n{combinator.value.title()} of: {role_string}"
        )
        blocks = [
            SectionBlock(text=MarkdownTextObject(text=title)),
            SectionBlock(
                text=MarkdownTextObject(text=full_message),
                accessory=ImageElement(
                    image_url=(
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/156px-Warning.svg.png"
                    ),
                    alt_text="Warning",
                ),
            ),
        ]

        admins_to_be_notified = {**admins, **roots}
        for user_id in admins_to_be_notified:
            await self.send_dm(
                user_id,
                title,
                blocks=blocks,
            )
