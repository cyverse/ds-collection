#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of esiil.re rule logic."""

import unittest

from irods.exception import SYS_INVALID_RESC_INPUT

import test_rules
from test_rules import IrodsTestCase


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class TestPepResourceResolveHierarchyPreEsiilResDefault(IrodsTestCase):
    """
    Test ESIIL instance of pep_resource_resolve_hierarchy_pre when the ESIIL resource is the same as
    the default resource.
    """

    def setUp(self):
        super().setUp()
        self.scp.get('/etc/irods/esiil-env.re', '/tmp/esiil-env.re')
        self.ssh.exec_command(
            "sed --in-place 's/esiil_RESC = .*/esiil_RESC = cyverse_DEFAULT_RESC/'")
        self.reload_rules()

    def tearDown(self):
        for obj in [
            "/testing/home/rods/other",
            "/testing/home/rods/esiil",
            "/testing/home/shared/esiil/other",
            "/testing/home/shared/esiil/esiil",
        ]:
            self.ensure_obj_absent(obj)
        self.update_rulebase([('esiil-env.re', '/tmp/esiil-env.re')])
        super().tearDown()

    def test_esiil_res_and_coll(self):
        """
        Verify that it allows upload when ESIIL resource is chosen and destination is a ESIIL
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/esiil/esiil", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_esiil_res_not_coll(self):
        """
        Verify that it allows upload when ESIIL resource is chosen and destination is not a ESIIL
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/esiil", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_esiil_coll(self):
        """
        Verify that it allows upload when ESIIL resource is not chosen and destination is a ESIIL
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when ESIIL resource is not chosen and destination is not a
        ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/esiil/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


class TestPepResourceResolveHierarchyPreEsiilResNotDefault(IrodsTestCase):
    """
    Test ESIIL instance of pep_resource_resolve_hierarchy_pre when the ESIIL resource isn't the same
    as the default resource.
    """

    def tearDown(self):
        for obj in [
            "/testing/home/rods/other",
            "/testing/home/rods/esiil",
            "/testing/home/shared/esiil/other",
            "/testing/home/shared/esiil/esiil",
        ]:
            self.ensure_obj_absent(obj)
        super().tearDown()

    def test_esiil_res_and_coll(self):
        """
        Verify that it allows upload when ESIIL resource is chosen and destination is a ESIIL
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/esiil/esiil", resource="esiilRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_esiil_res_not_coll(self):
        """
        Verify that it forbids upload when ESIIL resource is chosen and destination is not a ESIIL
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/esiil", resource="esiilRes")
            self.fail()
        except SYS_INVALID_RESC_INPUT:
            pass

    def test_not_res_esiil_coll(self):
        """
        Verify that it allows upload when ESIIL resource is not chosen and destination is a ESIIL
        collection.
        """
        try:
            self.irods.data_objects.create(
                "/testing/home/shared/esiil/other", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when ESIIL resource is not chosen and destination is not a
        ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


if __name__ == "__main__":
    unittest.main()
