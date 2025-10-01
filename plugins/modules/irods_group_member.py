#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: © 2025, The Arizona Board of Regents
# Standard BSD License | CyVerse (see https://cyverse.org/license)

"""
Provides an ansible module for adding and removing users from an iRODS group.
"""

import ssl

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: cyverse.ds.irods_group_member

short_description: Add/Remove user from iRODS group

version_added: "2.4"

description:
    - "Add/Remove user from iRODS group, group must be present"

options:
    group:
        description:
            - Name of the iRODS group
            - Group must already be present
        required: true
    users:
        description:
            - Username of user
        required: true
    state:
        description:
            - Desired state to achieve
            - Either present or absent
        required: true
    host:
        description:
            - Hostname of the iRODS server
        required: true
    port:
        description:
            - Port of the iRODS server
        required: true
    admin_user:
        description:
            - Username of the admin user
        required: true
    admin_password:
        description:
            - Password of the admin user
        required: true
    zone:
        description:
            - Zone of the admin user
        required: true

author:
    - John Xu
'''

EXAMPLES = r'''
# Ensure the user is present in the group (group must already exist)
- name: Add user to group
  irods_group_member:
    group: some_irods_group
    users:
        - one_user
    state: present
    host: cyverse.org
    port: 1247
    admin_user: rods
    admin_password: 1234
    zone: tempZone

# Ensure the user is absent from the group (group must already exist)
- name: Remove user to group
  irods_group_member:
    group: some_irods_group
    users:
        - one_user
    state: absent
    host: cyverse.org
    port: 1247
    admin_user: rods
    admin_password: 1234
    zone: tempZone
'''

RETURN = r'''
message:
    description: Performed operation
    type: str
    returned: always
users:
    description: users changed by the task
    type: list
    returned: always
