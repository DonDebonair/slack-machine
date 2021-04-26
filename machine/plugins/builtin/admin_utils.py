def role_assignments_by_role(self, role):
    if role == 'root':
        users_with_role = {
            self.settings['ROOT_USER']: 1
        }
    else:
        users_with_role = self.storage.get(f'rbac:role:{role}', shared=True)
        users_with_role = users_with_role or {}
    return users_with_role


def matching_roles_by_user_id(self, user_id, roles):
    matching_roles = 0
    for role in roles:
        assigned_roles = role_assignments_by_role(self, role)
        if assigned_roles and user_id in assigned_roles:
            matching_roles += 1

    return matching_roles


def notify_admins(self, title, message, icon='warning', color='#ff0000'):
    roots = role_assignments_by_role(self, 'root')
    admins = role_assignments_by_role(self, 'admin')

    admins_to_be_notified = {**admins, **roots}
    for user_id in admins_to_be_notified:
        self.send_dm(
            user_id, f':{icon}: *{title}*', attachments=[{
                "color": color,
                "text": message
            }]
        )
