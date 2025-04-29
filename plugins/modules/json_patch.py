#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2024 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Provides the json ansible module."""

import json
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: cyverse.ds.json_patch

short_description: This modules modifies JSON files on a managed host.

description: >
  This module can update entries in a JSON file on a managed host. If a entry is missing, it will be
  added. It only works with top level fields and only supports numbers and strings.

version_added: "2.16"

author: Tony Edgin

options:
  path:
    description: This is the absolute path to the JSON file
    type: str
    required: true
  updates:
    description: The set of updates to make
    type: list
    elements: dict
    suboptions:
      field:
        description: The name of a field to change.
        type: str
        required: true
      force:
        description: Whether or not to overwrite an existing field
        type: bool
        required: false
        default: false
      type:
        description: The JSON type of the field
        choices:
          - number
          - string
        required: false
        default: string
      value:
        description: The new value of the field.
        required: false
        default: null
    required: true
'''

EXAMPLES = r'''
- name: Add some values the iRODS environment file
  json_patch:
    path: /var/lib/irods/.irods/irods_environment.json
    updates:
      - field: irods_authentication_file
        value: /var/lib/irods/.irods/.irodsA
      - field: irods_default_number_of_transfer_threads
        type: number
        value: 4
        force: true
'''

_ARG_SPEC = {
    "path": {"type": "str", "required": True},
    "updates": {
        "type": "list",
        "elements": "dict",
        "options": {
            "field": {"type": "str", "required": True},
            "force": {"type": "bool", "required": False, "default": False},
            "type": {
                "type": "str",
                "choices": ["number", "string"],
                "required": False,
                "default": "string",
            },
            "value": {"required": False, "default": None},
        },
        "required": True,
    },
}


class _FieldUpdate:

    def __init__(self, field, force, json_type, value):
        self._field = field
        self._force = force
        if json_type == "number":
            self._value = float(value)
        else:
            self._value = str(value)

    def apply(self, json_doc) -> bool:
        """
        Ensures the field is in the json_doc and has the correct value

        Params:
            json_doc  the dictionary form of a JSON document

        Returns:
            It returns True if it modified the document, otherwise False
        """
        if self._field in json_doc and (not self._force or json_doc[self._field] == self._value):
            return False
        json_doc[self._field] = self._value
        return True


class _Request:

    def __init__(self, path, updates):
        self._json_file = Path(path)
        self._updates = []
        self._changed = False
        for update in updates:
            self._updates.append(_FieldUpdate(
                field=update['field'],
                force=update['force'],
                json_type=update['type'],
                value=update['value']))

    def perform(self) -> dict:
        """
        This performs the update

        Returns:
            It returns a dictionary suitable to pass to ansible.exit_json.
        """
        self._ensure_file_exists()
        with self._json_file.open(mode="r", encoding="utf-8") as f:
            doc = self._update(json.load(f))
        if self._changed:
            with self._json_file.open(mode="w", encoding="utf-8") as f:
                json.dump(doc, f, indent=4, sort_keys=True)
        return {'changed': self._changed}

    def _ensure_file_exists(self):
        if not self._json_file.exists():
            if not self._json_file.parent.exists():
                self._json_file.parent.mkdir(parents=True)
            self._json_file.write_text("{}", encoding='utf8')

    def _update(self, json_doc):
        for update in self._updates:
            self._changed |= update.apply(json_doc)
        return json_doc


def main() -> None:
    """Entrypoint of the Ansible module"""
    ansible = AnsibleModule(argument_spec=_ARG_SPEC)
    request = _Request(**ansible.params)
    result = request.perform()
    ansible.exit_json(**result)


if __name__ == "__main__":
    main()
