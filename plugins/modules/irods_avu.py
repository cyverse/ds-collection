#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright: © 2021, The Arizona Board of Regents
# Standard BSD License | CyVerse (see https://cyverse.org/license)

"""
This defines the irods_avu ansible module.
"""
import ssl
from ssl import Purpose
from typing import Mapping, Optional, Union
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community"
}

DOCUMENTATION = r'''
---
module: cyverse.ds.irods_avu

short_description: Manage iRODS AVU

description: >
  This module manipulates AVUs in iRODS. An AVU of a data object or resource
  can be added, set, or removed. Both "add" and "set" create a new AVU if it
  doesn't exist. However, if the entity has an AVU with the same attribute, an
  "add" will create a new AVU, while a "set" will update the existing one.

version_added: '2.9.10'

author: Tony Edgin (@tedgin)

options:
  attribute:
    description: This is the name of the attribute.
    required: true
    type: str

  value:
    description: This is the value of the attribute.
    required: true
    type: str

  units:
    description: This is the units of the value.
    default: null
    type: str

  entity_name:
    description: >
      The AVU will be attached or removed to this entity. If it is a data
      object, this should be its absolute path.
    required: true
    type: str

  entity_type:
    description: This is the type the entity.
    default: data object
    choices:
      - data object
      - resource

  state:
    description: >
      This is the desired state to achieve.
        - "set" means a single AVU is attached with this attribute.
        - "present" means that an AVU will be added as long as there isn't already one with the same attribute.
        - "absent" means that an AVU with the provided attribute and value will be removed.
        - "add" means that an AVU will be added if there isn't already one with the same attribute, value, and unit.

    default: present
    choices:
      - absent
      - add
      - present
      - set

  host:
    description: This is the FQDN or IP address of the iRODS server to connect to.
    default: localhost.localdomain
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

notes:
  - >
    In the future, it will be able to set an AVU on a collection, data object
    and user.
  - In the future, it will be able to add, remove, modify, and copy AVUs.

requirements::
  - python-irodsclient>=0.8.2
'''

EXAMPLES = r'''
---
- name: ensure a data object has a unitless AVU
  irods_avu:
    attribute: a
    value: v
    entity_name: /tempZone/home/user/file
    zone: tempZone
    password: rods

- name: ensure a resource of a remote iRODS does not have an AVU
  irods_avu:
    attribute: a
    value: v
    units: u
    state: absent
    entity_type: resource
    entity_name: demoResc
    host: provider.localdomain
    zone: tempZone
    password: rods

- name: ensure a data object on an iRODS listening on a custom port has an AVU
  irods_avu:
    attribute: a
    value: v
    units: u
    state: set
    entity_name: /tempZone/home/user/file
    port: 1250
    zone: tempZone
    password: rods

- name: ensure a dato object has an AVU connecting as a specific user
  irods_avu:
    attribute: a
    value: v
    units: u
    entity_name: /tempZone/home/user/file
    zone: tempZone
    username: user
    password: password
'''

RETURN = ''' # '''


_IRODSCLIENT_PACK_ERR: Optional[Exception] = None

try:
    from irods.data_object import iRODSDataObject
    from irods.collection import iRODSCollection
    from irods.exception import CAT_INVALID_AUTHENTICATION, \
        CAT_INVALID_CLIENT_USER, CAT_INVALID_USER, CollectionDoesNotExist, \
        DataObjectDoesNotExist, NetworkException
    from irods.meta import iRODSMeta
    from irods.resource import iRODSResource
    from irods.session import iRODSSession

except Exception as import_error:   #pylint: disable=broad-except
    _IRODSCLIENT_PACK_ERR = import_error


_IrodsEntity = Union[iRODSDataObject, iRODSResource, iRODSCollection]


class _IrodsAvuError(Exception):
    def __init__(self, message: str):
        self._message = message

    def __str__(self) -> str:
        return self._message


class _IrodsAvuAuthenticationError(_IrodsAvuError):

    def __init__(self, zone: str, user: str):
        msg_tmpl = "user '{0}' cannot be authenticated in zone '{1}'"

        super(_IrodsAvuAuthenticationError, self).__init__(
            msg_tmpl.format(user, zone))

def _ensure_avu_present(
    entity: _IrodsEntity, attribute: str, value: str, units: Optional[str]
) -> bool:

    if len(entity.metadata.get_all(attribute)) > 0:
        return False

    entity.metadata.add(attribute, value, units)
    return True

def _ensure_avu_added(
    entity: _IrodsEntity, attribute: str, value: str, units: Optional[str]
) -> bool:
    for avu in entity.metadata.get_all(attribute):
        if avu.value == value and avu.units == units:
            return False

    entity.metadata.add(attribute, value, units)
    return True


def _ensure_avu_removed(
    entity: _IrodsEntity, attribute: str, value: str, units: Optional[str]
) -> bool:
    for avu in entity.metadata.get_all(attribute):
        if avu.value == value and avu.units == units:
            entity.metadata.remove(attribute, value, units)
            return True

    return False


