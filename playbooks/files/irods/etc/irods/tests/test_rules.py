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
from typing import List, Optional, Tuple
from unittest import TestCase

from irods.exception import CAT_NO_ROWS_FOUND
from irods.message import RErrorStack
from irods.rule import Rule
from irods.session import iRODSSession
from paramiko import AutoAddPolicy, SSHClient
from scp import SCPClient


_IRODS_HOST = environ.get("IRODS_HOST")
_IRODS_PORT = int(environ.get("IRODS_PORT"))
_IRODS_ZONE_NAME = environ.get("IRODS_ZONE_NAME")
_IRODS_USER_NAME = environ.get("IRODS_USER_NAME")

IRODS_PASSWORD = environ.get("IRODS_PASSWORD")

_Emptied_Log = False  # pylint: disable=invalid-name


def setUpModule():  # pylint: disable=invalid-name
    """This clears the rodsLog on the iRODS catalog provider."""
    global _Emptied_Log  # pylint: disable=global-statement

    if not _Emptied_Log:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(_IRODS_HOST, password='')

        try:
            _, stdout, _ = ssh.exec_command(
                'truncate --size=0 /var/lib/irods/log/test_mode_output.log')

            _Emptied_Log = True

            if stdout.channel.recv_exit_status() != 0:
                raise RuntimeError("Failed to clear the rodsLog")
        finally:
            ssh.close()


class IrodsType(Enum):
    """This class encodes values as a given iRODS type for passing to an iRODS rule."""

    BOOLEAN = enum.auto()
    NONE = enum.auto()
    PATH = enum.auto()
    STRING = enum.auto()
    STRING_LIST = enum.auto()

    def format(self, value: any) -> Optional[str]:
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
        if self == IrodsType.NONE:
            return None
        if self == IrodsType.PATH:
            return str(value)
        if self == IrodsType.STRING:
            return f'"{value}"'
        return 'list(' + ','.join(map(IrodsType.STRING.format, value)) + ')'


class IrodsVal:
    """This holds a value to pass into an iRODS rule."""

    @staticmethod
    def boolean(val: bool):
        """
        Construct an iRODS Boolean.

        Parameters:
            val  a Boolean value

        Return:
            An _IrodsVal of type _IrodsType.BOOL
        """
        return IrodsVal(IrodsType.BOOLEAN, val)

    @staticmethod
    def none():
        """
        Construct an empty result

        Return:
            An _IrodsVal of type _IrodsType.NONE
        """
        return IrodsVal(IrodsType.NONE, None)

    @staticmethod
    def path(irods_path: str):
        """
        Construct an iRODS path.

        Parameters:
            irods_path  the value of the path to construct

        Return:
            An _IrodsVal of type _IrodsType.PATH
        """
        return IrodsVal(IrodsType.PATH, irods_path)

    @staticmethod
    def string(val: str):
        """
        Construct an iRODS string.

        Parameters:
            val  the value of the string to construct

        Return:
            An _IrodsVal of type _IrodsType.STRING
        """
        return IrodsVal(IrodsType.STRING, val)

    @staticmethod
    def string_list(val: list[str]):
        """
        Construct an iRODS list of strings

        Parameters:
            val  the python list of strings to convert

        Returns
            an _IrodsVal of type _IrodsType.STRING_LIST
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

    @classmethod
    def setUpClass(cls):
        setUpModule()

    @staticmethod
    def prep_path(irods_path: str) -> Tuple[IrodsVal.path, IrodsVal.string]:
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
        self._irods: iRODSSession = None
        self._ssh: SSHClient = None
        self._scp: SCPClient = None

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
            self._scp = SCPClient(self.ssh.get_transport())
        return self._scp

    @property
    def ssh(self) -> SSHClient:
        """provides access to an open SSH session"""
        if not self._ssh:
            self._ssh = SSHClient()
            self._ssh.set_missing_host_key_policy(AutoAddPolicy())
            self._ssh.connect(_IRODS_HOST, password='')
        return self._ssh

    def ensure_obj_absent(self, obj_path: str) -> None:
        """
        Ensures that a data object is not in iRODS

        Parameters:
            obj_path  the absolute path to the data object
        """
        try:
            self.irods.data_objects.unlink(obj_path, force=True)
        except CAT_NO_ROWS_FOUND:
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
        rule = self._mk_rule(f"writeLine('stdout', {fn}({', '.join(map(repr, args))}))")
        try:
            self.assertEqual(self._exec_rule(rule, exp_res.type), exp_res)
        except _RuleExecFailure as ref:
            self.fail(str(ref))

    def _mk_rule(self, logic):
        return Rule(
            session=self.irods,
            instance_name='irods_rule_engine_plugin-irods_rule_language-instance',
            body=logic,
            output='ruleExecOut')

    def _exec_rule(self, rule, res_type):
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
