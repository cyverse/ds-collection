#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# © 2023 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Provides an ansible module for creating and removing iRODS collection."""

from abc import ABC, abstractmethod
from enum import Enum, auto
from os.path import basename, dirname
import ssl
from ssl import Purpose
import traceback
from typing import Optional
from ansible.module_utils.basic import AnsibleModule
from irods.access import iRODSAccess
from irods.column import Like
from irods.exception import CAT_NO_ROWS_FOUND
from irods.models import Collection, CollectionAccess, DataObject, DataAccess, User
from irods.query import SpecificQuery
from irods.session import iRODSSession


DOCUMENTATION = r'''
---
module: cyverse.ds.irods_permission

short_description: This module modifies iRODS ACLs.

description: >
    This module is able to add or remove a permission to collection or data
    object's ACL. For a collection, it is able to add or remove a permission
    recursively to the ACLs of all of the collection's members.

version_added: "2.9.0"

author:
    - John Xu
    - Tony Edgin

options:
    zone:
        description: This is the iRODS zone where the change is being made.
        required: true
        type: str
    subject:
        description: This is the username of the user receiving the permission.
        required: true
        type: str
    subject_zone:
        description: This is the iRODS zone the subject belongs to.
        required: false
        default: O(zone)
        type: str
    permission:
        description: This is the type of permission being assigned.
        required: true
        choices:
            - null
            - read
            - write
            - own
        type: str
    object:
        description:
            - This is the object receiving the permission.
            - It can be a collection or data object.
        required: true
        type: str
    recursion:
        description:
            - >
                This indicates if the permission should be assigned to only a
                collection (none), a collection and all of its contents
                (inclusive), or only the contents of a collection, excluding the
                collection (exclusive).
            - This is ignored for a data object.
        required: false
        choices:
          - none
          - inclusive
          - exclusive
        default: none
        type: str
    admin_user:
        description:
            - This is the iRODS username to authorize the change.
            - This should be a rodsadmin type user.
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
    - python-irodsclient<2.0.0
'''

EXAMPLES = r'''
- name: Ensure anonymous user has read access to required collections
  irods_permission:
    subject: anonymous
    permission: read
    object: /tempZone/home/test_collection
    host: cyverse.org
    port: 1247
    admin_user: rods
    admin_password: 1234
    zone: tempZone

- name: Give ownership of a collection to a user
  irods_permission:
    subject: test_user123
    permission: own
    object: /tempZone/home/test_collection
    host: cyverse.org
    port: 1247
    admin_user: rods
    admin_password: 1234
    zone: tempZone
'''

RETURN = r'''
perm_before:
    description:
        - >
            The permission the user has on O(object) before the module changes
            anything.
        - >
            Regardless of the value of O(recursion), only the permission of
            O(object) will be returned.
        - The possible values are V(null), V(read), V(write), and V(own).
    returned: success
    type: str
perm_after:
    description:
        - >
            The permission the user has on O(object) after the module makes any
            changes.
        - >
            Regardless of the value of O(recursion), only the permission of
            O(object) will be returned.
        - The possible values are V(null), V(read), V(write), and V(own).
    returned: changed
    type: str
'''


