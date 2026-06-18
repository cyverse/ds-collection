#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of ncems.re rule logic."""

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


class TestPepResourceResolveHierarchyPreNcemsResDefault(IrodsTestCase):
    """
    Test NCEMS instance of pep_resource_resolve_hierarchy_pre when the NCEMS resource is the same as
    the default resource.
    """

    def setUp(self):
        super().setUp()
        self.scp.get('/etc/irods/ncems-env.re', '/tmp/ncems-env.re')
        self.ssh.exec_command(
            "sed --in-place 's/ncems_RESC = .*/ncems_RESC = cyverse_DEFAULT_RESC/'")
        self.reload_rules()

    def tearDown(self):
        for obj in [
            "/testing/home/rods/other",
            "/testing/home/rods/ncems",
            "/testing/home/shared/ncems/other",
            "/testing/home/shared/ncems/ncems",
        ]:
            self.ensure_obj_absent(obj)
        self.update_rulebase([('ncems-env.re', '/tmp/ncems-env.re')])
        super().tearDown()

    def test_ncems_res_and_coll(self):
        """
        Verify that it allows upload when NCEMS resource is chosen and destination is a NCEMS
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/ncems/ncems", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_ncems_res_not_coll(self):
        """
        Verify that it allows upload when NCEMS resource is chosen and destination is not a NCEMS
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/ncems", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_ncems_coll(self):
        """
        Verify that it allows upload when NCEMS resource is not chosen and destination is a NCEMS
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when NCEMS resource is not chosen and destination is not a
        NCEMS collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/ncems/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


class TestPepResourceResolveHierarchyPreNcemsResNotDefault(IrodsTestCase):
    """
    Test NCEMS instance of pep_resource_resolve_hierarchy_pre when the NCEMS resource isn't the same
    as the default resource.
    """

    def tearDown(self):
        for obj in [
            "/testing/home/rods/other",
            "/testing/home/rods/ncems",
            "/testing/home/shared/ncems/other",
            "/testing/home/shared/ncems/ncems",
        ]:
            self.ensure_obj_absent(obj)
        super().tearDown()

    def test_ncems_res_and_coll(self):
        """
        Verify that it allows upload when NCEMS resource is chosen and destination is an NCEMS
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/ncems/ncems", resource="ncemsRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_ncems_res_not_coll(self):
        """
        Verify that it forbids upload when NCEMS resource is chosen and destination is not an NCEMS
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/ncems", resource="ncemsRes")
            self.fail()
        except SYS_INVALID_RESC_INPUT:
            pass

    def test_not_res_ncems_coll(self):
        """
        Verify that it allows upload when NCEMS resource is not chosen and destination is an NCEMS
        collection.
        """
        try:
            self.irods.data_objects.create(
                "/testing/home/shared/ncems/other", resource="ncemsRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when NCEMS resource is not chosen and destination is not an
        NCEMS collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


if __name__ == "__main__":
    unittest.main()
