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
        self.exec_rule(
            self.mk_rule("_cyverse_transfer_tracking_addTransfer('rods', 'testing', 'out', 1)"),
            IrodsType.NONE)
        oid = self.irods.users.get(self.irods.username).id
        conn = psycopg2.connect(
            host=environ.get("PGHOST"),
            dbname=environ.get("PGDATABASE"),
            user=environ.get("PGUSER"),
            password=environ.get("PGPASSWORD"))
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM r_transfer_totals WHERE user_id = {oid}")
        if cur.fetchone():
            self.fail("recorded transfer for admin user")

    @unittest.skip("not implemented")
    def test_success_download_rodsuser(self):
        """Verify that an download is recorded when downloader is rodsuser"""

    @unittest.skip("not implemented")
    def test_success_upload(self):
        """Verify that an upload is recorded correctly"""

    @unittest.skip("not implemented")
    def test_failure(self):
        """Verify that failure is handled correctly"""


@test_rules.unimplemented
class PublicLogicTest(IrodsTestCase):
    """Tests of cyverse_transfer_tracking.re public rule logic"""


if __name__ == "__main__":
    unittest.main()