_ARG_SPEC = {
    "zone": {
        "type": "str",
        "required": True,
    },
    "subject": {
        "type": "str",
        "required": True,
    },
    "subject_zone": {
        "type": "str",
        "required": False,
    },
    "permission": {
        "type": "str",
        "choices": ["null", "read", "write", "own"],
        "required": True,
    },
    "object": {
        "type": "str",
        "required": True,
    },
    "recursion": {
        "type": "str",
        "choices": ["none", "inclusive", "exclusive"],
        "default": "none",
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


class _Memoize:
    class _NotEvaluated:  # pylint: disable=too-few-public-methods
        pass

    def __init__(self, generator):
        self._generator = generator
        self._result = _Memoize._NotEvaluated

    def get(self):
        """Retrieves the value, generating it if necessary"""
        if self._result == _Memoize._NotEvaluated:
            self._result = self._generator()
        return self._result

    def clear(self):
        """Removes the cached result, forcing recomputation"""
        self._result = _Memoize._NotEvaluated


class _EntityType(Enum):
    COLLECTION = auto()
    DATA_OBJECT = auto()


class _Permission(Enum):
    NULL = 1000
    READ = 1050
    WRITE = 1120
    DELETE_OBJECT = 1130  # Not officially supported in iRODS 4.2.8, but does show up
    OWN = 1200

    @classmethod
    def _missing_(cls, value):
        if value is None:
            return cls.NULL
        if not isinstance(value, str):
            return None
        for member in cls:
            if member.name == value.upper():
                return member
        return None

    def __str__(self):
        return self.name.lower()


class _Recursion(Enum):
    NONE = auto()
    INCLUSIVE = auto()
    EXCLUSIVE = auto()

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.name == value.upper():
                return member
        return None


class _User:

    def __init__(self, zone, name, session):
        self._session = session
        self._zone = zone
        self._name = name
        self._id = _Memoize(self._generate_id)

    @property
    def zone(self) -> str:
        """the authentication zone the user belongs to"""
        return self._zone

    @property
    def name(self) -> str:
        """the username of the user"""
        return self._name

    @property
    def id(self) -> Optional[int]:
        """the internal identification number of the user"""
        return self._id.get()

    def exists(self) -> bool:
        """Indicates whether or no the user exists"""
        return self.id is not None

    def _generate_id(self):
        cond = [User.name == self.name, User.zone == self.zone]
        query = self._session.query(User.id).filter(*cond)
        return query.first()[User.id] if query.first() else None


class _Result:
    def __init__(self):
        self._success = False
        self._changed = False
        self._failure_reason = ""
        self._init_perm = None
        self._final_perm = None

    def as_failure(self, reason: str = ""):
        """
        Makes this result into a failed result

        Args:
            msg  a message describing the failure

        Returns:
            the updated _Result object
        """
        self._success = False
        self._failure_reason = reason
        return self

    def as_success(self):
        """
        Makes this result into a success result

        Returns:
            the updated _Result object
        """
        self._success = True
        return self

    def made_changes(self):
        """
        Modifies the result to indicate that changes where made.

        Returns:
            the updated _Result object
        """
        self._changed = True
        return self

    @property
    def changed(self) -> bool:
        """Indicates whether or not a change was made"""
        return self._changed

    @property
    def success(self) -> bool:
        """Indicates if the operation was successful"""
        return self._success

    @property
    def failure_reason(self) -> str:
        """This may provide a reason why on operation failed"""
        return self._failure_reason

    @property
    def initial_permission(self) -> Optional[_Permission]:
        """the initial permission, if it was determined"""
        return self._init_perm

    @initial_permission.setter
    def initial_permission(self, perm: _Permission):
        self._init_perm = perm

    @property
    def final_permission(self) -> Optional[_Permission]:
        """the final permission, if it was determined"""
        return self._final_perm

    @final_permission.setter
    def final_permission(self, perm: _Permission):
        self._final_perm = perm


class _Entity:

    def __init__(self, path, session):
        self._session = session
        self._path = path
        self._type = _Memoize(self._generate_type)

    @property
    def name(self) -> str:
        """This is the base name of the entity."""
        return basename(self.path)

    @property
    def path(self) -> str:
        """This is the absolute logical path to the entity."""
        return self._path

    @property
    def parent_path(self) -> str:
        """
        This is the absolute logical path to the entity's parent collection.
        """
        if self.path == "/":
            return "/"
        return dirname(self.path)

    @property
    def type(self) -> Optional[_EntityType]:
        """This is the type of entity."""
        return self._type.get()

    def exists(self) -> bool:
        """Indicates whether or not this object exists in the iRODS zone"""
        return self.type is not None

    def _generate_type(self):
        query = self._session.query(Collection).filter(Collection.name == self.path)
        if query.first():
            return _EntityType.COLLECTION
        self._session.data_objects.get(self.path)
        return _EntityType.DATA_OBJECT


class _PermOp(ABC):

    def __init__(self, params, session):
        self._session = session
        self._subject = _User(params["subject_zone"], params["subject"], session)
        self._object = _Entity(params["object"], session)
        self._current_perm = _Memoize(self._generate_current_permission)
        self._target_perm = _Permission(params["permission"])
        self._recursion = _Recursion(params["recursion"])
        self._result = _Memoize(self._generate_result)

    @abstractmethod
    def needs_changes(self) -> bool:
        """
        This method indicates whether or not an operation needs to make changes.

        Returns:
            True is changes need to be made, otherwise False

        This method is abstract and needs to be implemented by its derived
        classes.
        """

    @property
    def subject(self) -> _User:
        """This is the user receiving permission on the object."""
        return self._subject

    @property
    def object(self) -> _Entity:
        """This is the object whose ACL is being modified."""
        return self._object

    @property
    def current_permission(self) -> _Permission:
        """This is the current permission of the object."""
        return self._current_perm.get()

    def _generate_current_permission(self):
        if not self.subject.exists() or not self.object.exists():
            return _Permission.NULL
        if self.object.type == _EntityType.COLLECTION:
            # NOTE - User.id doesn't condition correctly in this case in iRODS 4.2.8
            # conditions = [Collection.name == self.object_path, User.id == self.subject.id]
            # query = self._session.query(CollectionAccess.type).filter(*conditions)
            # if query.first():
            #     return _Permission(query.first()[CollectionAccess.type])
            sql = (
                f"SELECT access_type_id"
                f" FROM r_objt_access"
                f" WHERE object_id = ("
                f"      SELECT coll_id FROM r_coll_main WHERE coll_name = '{self.object.path}')"
                f"   AND user_id = {self.subject.id}")
            query = SpecificQuery(self._session, sql, columns=[CollectionAccess.type])
            query.register()
            try:
                for result in query:
                    return _Permission(result[CollectionAccess.type])
            except CAT_NO_ROWS_FOUND:
                return _Permission.NULL
            finally:
                query.remove()
            # NOTE - ^^^
        if self.object.type == _EntityType.DATA_OBJECT:
            conditions = [
                Collection.name == self.object.parent_path,
                DataObject.name == self.object.name,
                # NOTE - User.id doesn't condition correctly in this case in iRODS 4.2.8
                # User.id == self.subject.id
                User.name == self.subject.name,
                User.zone == self.subject.zone
                # NOTE - ^^^
            ]
            query = self._session.query(DataAccess.type).filter(*conditions)
            if query.first():
                return _Permission(query.first()[DataAccess.type])
        return _Permission.NULL

    @property
    def target_permission(self) -> _Permission:
        """This is the permission that will be set on the object."""
        return self._target_perm

    @property
    def recursion(self) -> _Recursion:
        """Indicates the type of recursion for the permission assignment."""
        if self.object.type == _EntityType.DATA_OBJECT:
            return _Recursion.NONE
        return self._recursion

    @property
    def result(self) -> _Result:
        """This is the result of the operation."""
        return self._result.get()

    def _generate_result(self):
        result = _Result()
        if not self.subject.exists():
            return result.as_failure(f"user {self.subject.name}#{self.subject.zone} does not exist")
        if not self.object.exists():
            return result.as_failure(f"object {self.object.path} does not exist")
        result.initial_permission = self.current_permission
        if self.needs_changes():
            self._update_permission()
            result.made_changes()
        result.final_permission = self.current_permission
        return result.as_success()

    def _update_permission(self):
        recursive = self.recursion != _Recursion.NONE
        access = iRODSAccess(
            str(self.target_permission),
            self.object.path,
            self.subject.name,
            self.subject.zone)
        self._session.acls.set(access, recursive=recursive, admin=True)
        if self.recursion == _Recursion.EXCLUSIVE:
            access = iRODSAccess(
                str(self.current_permission),
                self.object.path,
                self.subject.name,
                self.subject.zone)
            self._session.acls.set(access, recursive=False, admin=True)
        else:
            self._current_perm.clear()


class _PermAbsent(_PermOp):

    def needs_changes(self):
        if self.recursion == _Recursion.NONE:
            return self.current_permission != _Permission.NULL
        if self.recursion == _Recursion.INCLUSIVE:
            return self.current_permission != _Permission.NULL or self._has_accessible_members()
        return self._has_accessible_members()

    def _has_accessible_members(self):
        return (
            self._count_base_data_perms() > 0
            or self._count_sub_coll_perms() > 0
            or self._count_sub_data_perms() > 0)

    def _count_base_data_perms(self):
        cond = [
            Collection.name == self.object.path,
            DataAccess.user_id == self.subject.id,
        ]
        query = self._session.query().count(DataAccess.data_id).filter(*cond)
        return query.first()[DataAccess.data_id]

    def _count_sub_data_perms(self):
        cond = [
            Like(Collection.name, f"{self.object.path}/%"),
            DataAccess.user_id == self.subject.id,
        ]
        query = self._session.query().count(DataAccess.data_id).filter(*cond)
        return query.first()[DataAccess.data_id]

    def _count_sub_coll_perms(self):
        cond = [
            Like(Collection.name, f"{self.object.path}/%"),
            CollectionAccess.user_id == self.subject.id,
        ]
        query = self._session.query().count(CollectionAccess.access_id).filter(*cond)
        return query.first()[CollectionAccess.access_id]


class _PermPresent(_PermOp):

    def needs_changes(self):
        if self.recursion == _Recursion.NONE:
            return self.current_permission != self.target_permission
        if self.recursion == _Recursion.INCLUSIVE:
            return self.current_permission != self.target_permission or self._sub_needs_changes()
        return self._sub_needs_changes()

    def _sub_needs_changes(self):
        return (
            self._count_base_data_with_tgt_perm() != self._count_base_data()
            or self._count_sub_colls_with_tgt_perm() != self._count_sub_colls()
            or self._count_sub_data_with_tgt_perm() != self._count_sub_data())

    def _count_sub_colls(self):
        query = (
            self._session.query()
            .count(Collection.id)
            .filter(Like(Collection.name, f"{self.object.path}/%")))
        return query.first()[Collection.id]

    def _count_sub_colls_with_tgt_perm(self):
        cond = [
            Like(Collection.name, f"{self.object.path}/%"),
            CollectionAccess.type == self.target_permission.value,
            CollectionAccess.user_id == self.subject.id,
        ]
        query = self._session.query().count(Collection.id).filter(*cond)
        return query.first()[Collection.id]

    def _count_base_data(self):
        query = (
            self._session.query().count(DataObject.id).filter(Collection.name == self.object.path))
        return query.first()[DataObject.id]

    def _count_sub_data(self):
        query = (
            self._session.query()
            .count(DataObject.id)
            .filter(Like(Collection.name, f"{self.object.path}/%")))
        return query.first()[DataObject.id]

    def _count_base_data_with_tgt_perm(self):
        cond = [
            Collection.name == self.object.path,
            DataAccess.type == self.target_permission.value,
            DataAccess.user_id == self.subject.id,
        ]
        query = self._session.query().count(DataAccess.data_id).filter(*cond)
        return query.first()[DataAccess.data_id]

    def _count_sub_data_with_tgt_perm(self):
        cond = [
            Like(Collection.name, f"{self.object.path}/%"),
            DataAccess.type == self.target_permission.value,
            DataAccess.user_id == self.subject.id,
        ]
        query = self._session.query().count(DataAccess.data_id).filter(*cond)
        return query.first()[DataAccess.data_id]


class IrodsPermission(AnsibleModule):
    """Module class"""

    def __init__(self):
        super().__init__(argument_spec=_ARG_SPEC, supports_check_mode=True)
        if not self.params["subject_zone"]:
            self.params["subject_zone"] = self.params["zone"]

    def run(self) -> None:
        """performs the business logic of the module"""
        if self.check_mode:
            self.exit_json(**self._result)
            return
        try:
            with self._init_session() as session:
                action = self._select_action(session)
                result = action.result
                if result.success:
                    resp = {
                        "changed": result.changed,
                        "perm_before": str(result.initial_permission),
                        "perm_after": str(result.final_permission)}
                    self.exit_json(**resp)
                else:
                    self.fail_json(msg=result.failure_reason)
        except Exception:  # pylint: disable=broad-exception-caught
            tmpl = "An unexpected exception occurred:\n{0}"
            self.fail_json(msg=tmpl.format(traceback.format_exc()))

    def _init_session(self):
        ssl_context = ssl.create_default_context(
            purpose=Purpose.SERVER_AUTH,
            cafile=None,
            capath=None,
            cadata=None)
        ssl_settings = {"ssl_context": ssl_context}
        return iRODSSession(
            host=self.params["host"],
            port=self.params["port"],
            user=self.params["admin_user"],
            password=self.params["admin_password"],
            zone=self.params["zone"],
            **ssl_settings)

    def _select_action(self, session):
        if self.params["permission"] == "null":
            return _PermAbsent(self.params, session)
        return _PermPresent(self.params, session)


def main() -> None:
    """The entrypoint."""
    module = IrodsPermission()
    module.run()


if __name__ == "__main__":
    main()
