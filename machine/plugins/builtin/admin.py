import logging
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to, required_settings, require_any_role

logger = logging.getLogger(__name__)


def role_assignments_by_role(self, role):
    roles = self.storage.get(f'rbac:role:{role}', shared=True)
    roles = roles or {}
    if role == 'root':
        roles = {
            self.settings['RBAC_ROLE_ROOT']: 1
        }
    return roles


def matching_roles_by_user_id(self, user_id, roles):
    matching_roles = 0
    for role in roles:
        assigned_roles = role_assignments_by_role(self, role)
        if assigned_roles and user_id in assigned_roles:
            matching_roles += 1

    return matching_roles


def notify_admins(self, title, message, icon='warning', color='#ff0000'):
    roots  = role_assignments_by_role(self, 'root')
    admins = role_assignments_by_role(self, 'admin')

    admins_to_be_notified = {**admins, **roots}
    for user_id in admins_to_be_notified:
        self.send_dm(
            user_id, f':{icon}: *{title}*', attachments=[{
                "color": color,
                "text": message
            }]
        )


@required_settings(['RBAC_ROLE_ROOT'])
class RBACPlugin(MachineBasePlugin):
    """Role based access control"""

    @respond_to(regex=r'^grant\s+role\s+(?P<role>\w+)\s+to\s+<@(?P<user_id>\w+)>$')
    @require_any_role(['root', 'admin'])
    def grant_role_to_user(self, msg, role, user_id):
        """grant role <role> to <user>: Grant role"""
        if role == 'root':
            msg.say("Sorry, role `root` can only be granted via static configuration")
            return
        roles = role_assignments_by_role(self, role)
        roles[user_id] = 1
        self.storage.set(f'rbac:role:{role}', roles, shared=True)
        msg.say(f'Role `{role}` has been granted to <@{user_id}>')

    @respond_to(regex=r'^revoke\s+role\s+(?P<role>\w+)\s+from\s+<@(?P<user_id>\w+)>$')
    @require_any_role(['root', 'admin'])
    def revoke_role_from_user(self, msg, role, user_id):
        """revoke role <role> from <user>: Revoke role"""
        assigned_roles = role_assignments_by_role(self, role)
        if user_id in assigned_roles:
            del assigned_roles[user_id]
            self.storage.set(f'rbac:role:{role}', assigned_roles, shared=True)
            msg.say(f'Role `{role}` has been revoked from <@{user_id}>')
        else:
            msg.say(f'Role <@{user_id}> does not have role `{role}`')

    @respond_to(regex=r'^who\s+has\s+role\s+(?P<role>\w+)')
    @require_any_role(['root', 'admin'])
    def who_has_role(self, msg, role):
        """who has role <role>: List users with role"""
        assigned_roles = role_assignments_by_role(self, role)
        if len(assigned_roles):
            msg.say(
                f'Role `{role}` has been granted to {", ".join([f"<@{user_id}>" for user_id in assigned_roles.keys()])}'
            )
        else:
            msg.say(f'No one have been assigned role `{role}`')
