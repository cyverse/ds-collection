#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_transfer_tracking.re rule logic."""

from os import environ
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

    def test_success_download_rodsadmin(self):
        """Verify that an download not recorded when downloader is rodsadmin"""
        rule = self.mk_rule(
            f"_cyverse_transfer_tracking_addTransfer('rods', '{self.irods.zone}', 'out', 1)")
        self.exec_rule(rule, IrodsType.NONE)
        oid = self.irods.users.get('rods').id
        with psycopg2.connect(
            host=environ.get("PGHOST"),
            dbname=environ.get("PGDATABASE"),
            user=environ.get("PGUSER"),
            password=environ.get("PGPASSWORD")
        ) as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM r_transfer_totals WHERE user_id = {oid}")
            if cur.fetchone():
                self.fail("recorded transfer for admin user")

    def test_success_download_rodsuser(self):
        """Verify that an download is recorded when downloader is rodsuser"""
        with psycopg2.connect(
            host=environ.get("PGHOST"),
            dbname=environ.get("PGDATABASE"),
            user=environ.get("PGUSER"),
            password=environ.get("PGPASSWORD")
        ) as conn:
            username = 'user'
            self.ensure_user_exists(username)
            try:
                rule_src = f"""
                    _cyverse_transfer_tracking_addTransfer(
                        '{username}', '{self.irods.zone}', 'out', 1)
                """
                self.exec_rule(self.mk_rule(rule_src), IrodsType.NONE)
                oid = self.irods.users.get(username).id
                cur = conn.cursor()
                cur.execute(
                    f"SELECT action, exbibytes, bytes FROM r_transfer_totals WHERE user_id = {oid}")
                res = cur.fetchone()
                if not res or res != ('out', 0, 1):
                    self.fail("failed to correctly record result for normal user")
            finally:
                self.irods.users.remove(username)
                cur = conn.cursor()
                cur.execute("DELETE FROM r_transfer_totals")

    @unittest.skip("not implemented")
    def test_success_upload_rodsadmin(self):
        """Verify that an upload not recorded when uploader is rodsadmin"""

    @unittest.skip("not implemented")
    def test_success_upload_rodsuser(self):
        """Verify that an upload is recorded when uploader is rodsuser"""

    @unittest.skip("not implemented")
    def test_failure(self):
        """Verify that failure is handled correctly"""


@test_rules.unimplemented
class PublicLogicTest(IrodsTestCase):
    """Tests of cyverse_transfer_tracking.re public rule logic"""


if __name__ == "__main__":
    unittest.main()
