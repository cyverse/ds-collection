#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""
Provides an ansible module for creating, updating and removing iRODS users.
"""

from abc import ABC, abstractmethod
import enum
from enum import Enum
from ssl import Purpose
import ssl
from typing import Optional

from ansible.module_utils.basic import AnsibleModule

from irods.access import iRODSAccess
from irods.collection import iRODSCollection
from irods.exception import CAT_INVALID_USER, UserDoesNotExist
from irods.session import iRODSSession
from irods.user import iRODSUser


DOCUMENTATION = r'''
---
module: cyverse.ds.irods_user

short_description: This module manages iRODS users.

description: >
    This module can create or remove an iRODS user, and it can modify certain
    properties of an existing user.

version_added: "2.4"

author:
    - John Xu
    - Tony Edgin

options:
    zone:
        description: >
            This is the iRODS zone where the change is being made. It is also the zone of the user
            being managed.
        required: true
        type: str
    name:
        description: This is the username being managed.
        required: true
        type: str
    state:
        description: This indicates whether or not the user should exist.
        required: false
        choices:
            - present
            - absent
        default: present
        type: str
    force:
        description: >
            If the user has data in their home or trash folder, the user will not be removed unless
            this is set to `true`.
        type: bool
        default: false
    info:
        description: >
            This is information to set about the user. It is only meaningful when O(state) is
            V(present).
        required: false
        type: str
    password:
        description: This is the user's password. It is only meaningful when O(state) is V(present).
        required: false
        type: str
    type:
        description:
            - >
                This is the type of user, e.g., V(rodsadmin) and V(rodsuser). It is only meaningful
                when O(state) is V(present).
            - *The default when creating a user is V(rodsuser), otherwise there is no default.
        required: false
        default: rodsuser*
        type: str
    admin_user:
        description: >
            This is the iRODS username to authorize the change. This should be a rodsadmin type
            user.
        required: false
        default: rods
        type: str
    admin_password: This is the password used to authenticate O(admin_user).
        required: true
        type: str
    host:
        description: >
            This is the name of the iRODS server to connect to when making the
            change.
        required: false
        default: localhost
        type: str
    port:
        description: This is the TCP port to connect to on the iRODS server.
        required: false
        default: 1247
        type: int

requirements:
    - python-irodsclient>=0.8.2
'''

EXAMPLES = r'''
# Create iRODS user of type rodsuser
- name: Create user
  irods_user:
    zone: tempZone
    name: test_user1
    state: present
    password: fun
    admin_user: rods
    admin_password: 1234
    host: cyverse.org
    port: 1247

# Update password of test_user1
- name: Update password
  irods_user:
    zone: tempZone
    name: test_user1
    password: foo
    admin_user: rods
    admin_password: 1234

# Update info of test_user1
- name: Update info
  irods_user:
    zone: tempZone
    name: test_user1
    info: some information
    admin_password: 1234

# Update type of test_user1
- name: Update user type
  irods_user:
    zone: tempZone
    name: test_user1
    type: other_type
    admin_user: rods
    admin_password: 1234

# Remove iRODS user
- name: Remove user
  irods_user:
    zone: tempZone
    name: test_user1
    state: absent
    force: true
    admin_user: rods
    admin_password: 1234
'''

RETURN = r'''
user:
    description: This is the username of the user that was managed.
    type: str
    returned: always
'''


_ARG_SPEC = {
    "zone": {
        "type": "str",
        "required": True,
    },
    "name": {
        "type": "str",
        "required": True,
    },
    "state": {
        "type": "str",
        "choices": ["present", "absent"],
        "default": "present",
        "required": False,
    },
    "force": {
        "type": "bool",
        "default": False,
        "required": False,
    },
    "info": {
        "type": "str",
        "required": False,
    },
    "password": {
        "type": "str",
        "required": False,
        "no_log": True,
    },
    "type": {
        "type": "str",
        "required": False,
    },
    "admin_user": {
        "type": "str",
        "default": "rods",
        "required": False,
    },
    "admin_password": {
        "type": "str",
        "required": True,
        "no_log": True,
    },
    "host": {
        "type": "str",
        "default": "localhost",
        "required": False,
    },
    "port": {
        "type": "int",
        "default": 1247,
        "required": False,
    },
}


class _State(Enum):
    ABSENT = enum.auto()
    PRESENT = enum.auto()

    @classmethod
    def from_param(cls, param: str):
        """Creates a _State from its corresponding state parameter value"""
        if param.lower() == 'absent':
            return cls.ABSENT
        return cls.PRESENT


class Request:
    """This class encapsulates the parameters passed into this module. """

    def __init__(self, module_params: dict):
        self._conn_info = {
            'host': module_params['host'],
            'port': module_params['port'],
            'zone': module_params['zone'],
            'admin_username': module_params['admin_user'],
            'admin_password': module_params['admin_password']}
        self._username = module_params['name']
        self._state = _State.from_param(module_params['state'])
        self._force = module_params['force']
        self._user_info = module_params.get('info')
        self._password = module_params.get('password')
        self._user_type = module_params.get('type')

    @property
    def zone(self) -> str:
        """
        This is the iRODS zone that will be used. It is also the zone the user belongs to.
        """
        return self._conn_info['zone']

    @property
    def admin_username(self) -> str:
        """This is the rodsadmin account that authorizes the user changes."""
        return self._conn_info['admin_username']

    @property
    def admin_password(self) -> str:
        """
        This is the password that authenticates the rodsadmin account making the changes.
        """
        return self._conn_info['admin_password']

    @property
    def host(self) -> str:
        """
        This is the domain name or IP address of the iRODS server to connect to.
        """
        return self._conn_info['host']

    @property
    def port(self) -> int:
        """
        This is the TCP port iRODS uses on the server that will be connected to.
        """
        return self._conn_info['port']

    @property
    def username(self) -> str:
        """This is the user account that is being managed."""
        return self._username

    @property
    def state(self) -> _State:
        """The state of the user account after this module finishes."""
        return self._state

    @property
    def force(self) -> bool:
        """Indicates that a user removal should delete user data."""
        return self._force

    @property
    def password(self) -> Optional[str]:
        """This is the password used to authenticate the user account."""
        return self._password if self.state == _State.PRESENT else None

    @property
    def user_info(self) -> Optional[str]:
        """This is information to attach to the user account."""
        return self._user_info if self.state == _State.PRESENT else None

    @property
    def user_type(self) -> Optional[str]:
        """This is the type of user account being managed."""
        return self._user_type if self.state == _State.PRESENT else None


class Irods(ABC):
    """
    This is the interface to an object that provides required iRODS requests.

    This interface has been separated from the _IrodsImpl class so that it can be mocked for
    testing.
    """

    @abstractmethod
    def check_password(self, user: iRODSUser, password: str) -> bool:
        """
        This verifies that a given password belongs to a given user.

        Args:
            user      the iRODS user object representing the user whose password is being checked.
            password  the password to check

        Returns:
            It returns True if the password belongs to the user, otherwise it
            returns False.
        """

    @abstractmethod
    def create_user(
        self,
        username: str,
        password: Optional[str],
        info: Optional[str],
        user_type: Optional[str] = 'rodsuser'
    ) -> None:
        """
        This creates a new user account.

        Args:
            username   the username of the account
            password   an optional password that would be used to authenticate the account
            info       optional information to attach to the account
            user_type  the type of iRODS account to create
        """

    @abstractmethod
    def get_user(self, username: str) -> Optional[iRODSUser]:
        """
        This retrieves an iRODS user object for a given account.

        Args:
            username  the name of the account to retrieve

        Returns:
            If there is an account associated with the given username, it returns a iRODS user
            object for it, otherwise it returns None.
        """

    @abstractmethod
    def get_user_home(self, user: iRODSUser) -> iRODSCollection:
        """
        This retrieves a user's home collection.

        Args:
            user  the user of interest

        Returns:
            It returns an iRODS collection object.
        """

    @abstractmethod
    def get_user_trash(self, user: iRODSUser) -> iRODSCollection:
        """
        This retrieves a user's trash collection.

        Args:
            user  the user of interest

        Returns:
            It returns an iRODS collection object.
        """

    @abstractmethod
    def set_coll_perm(self, coll: iRODSCollection, perm: str) -> None:
        """
        This recursively gives the user owning the current iRODS session a given permission on a
        given collection

        Args:
            coll  the collection receiving the permission
            perm  the permission being assigned
        """


class _IrodsImpl(Irods):

    def __init__(self, request):
        self._ssl_context = ssl.create_default_context(Purpose.SERVER_AUTH)
        self._session = iRODSSession(
            host=request.host,
            port=request.port,
            zone=request.zone,
            user=request.admin_username,
            password=request.admin_password,
            ssl_context=self._ssl_context)

    def __enter__(self):
        return self

    def __exit__(self, _exn_type, _exn_value, _traceback):
        self._session.cleanup()

    def check_password(self, user, password):
        try:
            with iRODSSession(
                host=self._session.host,
                port=self._session.port,
                user=user.name,
                password=password,
                zone=self._session.zone,
                ssl_context=self._ssl_context
            ) as user_session:
                # do something to force connection
                user_session.users.get(user.name)
            return True
        except CAT_INVALID_USER:
            return False

    def create_user(self, username, password, info, user_type='rodsuser'):
        if user_type is None:
            user_type = 'rodsuser'
        user = self._session.users.create(username, user_type)
        if password is not None:
            user.modify('password', password)
        if info is not None:
            user.modify('info', info)

    def get_user(self, username):
        try:
            return self._session.users.get(username, self._session.zone)
        except UserDoesNotExist:
            return None

    def get_user_home(self, user):
        return self._session.collections.get(f"/{self._session.zone}/home/{user.name}")

    def get_user_trash(self, user):
        return self._session.collections.get(f"/{self._session.zone}/trash/home/{user.name}")

    def set_coll_perm(self, coll, perm):
        return self._session.acls.set(
            iRODSAccess(perm, coll.path, self._session.username), recursive=True, admin=True)


def _empty_collection(irods, coll):
    irods.set_coll_perm(coll, 'own')
    for child in coll.subcollections:
        child.remove(force=True)
    for obj in coll.data_objects:
        obj.unlink(force=True)


def _create_user(irods, name, user_type, password, info):
    irods.create_user(username=name, user_type=user_type, password=password, info=info)
    return True


def _ensure_user_removed(irods, user, force):
    if not user:
        return False
    if force:
        _empty_collection(irods, irods.get_user_home(user))
        _empty_collection(irods, irods.get_user_trash(user))
    user.remove()
    return True


def _update_user(irods, user, user_type, password, info):
    updated = False
    if user_type is not None and user_type != user.type:
        user.modify('type', user_type)
        updated = True
    if info is not None and info != user.info:
        user.modify('info', info)
        updated = True
    if password is not None and not irods.check_password(user, password):
        user.modify('password', password)
        updated = True
    return updated


def irods_user(request: Request, irods: Irods) -> bool:
    """
    This performs the business logic of the module.

    Args:
        request  the parameters passed into the module
        irods    the object managing the interaction with iRODS

    Returns:
        It returns True, if it made any changes to iRODS, otherwise it returns False.
    """
    user = irods.get_user(request.username)
    if request.state == _State.ABSENT:
        return _ensure_user_removed(irods, user, request.force)
    if not user:
        return _create_user(
            irods=irods,
            name=request.username,
            user_type=request.user_type,
            password=request.password,
            info=request.user_info)
    return _update_user(
        irods=irods,
        user=user,
        user_type=request.user_type,
        password=request.password,
        info=request.user_info)


def main() -> None:
    """Entrypoint of the Ansible module"""
    ansible = AnsibleModule(argument_spec=_ARG_SPEC, supports_check_mode=True)
    result = {
        'user': ansible.params['name'],
        'changed': False
    }
    if ansible.check_mode:
        ansible.exit_json(**result)
    request = Request(ansible.params)
    with _IrodsImpl(request) as irods:
        result['changed'] = irods_user(request, irods)
    ansible.exit_json(**result)


if __name__ == '__main__':
    main()