'''

try:
    USE_IRODS_CLIENT = True
    from irods.session import iRODSSession
    from irods.models import User, Group
except ImportError:
    USE_IRODS_CLIENT = False


class IRODSGroupModule:
    """
    Module class
    """
    def __init__(self):
        """
        Initialize the module
        """
        self.module_args = {
            "group": {
                "type": "str",
                "required": True,
            },
            "users": {
                "type": "list",
                "elements": "str",
                "required": True,
            },
            "state": {
                "type": "str",
                "required": True,
                "choices": [
                    "present",
                    "absent",
                ],
            },
            "host": {
                "type": "str",
                "required": True,
            },
            "port": {
                "type": "int",
                "required": True,
            },
            "admin_user": {
                "type": "str",
                "no_log": True,
                "required": True,
            },
            "admin_password": {
                "type": "str",
                "no_log": True,
                "required": True,
            },
            "zone": {
                "type": "str",
                "required": True,
            },
        }
        self.result = {
            "changed": False,
            "message": "",
            "users": [],
        }

        # init module
        self.module = AnsibleModule(
            argument_spec=self.module_args,
            supports_check_mode=True
        )

        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None,
            cadata=None)
        ssl_settings = {"ssl_context": ssl_context}
        self.session = iRODSSession(
            host=self.module.params["host"],  # pyright: ignore[reportArgumentType]
            port=self.module.params["port"],  # pyright: ignore[reportArgumentType]
            user=self.module.params["admin_user"],  # pyright: ignore[reportArgumentType]
            password=self.module.params["admin_password"],  # pyright: ignore[reportArgumentType]
            zone=self.module.params["zone"],  # pyright: ignore[reportArgumentType]
            **ssl_settings)  # pyright: ignore[reportArgumentType]

    def run(self):
        """
        Entry point for module class, method to be called to run the module
        """

        # check param and env
        self.sanity_check()

        # only-check mode
        if self.module.check_mode:
            self.module.exit_json(**self.result)

        action = self.select_action()
        action()

    def _fail(self, msg, err=None):
        """
        Failure routine, called when operation failed
        """

        if self.session:
            self.session.cleanup()

        if err:
            self.module.fail_json(msg=msg + "\n" + str(err), **self.result)
        else:
            self.module.fail_json(msg=msg, **self.result)

    def _success(self, msg=""):
        """
        Success routine, called when operation succeeds
        """
        if msg:
            self.result["message"] = msg
        self.module.exit_json(**self.result)

    def sanity_check(self):
        """
        Check if python-irodsclient is installed
        """
        # python-irodsclient is required at this point
        if not USE_IRODS_CLIENT:
            self._fail("python-irodsclient not installed")

    def select_action(self):
        """
        Dispatch action according to the argument passed to the module
        """
        if self.module.params["state"] == "present":  # pyright: ignore[reportArgumentType]
            return self.member_present
        return self.member_absent

    def member_present(self):
        """
        Ensure a user exist in an iRODS group, add the user to the group
        if missing.
        The user and the group must already exists, module will fail if the
        user is missing.
        """
        group_name = self.module.params["group"]  # pyright: ignore[reportArgumentType]
        users = set(self.module.params["users"])  # pyright: ignore[reportArgumentType]
        self.result["users"] = []

        # group must already exist
        if not self._group_exist(group_name):
            self._fail("Group must already exist")

        # check if users are in the group
        users = [username for username in users
                 if not self._is_user_in_group(group_name, username)]

        # if all users present
        if not users:
            self._success()

        # add users
        for username in users:
            self._add_user_to_group(group_name, username)
            self.result["users"].append(username)

        users_remain_absent = [username for username in users if not
                               self._is_user_in_group(group_name, username)]
        if not users_remain_absent:
            self.result["users"] = list(users)
            self._success("All specified user(s) are added to the group")
        else:
            self.result["users"] = users_remain_absent
            self._fail("Specified user(s) not in group after adding")

    def member_absent(self):
        """
        Ensure a user is absent from an iRODS group, remove the user from
        group if necessary.
        The iRODS group must exist, module will fail if absent.
        """
        group_name = self.module.params["group"]  # pyright: ignore[reportArgumentType]
        users = set(self.module.params["users"])  # pyright: ignore[reportArgumentType]
        self.result["users"] = []

        # group must already exist
        if not self._group_exist(group_name):
            self._fail("Group must already exist")

        # check if users are in the group
        users = {username for username in users if
                 self._is_user_in_group(group_name, username)}

        # if all users absent
        if not users:
            self._success()

        # remove users from group
        for username in users:
            self._remove_user_from_group(group_name, username)
            self.result["users"].append(username)

        users_still_exist = [username for username in users
                             if self._is_user_in_group(group_name, username)]
        if not users_still_exist:
            self.result["users"] = list(users)
            self._success("All specified user(s) are removed from the group")
        else:
            self.result["users"] = users_still_exist
            self._fail("Specified user(s) remain in group after removal")

    def _add_user_to_group(self, group_name, username):
        """
        Add a user to an iRODS group, fail if unable to add
        """
        self.session.groups.addmember(group_name, username)  # pyright: ignore[reportOptionalMemberAccess] # noqa: E501 # pylint: disable=line-too-long
        self.result["changed"] = True

    def _remove_user_from_group(self, group_name, username):
        """
        Remove a user from an iRODS group, fail if unable to remove
        """
        self.session.groups.removemember(group_name, username)  # pyright: ignore[reportOptionalMemberAccess] # noqa: E501 # pylint: disable=line-too-long
        self.result["changed"] = True

    def _is_user_in_group(self, group_name, username):
        """
        Check if an user is in the iRODS group
        """
        query = self.session.query(User.name, Group.name)
        for result in query:
            if group_name == result[Group.name] and username == result[User.name]:
                return True
        return False

    def _group_exist(self, group_name):
        """
        Check if an iRODS group with given name exist
        """
        query = self.session.query(Group.name)
        for result in query:
            if group_name == result[Group.name]:
                return True
        return False


def main():
    """
    Entrypoint for the ansible module
    """
    module = IRODSGroupModule()
    module.run()


if __name__ == "__main__":
    main()
