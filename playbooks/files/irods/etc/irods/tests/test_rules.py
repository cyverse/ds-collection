#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""This is a library to support testing iRODS rule logic."""

import enum
from enum import Enum
from os import environ, path
import pprint
from typing import Any, List, Optional, Tuple
from unittest import TestCase

from irods.access import iRODSAccess
from irods.exception import (
    CAT_INVALID_ARGUMENT, CAT_NO_ROWS_FOUND, CAT_SQL_ERR, CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME,
    CUT_ACTION_PROCESSED_ERR)
from irods.message import RErrorStack
from irods.rule import Rule
from irods.session import iRODSSession
from paramiko import AutoAddPolicy, SSHClient
from scp import SCPClient


_IRODS_HOST = environ.get("IRODS_HOST", "localhost")
_IRODS_PORT = int(environ.get("IRODS_PORT", 1247))
_IRODS_ZONE_NAME = environ.get("IRODS_ZONE_NAME", "tempZone")
_IRODS_USER_NAME = environ.get("IRODS_USER_NAME", "anonymous")

IRODS_PASSWORD = environ.get("IRODS_PASSWORD", "")


_Setup = False  # pylint: disable=invalid-name


def setUpModule():  # pylint: disable=invalid-name
    """Prepares the testing env for testing"""
    global _Setup  # pylint: disable=global-statement
    _place_mocks()
    clear_rods_log()
    _Setup = True


def tearDownModule():  # pylint: disable=invalid-name
    """Restores the testing env for testing"""
    global _Setup  # pylint: disable=global-statement
    _Setup = False
    _remove_mocks()


def clear_rods_log():
    """Deletes the contents of the iRODS test log"""
    with _connect_ssh() as ssh:
        _, stdout, _ = ssh.exec_command(
            'truncate --size=0 /var/lib/irods/log/test_mode_output.log')

        if stdout.channel.recv_exit_status() != 0:
            raise RuntimeError("Failed to clear the rodsLog")


def _place_mocks():
    with _connect_ssh() as ssh:
        with _connect_scp(ssh) as scp:
            mock_path = path.join(path.dirname(__file__), 'mocks/amqp-topic-send')
            scp.put(mock_path, '/var/lib/irods/msiExecCmd_bin')


def _remove_mocks():
    with _connect_ssh() as ssh:
        with _connect_scp(ssh) as scp:
            orig_path = path.join(
                path.dirname(__file__), '../../../var/lib/irods/msiExecCmd_bin/amqp-topic-send')

            scp.put(orig_path, '/var/lib/irods/msiExecCmd_bin')


def _connect_scp(ssh: SSHClient) -> SCPClient:
    transport = ssh.get_transport()

    if transport:
        return SCPClient(transport)
    else:
        raise RuntimeError("Could not get ssh transport")


def _connect_ssh() -> SSHClient:
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(_IRODS_HOST, password='')
    return ssh


class IrodsType(Enum):
    """This class encodes values as a given iRODS type for passing to an iRODS rule."""

    BOOLEAN = enum.auto()
    INTEGER = enum.auto()
    NONE = enum.auto()
    PATH = enum.auto()
    STRING = enum.auto()
    STRING_LIST = enum.auto()

    def format(self, value: Any) -> Optional[str]:
        """
        formats a value for iRODS rule base on its type

        Parameters:
            value  the value to format

        Returns:
            the formatted value
        """
        if value is None:
            return None
        if self == IrodsType.BOOLEAN:
            return str(value).lower()
        if self == IrodsType.INTEGER:
            return str(value)
        if self == IrodsType.NONE:
            return None
        if self == IrodsType.PATH:
            return str(value)
        if self == IrodsType.STRING:
            return IrodsType._fmt_str(value)
        return 'list(' + ','.join(map(IrodsType._fmt_str, value)) + ')'

    @staticmethod
    def _fmt_str(value: str) -> str:
        return f'"{value}"'


