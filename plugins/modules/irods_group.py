#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2024 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""
Provides an ansible module for creating and removing an iRODS group.
"""

import ssl
from ansible.module_utils.basic import AnsibleModule

from irods.exception import iRODSException
from irods.models import UserGroup
from irods.session import iRODSSession


DOCUMENTATION = r"""
---
module: cyverse.ds.irods_group

short_description: Create/Remove iRODS group

version_added: "2.4"

description: Create/Remove iRODS group

options:
  group:
    description: Name of the iRODS group
    type: str
    required: true
  state:
    description: Desired state to achieve
    type: str
    choices:
      - absent
      - present
    required: true
  host:
    description: Hostname of the iRODS server
    type: str
    required: true
  port:
    description: Port of the iRODS server
    type: int
    required: true
  admin_user:
    description: Username of the admin user
    type: str
    required: true
  admin_password:
    description: Password of the admin user
    type: str
    required: true
  zone:
    description: Zone of the admin user
    type: str
    required: true

author:
  - John Xu
  - Tony Edgin
"""

EXAMPLES = r"""
# Ensure a group exist, create if not exist
- name: Add a irods group
  irods_group:
    group: some_irods_group
    state: present
    host: cyverse.org
    port: 1247
    admin_user: rods
    admin_password: 1234
    zone: tempZone

# Ensure the group with given name is absent
- name: Remove irods group
  irods_group:
    group: some_irods_group
    state: absent
    host: cyverse.org
    port: 1247
    admin_user: rods
    admin_password: 1234
    zone: tempZone
"""

RETURN = r"""
message:
  description: Performed operation
  type: str
  returned: always
group:
  description: group changed by the task
  type: str
  returned: always
"""


_ARG_SPEC = {
    'group': {
        'type': "str",
        'required': True,
    },
    'state': {
        'type': "str",
        'required': True,
        'choices': ["present", "absent"],
    },
    'host': {
        'type': "str",
        'required': True,
    },
    'port': {
        'type': "int",
        'required': True,
    },
    'admin_user': {
        'type': "str",
        'required': True,
    },
    'admin_password': {
        'type': "str",
        'no_log': True,
        'required': True,
    },
    'zone': {
        'type': "str",
        'required': True,
    },
}


class _IRODSGroupModule:

    def __init__(self):
        self._module = AnsibleModule(argument_spec=_ARG_SPEC, supports_check_mode=True)
        self._result = {
            'changed': False,
            'message': "",
            'group': self._module.params["group"],
        }
        self._session = None

    def run(self):
        """
        Entry point for module class, method to be called to run the module
        """
        if self._module.check_mode:
            self._module.exit_json(**self._result)
            return
        self._init_session()
        if self._module.params["state"] == "present":
            return self._group_present()
        return self._group_absent()

    def _init_session(self):
        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=None,
            capath=None,
            cadata=None)
        ssl_settings = {"ssl_context": ssl_context}
        self._session = iRODSSession(
            host=self._module.params["host"],
            port=self._module.params["port"],
            user=self._module.params["admin_user"],
            password=self._module.params["admin_password"],
            zone=self._module.params["zone"],
            **ssl_settings)

    def _group_absent(self):
        try:
            group_name = self._module.params["group"]
            if not self._group_exists(group_name):
                self._success("Group does not exist")
                return
            self._session.user_groups.remove(group_name)
            self._result["changed"] = True
            self._success("Group is removed")
        except iRODSException as exc:
            self._fail("Unable to remove irods group {}".format(group_name), exc)

    def _group_present(self):
        try:
            group_name = self._module.params["group"]
            if self._group_exists(group_name):
                self._success("Group already exists")
                return
            self._session.user_groups.create(group_name)
            self._result["changed"] = True
            self._success("Group is created")
        except iRODSException as exc:
            self._fail("Unable to create irods group {}".format(group_name), exc)

    def _group_exists(self, group_name):
        for result in self._session.query(UserGroup.id).filter(UserGroup.name == group_name):
            return True
        return False

    def _fail(self, msg, err=None):
        if self._session:
            self._session.cleanup()
        self._result["message"] = msg
        if err:
            self._module.fail_json(msg=msg + "\n" + str(err), **self._result)
        else:
            self._module.fail_json(msg=msg, **self._result)

    def _success(self, msg=""):
        if self._session:
            self._session.cleanup()
        if msg:
            self._result["message"] = msg
        self._module.exit_json(**self._result)


def main():
    """ Entrypoint for the ansible module """
    module = _IRODSGroupModule()
    module.run()


if __name__ == "__main__":
    main()