def _ensure_avu_set(
    entity: _IrodsEntity, attribute: str, value: str, units: Optional[str]
) -> bool:
    avus = entity.metadata.get_all(attribute)

    if len(avus) == 1 and avus[0].value == value and avus[0].units == units:
        return False

    avu = iRODSMeta(attribute, value, units)
    entity.metadata[attribute] = avu
    return True


def _get_entity(
    session: iRODSSession, entity_type: str, entity_name: str
) -> _IrodsEntity:
    if entity_type == "data object":
        try:
            return session.data_objects.get(entity_name)
        except CollectionDoesNotExist as e:
            raise _IrodsAvuError(
                f"The collection '{entity_name}' does not exist") from e
        except DataObjectDoesNotExist as e:
            raise _IrodsAvuError(
                f"The data object '{entity_name}' does not exist") from e
    elif entity_type == "resource":
        try:
            return session.resources.get(entity_name)
        except Exception as e:
            raise _IrodsAvuError(
                f"The resource '{entity_name}' does not exist") from e

    elif entity_type == "collection":
        try:
            return session.collections.get(entity_name)
        except CollectionDoesNotExist as e:
            raise _IrodsAvuError(
                f"The collection '{entity_name}' does not exist") from e
    else:
        raise _IrodsAvuError("entities of that type not supported")


def _irods_session(
    host: str, port: int, zone: str, user: str, password: str
) -> iRODSSession:
    return iRODSSession(
        host=host,
        port=port,
        zone=zone,
        user=user,
        password=password,
        ssl_context=ssl.create_default_context(Purpose.SERVER_AUTH))


def _irods_avu(
    attribute: str,
    value: str,
    units: Optional[str],
    entity_name: str,
    entity_type: str,
    state: str,
    host: str,
    port: int,
    zone: str,
    username: str,
    password: str
) -> bool:
    try:
        with _irods_session(
            host, port, zone, username, password
        ) as session:
            if not session.users.get(username, zone).type == "rodsadmin":
                raise _IrodsAvuError(
                    f"'{username}' must be a rodsadmin user")

            entity = _get_entity(session, entity_type, entity_name)

            if state == "absent":
                return _ensure_avu_removed(entity, attribute, value, units)
            elif state == "add":
                return _ensure_avu_added(entity, attribute, value, units)
            elif state == "set":
                return _ensure_avu_set(entity, attribute, value, units)
            elif state == "present":
                return _ensure_avu_present(entity, attribute, value, units)
            else:
                raise _IrodsAvuError("state not implemented")
    except CAT_INVALID_AUTHENTICATION as e:
        raise _IrodsAvuAuthenticationError(zone, username) from e
    except CAT_INVALID_CLIENT_USER as e:
        raise _IrodsAvuAuthenticationError(zone, username) from e
    except CAT_INVALID_USER as e:
        raise _IrodsAvuAuthenticationError(zone, username) from e


def _validate_params(
    params: Mapping[str, Union[str, int, Optional[str]]]
) -> None:
    if not params['host']:
        raise _IrodsAvuError("host cannot be empty")
    if not params['port']:
        raise _IrodsAvuError("port cannot be null")
    if not params['attribute']:
        raise _IrodsAvuError("attribute name cannot be empty")
    if not params['value']:
        raise _IrodsAvuError("value cannot be empty")


def _prep_module() -> AnsibleModule:
    options_spec = dict(
        attribute=dict(type='str', required=True),
        value=dict(type='str', required=True),
        units=dict(type='str', default=None),
        entity_name=dict(type='str', required=True),
        entity_type=dict(
            type='str',
            choices=["data object", "resource", "collection"],
            default="data object"),
        state=dict(
            type='str',
            choices=["absent", "present", "add", "set"],
            default="present"),
        host=dict(type='str', default="localhost.localdomain"),
        port=dict(type='int', default=1247),
        zone=dict(type='str', required=True),
        username=dict(type='str', default="rods"),
        password=dict(type='str', required=True, no_log=True))

    return AnsibleModule(argument_spec=options_spec)


def main() -> None:
    """Entrypoint of module."""
    module: AnsibleModule = _prep_module()
    if _IRODSCLIENT_PACK_ERR:
        err_msg = f"python-irodsclient issue: {_IRODSCLIENT_PACK_ERR}"
        module.fail_json(msg=err_msg)
        return

    result = dict(changed=False)

    try:
        _validate_params(module.params)
        result['changed'] = _irods_avu(**module.params)
        module.exit_json(**result)
    except _IrodsAvuError as e:
        module.fail_json(msg=str(e))
    except NetworkException as e:
        module.fail_json(msg=str(e))
    except Exception as e:    #pylint: disable=broad-except
        tmpl = "An unexpected exception of type {0} occurred. Arguments: {1!r}"
        module.fail_json(msg=tmpl.format(type(e).__name__, e.args))


if __name__ == '__main__':
    main()
