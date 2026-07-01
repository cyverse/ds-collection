#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of pire.re rule logic."""

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


class TestPepResourceResolveHierarchyPrePireResDefault(IrodsTestCase):
    """
    Test PIRE instance of pep_resource_resolve_hierarchy_pre when the PIRE
    resource is the same as the default resource.
    """

    def setUp(self):
        super().setUp()
        self.scp.get('/etc/irods/pire-env.re', '/tmp/pire-env.re')
        self.ssh.exec_command("sed --in-place 's/pire_RESC = .*/pire_RESC = cyverse_DEFAULT_RESC/'")
        self.reload_rules()

    def tearDown(self):
        for obj in [
            "/testing/home/rods/other",
            "/testing/home/rods/pire",
            "/testing/home/shared/bhpire/other",
            "/testing/home/shared/bhpire/pire",
        ]:
            self.ensure_obj_absent(obj)
        self.update_rulebase([('pire-env.re', '/tmp/pire-env.re')])
        super().tearDown()

    def test_pire_res_and_coll(self):
        """
        Verify that it allows upload when PIRE resource is chosen and
        destination is a PIRE collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/bhpire/pire", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_pire_res_not_coll(self):
        """
        Verify that it allows upload when PIRE resource is chosen and
        destination is not a PIRE collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/pire", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_pire_coll(self):
        """
        Verify that it allows upload when PIRE resource is not chosen and
        destination is a PIRE collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when PIRE resource is not chosen and
        destination is not a PIRE collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/bhpire/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


class TestPepResourceResolveHierarchyPrePireResNotDefault(IrodsTestCase):
    """
    Test PIRE instance of pep_resource_resolve_hierarchy_pre when the PIRE
    resource isn't the same as the default resource.
    """

    def tearDown(self):
        for obj in [
            "/testing/home/rods/other",
            "/testing/home/rods/pire",
            "/testing/home/shared/bhpire/other",
            "/testing/home/shared/bhpire/pire",
        ]:
            self.ensure_obj_absent(obj)
        super().tearDown()

    def test_pire_res_and_coll(self):
        """
        Verify that it allows upload when PIRE resource is chosen and
        destination is a PIRE collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/bhpire/pire", resource="pireRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_pire_res_not_coll(self):
        """
        Verify that it forbids upload when PIRE resource is chosen and
        destination is not a PIRE collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/pire", resource="pireRes")
            self.fail()
        except SYS_INVALID_RESC_INPUT:
            pass

    def test_not_res_pire_coll(self):
        """
        Verify that it allows upload when PIRE resource is not chosen and
        destination is a PIRE collection.
        """
        try:
            self.irods.data_objects.create(
                "/testing/home/shared/bhpire/other", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when PIRE resource is not chosen and
        destination is not a PIRE collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="ingestRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


class TestPepResourceResolveHierarchyPreNcemsResNoAdd(IrodsTestCase):
    """
    Verify PIRE instance of pep_resource_resolve_hierarchy_pre allows operations
    that don't add a replica to the PIRE resource.
    """

    def __init__(self, method: str):
        super().__init__(method)
        self._obj_path = None
        self._resc = None
        self._resc_avu = None

    def setUp(self):
        super().setUp()
        resc_name = 'pireRes'
        bhpire = iRODSPath(self.irods.zone, "home", "shared", "bhpire")
        self._obj_path = iRODSPath(bhpire, "pire")
        self.irods.data_objects.create(self._obj_path, resource=resc_name)
        self._resc = self.irods.resources.get(resc_name)
        for avu in self._resc.metadata.get_all('ipc::hosted-collection'):
            if avu.value == bhpire:
                self._resc_avu = avu
                break
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