class IrodsVal:
    """This holds a value to pass into an iRODS rule."""

    @staticmethod
    def boolean(val: bool) -> "IrodsVal":
        """
        Construct an iRODS Boolean.

        Parameters:
            val  a Boolean value

        Return:
            An IrodsVal of type IrodsType.BOOLEAN
        """
        return IrodsVal(IrodsType.BOOLEAN, val)

    @staticmethod
    def integer(val: int) -> "IrodsVal":
        """
        Construct an iRODS integer.

        Parameters:
            val  an integer

        Return:
            An IrodsVal of type IrodsType.INTEGER
        """
        return IrodsVal(IrodsType.INTEGER, val)

    @staticmethod
    def none() -> "IrodsVal":
        """
        Construct an empty result

        Return:
            An IrodsVal of type IrodsType.NONE
        """
        return IrodsVal(IrodsType.NONE, None)

    @staticmethod
    def path(irods_path: str) -> "IrodsVal":
        """
        Construct an iRODS path.

        Parameters:
            irods_path  the value of the path to construct

        Return:
            An IrodsVal of type IrodsType.PATH
        """
        return IrodsVal(IrodsType.PATH, irods_path)

    @staticmethod
    def string(val: str) -> "IrodsVal":
        """
        Construct an iRODS string.

        Parameters:
            val  the value of the string to construct

        Return:
            An IrodsVal of type IrodsType.STRING
        """
        return IrodsVal(IrodsType.STRING, val)

    @staticmethod
    def string_list(val: list[str]) -> "IrodsVal":
        """
        Construct an iRODS list of strings

        Parameters:
            val  the python list of strings to convert

        Returns
            an IrodsVal of type IrodsType.STRING_LIST
        """
        return IrodsVal(IrodsType.STRING_LIST, val)

    def __init__(self, irods_type, val):
        self._type = irods_type
        self._irods_val = irods_type.format(val)

    def __eq__(self, other):
        return self.type == other.type and self._irods_val == other._irods_val

    def __repr__(self):
        return self._irods_val

    @property
    def type(self) -> IrodsType:
        """The iRODS type of the value"""
        return self._type


class _RuleExecFailure(Exception):
    pass


def unimplemented(test_case):
    """This decorator marks an test case as not being implemented. All tests will be skipped."""

    @classmethod
    def do_nothing(_):
        pass

    setattr(test_case, 'setUpClass', do_nothing)
    setattr(test_case, 'tearDownClass', do_nothing)
    setattr(test_case, 'setUp', do_nothing)
    setattr(test_case, 'tearDown', do_nothing)

    for attr in dir(test_case):
        if attr.startswith("test_"):
            delattr(test_case, attr)

    return test_case


