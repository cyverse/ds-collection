#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_transfer_tracking.re rule logic."""

from os import environ, path
from typing import Optional, Tuple
import unittest

import psycopg2

import test_rules
from test_rules import IrodsTestCase, IrodsType

from irods.exception import iRODSException


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class _AddtransferTest(IrodsTestCase):

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self._db_conn = None
        self._username = 'user'

    def setUp(self):
        super().setUp()
        self.ensure_user_exists(self._username)
        self._db_conn = psycopg2.connect(
            host=environ.get("PGHOST"),
            dbname=environ.get("PGDATABASE"),
            user=environ.get("PGUSER"),
            password=environ.get("PGPASSWORD"))

    def tearDown(self):
        cur = self._db_conn.cursor()  # type: ignore
        cur.execute("DELETE FROM r_transfer_totals")
        self._db_conn.close()  # type: ignore
        self.irods.users.remove(self._username)
        super().tearDown()

    @property
    def rodsuser(self) -> str:
        """The name of the rodsuser to use for testing"""
        return self._username

    def exec_addtransfer(
        self, username: str, direction: str, vol: int
    ) -> Optional[Tuple[str, int, int]]:
        """execute the rule"""
        rule = f"""
            _cyverse_transfer_tracking_addTransfer(
                '{username}', '{self.irods.zone}', '{direction}', {vol} );
        """
        self.exec_rule(self.mk_rule(rule), IrodsType.NONE)
        oid = self.irods.users.get(username).id
        cur = self._db_conn.cursor()  # type: ignore
        cur.execute(f"SELECT action, exbibytes, bytes FROM r_transfer_totals WHERE user_id = {oid}")
        return cur.fetchone()


class TestAddtransferFailure(_AddtransferTest):
    """Test how cyverse_transfer_tracking_addTransfer fails"""

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self._cwd = path.dirname(__file__)

    def setUp(self):
        super().setUp()
        mock_at_path = path.join(self._cwd, 'mocks/add-transfer')
        self.scp.put(mock_at_path, '/var/lib/irods/msiExecCmd_bin')

    def tearDown(self):
        real_at_path = path.join(
            self._cwd, '../../files/irods/var/lib/irods/msiExecCmd_bin/add-transfer')
        self.scp.put(real_at_path, '/var/lib/irods/msiExecCmd_bin')
        super().tearDown()

    def test_failure(self):
        """Verify that failure is handled correctly"""
        try:
            self.exec_addtransfer(self.rodsuser, 'in', 5)
            self.fail("failure didn't return a failure status code")
        except iRODSException:
            pass

    def test_log_msg(self):
        """Verify that a message is logged"""
        try:
            self.exec_addtransfer(self.rodsuser, 'in', 5)
        except iRODSException:
            for line in self.tail_rods_log():
                if 'add-transfer failed:' in line:
                    return
        self.fail("failure didn't log message")


class TestAddtransferSuccess(_AddtransferTest):
    """
    Test how _cyverse_transfer_tracking_addTransfer handles the various
    success modes
    """

    def test_success_download_rodsadmin(self):
        """Verify that a download not recorded when downloader is rodsadmin"""
        if self.exec_addtransfer('rods', 'out', 1):
            self.fail("recorded download for admin user")

    def test_success_download_rodsuser(self):
        """Verify that a download is recorded when downloader is rodsuser"""
        res = self.exec_addtransfer(self.rodsuser, 'out', 2)
        if not res or res != ('out', 0, 2):
            self.fail(f"failed to correctly record result for normal user: {res}")

    def test_success_upload_rodsadmin(self):
        """Verify that an upload is not recorded when uploader is rodsadmin"""
        if self.exec_addtransfer('rods', 'in', 3):
            self.fail("recorded upload by rodsadmin")

    def test_success_upload_rodsuser(self):
        """Verify that an upload is recorded when uploader is rodsuser"""
        res = self.exec_addtransfer(self.rodsuser, 'in', 4)
        if not res or res != ('in', 0, 4):
            self.fail(f"failed to correctly record result for normal user: {res}")


class PublicLogicTest(IrodsTestCase):
    """Tests of cyverse_transfer_tracking.re public rule logic"""

    @unittest.skip("not implemented")
    def test_apibulkdataobjput(self):
        """test cyverse_transfer_tracking_api_bulk_data_obj_put_post"""

    @unittest.skip("not implemented")
    def test_apidataobjget(self):
        """test cyverse_transfer_tracking_api_data_obj_get_post"""

    @unittest.skip("not implemented")
    def test_apidataobjput(self):
        """test cyverse_transfer_tracking_api_data_obj_put_post"""

    @unittest.skip("not implemented")
    def test_apidataobjread(self):
        """test cyverse_transfer_tracking_api_data_obj_read_post"""

    @unittest.skip("not implemented")
    def test_apidataobjwrite(self):
        """test cyverse_transfer_tracking_api_data_obj_write_post"""


if __name__ == "__main__":
    unittest.main()
