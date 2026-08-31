#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_transfer_tracking.re rule logic."""

from os import environ
from typing import Optional, Tuple
import unittest

import psycopg2

import test_rules
from test_rules import IrodsTestCase, IrodsType


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class AddtransferTest(IrodsTestCase):
    """Tests of _cyverse_transfer_tracking_addTransfer"""

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self._db_conn = None

    def setUp(self):
        super().setUp()
        self._db_conn = psycopg2.connect(
            host=environ.get("PGHOST"),
            dbname=environ.get("PGDATABASE"),
            user=environ.get("PGUSER"),
            password=environ.get("PGPASSWORD"))

    def tearDown(self):
        cur = self._db_conn.cursor()  # type: ignore
        cur.execute("DELETE FROM r_transfer_totals")
        self._db_conn.close()  # type: ignore
        super().tearDown()

    def test_success_download_rodsadmin(self):
        """Verify that an download not recorded when downloader is rodsadmin"""
        if self._run_test('rods', 'out', 1):
            self.fail("recorded download for admin user")

    def test_success_download_rodsuser(self):
        """Verify that an download is recorded when downloader is rodsuser"""
        username = 'user'
        self.ensure_user_exists(username)
        try:
            res = self._run_test(username, 'out', 2)
            if not res or res != ('out', 0, 2):
                self.fail(f"failed to correctly record result for normal user: {res}")
        finally:
            self.irods.users.remove(username)

    def test_success_upload_rodsadmin(self):
        """Verify that an upload is not recorded when uploader is rodsadmin"""
        if self._run_test('rods', 'in', 3):
            self.fail("recorded upload by rodsadmin")

    def test_success_upload_rodsuser(self):
        """Verify that an upload is recorded when uploader is rodsuser"""
        username = 'user'
        self.ensure_user_exists(username)
        try:
            res = self._run_test(username, 'in', 4)
            if not res or res != ('in', 0, 4):
                self.fail(f"failed to correctly record result for normal user: {res}")
        finally:
            self.irods.users.remove(username)

    @unittest.skip("not implemented")
    def test_failure(self):
        """Verify that failure is handled correctly"""

    def _run_test(self, username: str, direction: str, vol: int) -> Optional[Tuple[str, int, int]]:
        rule = f"""
            _cyverse_transfer_tracking_addTransfer(
                '{username}', '{self.irods.zone}', '{direction}', {vol} );
        """
        self.exec_rule(self.mk_rule(rule), IrodsType.NONE)
        oid = self.irods.users.get(username).id
        cur = self._db_conn.cursor()  # type: ignore
        cur.execute(f"SELECT action, exbibytes, bytes FROM r_transfer_totals WHERE user_id = {oid}")
        return cur.fetchone()


@test_rules.unimplemented
class PublicLogicTest(IrodsTestCase):
    """Tests of cyverse_transfer_tracking.re public rule logic"""


if __name__ == "__main__":
    unittest.main()