class IrodsTestCase(TestCase):
    """This is a base class for all iRODS rule unit tests."""

    @staticmethod
    def prep_path(irods_path: str) -> Tuple[IrodsVal, IrodsVal]:
        """
        This creates a pair of encoding for a path, one as an iRODS path type, and one as a iRODS
        string type.

        Args:
            irods_path  the path to encode

        Returns:
            A tuple containing the two encodings.
        """
        return (IrodsVal.path(irods_path), IrodsVal.string(irods_path))

    def setUp(self):
        super().setUp()
        self._irods = None
        self._ssh = None
        self._scp = None

    def tearDown(self):
        if self._scp:
            self._scp.close()
        if self._ssh:
            self._ssh.close()
        if self._irods:
            self._irods.cleanup()
        super().tearDown()

    @property
    def irods(self) -> iRODSSession:
        """provides access to an open iRODS session"""
        if not self._irods:
            self._irods = iRODSSession(
                host=_IRODS_HOST,
                port=_IRODS_PORT,
                zone=_IRODS_ZONE_NAME,
                user=_IRODS_USER_NAME,
                password=IRODS_PASSWORD)
        return self._irods

    @property
    def scp(self) -> SCPClient:
        """provides access to an open SCP session"""
        if not self._scp:
            self._scp = _connect_scp(self.ssh)
        return self._scp

    @property
    def ssh(self) -> SSHClient:
        """provides access to an open SSH session"""
        if not self._ssh:
            self._ssh = _connect_ssh()
        return self._ssh

    def ensure_obj_absent(self, obj_path: str) -> None:
        """
        Ensures that a data object is not in iRODS

        Parameters:
            obj_path  the absolute path to the data object
        """
        if self.irods.data_objects.exists(obj_path):
            self.irods.acls.set(iRODSAccess('own', obj_path, 'rods'), admin=True)
            self.irods.data_objects.unlink(obj_path, force=True)

    def ensure_user_exists(self, username: str, password: Optional[str] = None) -> None:
        """
        Ensures that a user exists
        """
        try:
            if password is None:
                self.irods.users.create(username, 'rodsuser')
            else:
                self.irods.users.create_with_password(username, password)
        except CAT_SQL_ERR as e:
            if not str(e).endswith('CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME'):
                raise e
        except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            pass

    def reload_rules(self) -> None:
        """Reloads the iRODS rule engine."""
        if self._irods:
            self._irods.cleanup()
            self._irods = None
        self.ssh.exec_command("touch /etc/irods/core.re")

    def update_rulebase(self, rulebase: str, local_path: str) -> None:
        """
        Updates a rulebase on the iRODS server.

        Parameters:
            rulebase    the name of the rulebase to update
            local_path  the path to the local rulebase file relative to this module
        """
        abs_local_path = path.join(path.dirname(__file__), local_path)
        self.scp.put(abs_local_path, f'/etc/irods/{rulebase}')
        self.reload_rules()

    def fn_test(self, fn: str, args: List[IrodsVal], exp_res: IrodsVal) -> None:
        """
        Tests an iRODS rule function.

        Parameters:
            fn       the iRODS rule function under test
            args     the list of input parameters to pass to the function
            exp_res  the expected result of the function call
        """
        rule = self.mk_rule(f"writeLine('stdout', {fn}({', '.join(map(repr, args))}))")
        try:
            self.assertEqual(self.exec_rule(rule, exp_res.type), exp_res)
        except _RuleExecFailure as ref:
            self.fail(str(ref))

    def mk_rule(self, logic: str) -> Rule:
        """
        Creates an iRODS rule object

        Parameters:
            logic  the iRODS rule language logic defining the rule

        Returns:
            the rule object
        """
        return Rule(
            session=self.irods,
            instance_name='irods_rule_engine_plugin-irods_rule_language-instance',
            body=logic,
            output='ruleExecOut')

    def exec_rule(self, rule: Rule, res_type: IrodsType) -> IrodsVal:
        """
        Executes a rule.

        Parameters:
            rule      the rule to execute
            res_type  the type of iRODS value the rule returns.

        Returns:
            the result returned by the rule
        """
        output = rule.execute(r_error=(r_errs := RErrorStack()))
        if r_errs:
            raise _RuleExecFailure(pprint.pformat([vars(r) for r in r_errs]))
        if not output or len(output.MsParam_PI) == 0:
            return IrodsVal.none()
        err_buf = output.MsParam_PI[0].inOutStruct.stderrBuf.buf
        if err_buf:
            raise _RuleExecFailure(err_buf.rstrip(b'\0').decode('utf-8'))
        buf = output.MsParam_PI[0].inOutStruct.stdoutBuf.buf
        return IrodsVal(res_type, buf.rstrip(b'\0').decode('utf-8').rstrip("\n"))

    def tail_rods_log(self, num_lines: int = 0) -> list[str]:
        """
        Reads the last part of the rodsLog on the connected iRODS server.

        Parameters:
            num_lines  the number of lines to read

        Returns:
            the last num_lines of the log file
        """
        if num_lines <= 0:
            lines = "+1"
        else:
            lines = f"{num_lines}"
        _, stdout, _ = self.ssh.exec_command(
            f'tail --lines={lines} /var/lib/irods/log/test_mode_output.log')
        return stdout.read().decode().splitlines()
