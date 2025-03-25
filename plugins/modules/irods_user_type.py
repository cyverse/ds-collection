#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright: © 2025, The Arizona Board of Regents
# Standard BSD License | CyVerse (see https://cyverse.org/license)

"""the irods_user_type ansible module"""

import subprocess
from subprocess import CalledProcessError

from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community"
}

DOCUMENTATION = r'''
---
module: irods_user_type

short_description: managed iRODS user types

description: This modules can add or remove user types to an iRODS zone.

version_added: '2.16'

options:
  type:
    description: This is the label for the user type being added or removed
    type: str
    required: true

  description:
    description: the description of the user type, only applicable when state = present
    type: str
    required: false
    default: ''

  state:
    description: >
      This is the desired state to achieve. "absent" will ensure user type is not in iRODS, and
      "present" will ensure the user type is in iRODS.
    choices:
      - absent
      - present
    default: present
'''

RETURN = r'''
'''

EXAMPLES = r'''
---
- name: Ensure service user type exists
  cyverse.ds.irods_user_type:
    type: ds-service
    description: not a service
'''


_ARG_SPEC = {
    "type": {
        "type": "str",
        "required": True,
    },
    "description": {
        "type": "str",
        "required": False,
        "default": "",
    },
    "state": {
        "type": "str",
        "choices": ["absent", "present"],
        "required": False,
        "default": "present",
    },
}


class _UserExists(RuntimeError):

    def __init__(self, user_type):
        self._user_type = user_type

    def __str__(self):
        return f"user type {self._user_type} already in use for another purpose"


def main() -> None:
    """This is the entrypoint."""
    module = AnsibleModule(_ARG_SPEC)
    try:
        module.exit_json(params=module.params, changed=_perform(module.params))
    except RuntimeError as e:
        module.fail_json(msg=str(e))


def _perform(params: dict) -> bool:
    if params["state"] == "absent":
        return _ensure_absent(params["type"])

    return _ensure_present(params["type"], params["description"])


def _ensure_absent(user_type: str) -> bool:
    if not _get_type_id(user_type):
        return False

    _rm_type(user_type)
    return True


def _ensure_present(user_type: str, description: str) -> bool:
    if not _get_type_id(user_type):
        _add_type(user_type, description)
        return True

    if description != _get_description(user_type):
        raise _UserExists(user_type)

    return False


def _add_type(user_type: str, description: str) -> None:
    try:
        subprocess.run(
            f"iadmin at user_type {user_type} '' '{description}'",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=True,
            encoding='utf-8',
        )
    except CalledProcessError as e:
        raise RuntimeError(
            f"Failed to add {user_type} with description '{description}': {e.stderr.strip()}"
        ) from e


def _rm_type(user_type: str) -> None:
    try:
        subprocess.run(
            f"iadmin rt user_type {user_type}",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=True,
            encoding='utf-8',
        )
    except CalledProcessError as e:
        raise RuntimeError(f"Failed to remove {user_type}: {e.stderr.strip()}") from e


def _get_description(user_type: str) -> str:
    return _quest(
        f"select TOKEN_VALUE2 where TOKEN_NAMESPACE = 'user_type' and TOKEN_NAME = '{user_type}'")


def _get_type_id(user_type: str) -> str:
    return _quest(
        f"select TOKEN_ID where TOKEN_NAMESPACE = 'user_type' and TOKEN_NAME = '{user_type}'")


def _quest(query: str) -> str:
    result = subprocess.run(
        f"iquest --no-page %s \"{query}\"",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        check=False,
        encoding='utf-8',
    )

    if result.returncode == 0:
        return result.stdout.strip()

    if result.returncode == 1:
        return ""

    raise RuntimeError(f"iquest failed: {result.stderr.strip()}")


if __name__ == "__main__":
    main()
