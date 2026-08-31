#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright: © 2025, The Arizona Board of Regents
# Standard BSD License | CyVerse (see https://cyverse.org/license)

"""Provide irods_unixfilesystem_resource Ansible module"""

from ansible.module_utils.basic import AnsibleModule

from irods.exception import ResourceDoesNotExist
from irods.resource import iRODSResource
from irods.session import iRODSSession


DOCUMENTATION = r"""
---
module: cyverse.ds.irods_unixfilesystem_resource

short_description: Create an iRODS Unix filesystem storage resource

version added: "2.11.11"

description: >
  An ansible module for creating an iRODS Unix filesystem storage resource. The
  status will be set only and free space will be initialized only if the
  resource is created.

options:
  name:
    description: the name of the resource
    required: true
    type: str

  host:
    description: >
      the identity of the resource server that will host this resource
    required: true
    type: str

  vault:
    description: the absolute path to the root directory of the vault
    required: true
    type: path

  context:
    description: any context to attach to this resource
    required: false
    type: str

  status:
    description: starting status 'up' or 'down'
    required: false
    default: "up"
    type: str

  port:
    description: This is the TCP port to connect to.
    default: 1247
    type: int

  zone:
    description: This is the local zone served by iRODS.
    required: true
    type: str

  username:
    description: This is the iRODS rodsadmin account used when connecting.
    default: rods
    type: str

  password:
    description: This is the password used to authenticate the iRODS account.
    required: true
    type: str

requirements:
  - python-irodsclient

author: Fenn Garnett (@Fennersteel)
"""


class _IRODSError(Exception):

    def __init__(self, message, cause=None):
        super().__init__()
        self._message = message
        self._cause = cause

    def __str__(self):
        return self._message

    @property
    def cause(self):
        """the exception causing of the error"""
        return self._cause


class IRODSUnixResourceModule:  # pylint: disable=too-few-public-methods
    """
    Module class
    """

    def __init__(self):
        """
        Initialize the module
        """
        module_args = {
            "name": {
                "type": "str",
                "required": True,
            },
            "host": {
                "type": "str",
                "required": True,
            },
            "vault": {
                "type": "path",
                "required": True,
            },
            "context": {
                "type": "str",
                "required": False,
                "default": "",
            },
            "status": {
                "type": "str",
                "required": False,
                "default": "up",
            },
            "port": {
                "type": "int",
                "required": False,
                "default": 1247,
            },
            "zone": {
                "type": "str",
                "required": True,
            },
            "username": {
                "type": "str",
                "required": False,
                "default": "rods",
            },
            "password": {
                "type": "str",
                "required": True,
                "no_log": True,
            },
        }
        self._module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
        self._result = {
            "changed": False,
            "response": "",
            "exc": "",
            "exc_msg": "",
        }

    def run_module(self) -> None:
        """
        Main module operative function
        """
        if self._module.check_mode:
            self._module.exit_json(**self._result)
            return
        try:
            with self._init_session() as session:
                self._ensure_resource_created(session)
            self._module.exit_json(**self._result)
        except _IRODSError as err:
            if err.cause:
                self._result["exc"] = type(err.cause).__name__
                self._result["exc_msg"] = str(err.cause)
            fail_msg = "\n".join(
                filter(lambda x: x != "", [str(err), str(self._result["exc_msg"])]))
            self._module.fail_json(msg=fail_msg, **self._result)

    def _init_session(self):
        try:
            return iRODSSession(
                host=self._module.params["host"],  # pyright: ignore[reportArgumentType]
                port=self._module.params["port"],  # pyright: ignore[reportArgumentType]
                zone=self._module.params["zone"],  # pyright: ignore[reportArgumentType]
                user=self._module.params["username"],  # pyright: ignore[reportArgumentType]
                password=self._module.params["password"],  # pyright: ignore[reportArgumentType]
            )
        except Exception as exc:  # pylint: disable=broad-except
            raise _IRODSError(  # pylint: disable=raise-missing-from
                message="unable to connect to iRODS server", cause=exc)

    def _ensure_resource_created(self, session):
        if self._resource_exists(session):
            self._verify_resource_same(session)
        else:
            self._create_resource(session)

    def _create_resource(self, session: iRODSSession) -> None:
        try:
            session.resources.create(
                name=self._module.params["name"],  # pyright: ignore[reportArgumentType]
                resource_type="unixfilesystem",
                host=self._module.params["host"],  # pyright: ignore[reportArgumentType]
                path=self._module.params["vault"],  # pyright: ignore[reportArgumentType]
                context=self._module.params["context"],  # pyright: ignore[reportArgumentType]
            )
            session.resources.modify(
                name=self._module.params["name"],  # pyright: ignore[reportArgumentType]
                attribute="status",
                value=self._module.params["status"],  # pyright: ignore[reportArgumentType]
            )
            self._result["changed"] = True
        except Exception as exc:  # pylint: disable=broad-except
            msg = "unable to create resource"
            try:
                if self._resource_exists(session):
                    session.resources.remove(self._module.params["name"])  # pyright: ignore[reportArgumentType] # noqa: E501 # pylint: disable=line-too-long
            except Exception:  # pylint: disable=broad-except
                msg = "unable to fully create resource"
            raise _IRODSError(message=msg, cause=exc)  # pylint: disable=raise-missing-from # noqa

    def _resource_exists(self, session):
        try:
            session.resources.get(self._module.params["name"])  # pyright: ignore[reportArgumentType] # noqa: E501 # pylint: disable=line-too-long
            return True
        except ResourceDoesNotExist:
            return False

    def _verify_resource_same(self, session):
        resc: iRODSResource = session.resources.get(self._module.params["name"])  # pyright: ignore[reportArgumentType] # noqa: E501 # pylint: disable=line-too-long
        if resc.type not in ("unixfilesystem", "unix file system"):  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501 # pylint: disable=line-too-long
            raise _IRODSError("Resource already exists with different type")
        if resc.location != self._module.params["host"]:  # pyright: ignore[reportAttributeAccessIssue,reportArgumentType] # noqa: E501 # pylint: disable=line-too-long
            raise _IRODSError("Resource already exists on different host")
        if resc.vault_path != self._module.params["vault"]:  # pyright: ignore[reportAttributeAccessIssue,reportArgumentType] # noqa: E501 # pylint: disable=line-too-long
            raise _IRODSError("Resource already exists in different vault")
        if (resc.context or "") != self._module.params["context"]:  # pyright: ignore[reportAttributeAccessIssue,reportArgumentType] # noqa: E501 # pylint: disable=line-too-long
            raise _IRODSError("Resource already exists with different context")


def main():
    """
    Entrypoint of the Ansible module
    """
    IRODSUnixResourceModule().run_module()


if __name__ == "__main__":
    main()
