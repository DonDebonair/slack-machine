import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.builtin.admin_utils import role_assignments_by_role
from machine.plugins.decorators import respond_to, required_settings, require_any_role

logger = logging.getLogger(__name__)


@required_settings(['ROOT_USER'])
class RBACPlugin(MachineBasePlugin):
    """Role based access control"""

    @respond_to(regex=r'^grant\s+role\s+(?P<role>\w+)\s+to\s+<@(?P<user_id>\w+)>$')
    @require_any_role(['root', 'admin'])
    def grant_role_to_user(self, msg, role, user_id):
        """grant role <role> to <user>: Grant role"""
        if role == 'root':
            msg.say("Sorry, role `root` can only be granted via static configuration")
            return
        users_with_role = role_assignments_by_role(self, role)
        users_with_role[user_id] = 1
        self.storage.set(f'rbac:role:{role}', users_with_role, shared=True)
        msg.say(f"Role `{role}` has been granted to <@{user_id}>")

    @respond_to(regex=r'^revoke\s+role\s+(?P<role>\w+)\s+from\s+<@(?P<user_id>\w+)>$')
    @require_any_role(['root', 'admin'])
    def revoke_role_from_user(self, msg, role, user_id):
        """revoke role <role> from <user>: Revoke role"""
        users_with_role = role_assignments_by_role(self, role)
        if user_id in users_with_role:
            del users_with_role[user_id]
            self.storage.set(f'rbac:role:{role}', users_with_role, shared=True)
            msg.say(f"Role `{role}` has been revoked from <@{user_id}>")
        else:
            msg.say(f"Role <@{user_id}> does not have role `{role}`")

    @respond_to(regex=r'^who\s+has\s+role\s+(?P<role>\w+)')
    @require_any_role(['root', 'admin'])
    def who_has_role(self, msg, role):
        """who has role <role>: List users with role"""
        users_with_role = role_assignments_by_role(self, role)
        if len(users_with_role):
            users_string = ", ".join([f"<@{user_id}>" for user_id in users_with_role.keys()])
            msg.say(
                f"Role `{role}` has been granted to {users_string}"
            )
        else:
            msg.say(f"No one have been assigned role `{role}`")
