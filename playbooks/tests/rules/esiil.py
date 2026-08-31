#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of esiil.re rule logic."""

import unittest

from irods.exception import iRODSException, SYS_INVALID_RESC_INPUT
from irods.path import iRODSPath

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
    Test ESIIL instance of pep_resource_resolve_hierarchy_pre when the ESIIL
    resource is the same as the default resource.
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
        Verify that it allows upload when ESIIL resource is chosen and
        destination is a ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/esiil/esiil", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_esiil_res_not_coll(self):
        """
        Verify that it allows upload when ESIIL resource is chosen and
        destination is not a ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/esiil", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_esiil_coll(self):
        """
        Verify that it allows upload when ESIIL resource is not chosen and
        destination is a ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when ESIIL resource is not chosen and
        destination is not a ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/esiil/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


class TestPepResourceResolveHierarchyPreEsiilResNotDefault(IrodsTestCase):
    """
    Test ESIIL instance of pep_resource_resolve_hierarchy_pre when the ESIIL
    resource isn't the same as the default resource.
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
        Verify that it allows upload when ESIIL resource is chosen and
        destination is a ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/esiil/esiil", resource="esiilRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_esiil_res_not_coll(self):
        """
        Verify that it forbids upload when ESIIL resource is chosen and
        destination is not a ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/esiil", resource="esiilRes")
            self.fail()
        except SYS_INVALID_RESC_INPUT:
            pass

    def test_not_res_esiil_coll(self):
        """
        Verify that it allows upload when ESIIL resource is not chosen and
        destination is a ESIIL collection.
        """
        try:
            self.irods.data_objects.create(
                "/testing/home/shared/esiil/other", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when ESIIL resource is not chosen and
        destination is not a ESIIL collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


class TestPepResourceResolveHierarchyPreEsiilResNoAdd(IrodsTestCase):
    """
    Verify ESIIL instance of pep_resource_resolve_hierarchy_pre allows
    operations that don't add a replica to the ESIIL resource.
    """

    def __init__(self, method: str):
        super().__init__(method)
        self._obj_path = None
        self._resc = None
        self._resc_avu = None

    def setUp(self):
        super().setUp()
        resc_name = 'esiilRes'
        self._obj_path = iRODSPath(self.irods.zone, "home", "shared", "esiil", "esiil")
        self.irods.data_objects.create(self._obj_path, resource=resc_name)
        self._resc = self.irods.resources.get(resc_name)
        self._resc_avu = self._resc.metadata.get_one('ipc::hosted-collection')
        self._resc.metadata.remove(self._resc_avu)

    def tearDown(self):
        self._resc.metadata.add(self._resc_avu)  # pyright: ignore[reportOptionalMemberAccess]
        self.ensure_obj_absent(self._obj_path)  # pyright: ignore[reportArgumentType]
        super().tearDown()

    def test_open(self):
        """Verify that an open operation is allowed"""
        try:
            self.irods.data_objects.chksum(self._obj_path)
        except iRODSException:
            self.fail("the open operation failed")

    def test_unlink(self):
        """Verify that an unlink operation is allowed"""
        try:
            self.irods.data_objects.unlink(self._obj_path, force=True)
        except iRODSException:
            self.fail("the open operation failed")


if __name__ == "__main__":
    unittest.main()
