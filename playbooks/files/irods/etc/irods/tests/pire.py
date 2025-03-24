#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of pire.re rule logic."""

import unittest

from irods.exception import SYS_INVALID_RESC_INPUT
from scp import SCPClient

import test_rules
from test_rules import IrodsTestCase, IrodsVal


@test_rules.unimplemented
class TestPireIsforpire(IrodsTestCase):
    """Test _pire_isForPIRE"""

    def test_path_in_proj_coll(self):
        """Verify that it correctly determines that a path in the project collection is for PIRE"""
        for p in IrodsTestCase.prep_path("/testing/home/shared/bhpire/file"):
            with self.subTest(p=p):
                self.fn_test("_pire_isForPIRE", [p], IrodsVal.boolean(True))

    def test_path_in_pub_coll(self):
        """Verify that it correctly determines that a path in the public collection is for PIRE"""
        for p in IrodsTestCase.prep_path("/testing/home/shared/eht/file"):
            with self.subTest(p=p):
                self.fn_test("_pire_isForPIRE", [p], IrodsVal.boolean(True))

    def test_path_not_in_pire(self):
        """Verify that it correctly determines a path is not in a PIRE collection"""
        for p in IrodsTestCase.prep_path("/testing/home/rods"):
            with self.subTest(p=p):
                self.fn_test("_pire_isForPIRE", [p], IrodsVal.boolean(False))


@test_rules.unimplemented
class TestPepResourceResolveHierarchyPrePireResDefault(IrodsTestCase):
    """
    Test PIRE instance of pep_resource_resolve_hierarchy_pre when the PIRE resource is the same as
    the default resource.
    """

    def setUp(self):
        super().setUp()
        self._scp = SCPClient(self.ssh.get_transport())
        self._scp.get('/etc/irods/pire-env.re', '/tmp/pire-env.re')
        self.ssh.exec_command("sed --in-place 's/pire_RESC = .*/pire_RESC = cyverse_DEFAULT_RESC/'")
        self.ssh.exec_command("touch /etc/irods/core.re")

    def tearDown(self):
        for obj in [
            "/testing/home/rods/other",
            "/testing/home/rods/pire",
            "/testing/home/shared/bhpire/other",
            "/testing/home/shared/bhpire/pire",
        ]:
            self.ensure_obj_absent(obj)
        self._scp.put('/tmp/pire-env.re', '/etc/irods/pire-env.re')
        self._scp.close()
        self.ssh.exec_command("touch /etc/irods/core.re")
        super().tearDown()

    def test_pire_res_and_coll(self):
        """
        Verify that it allows upload when PIRE resource is chosen and destination is a PIRE
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/bhpire/pire")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_pire_res_not_coll(self):
        """
        Verify that it allows upload when PIRE resource is chosen and destination is not a PIRE
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/pire")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_pire_coll(self):
        """
        Verify that it allows upload when PIRE resource is not chosen and destination is a PIRE
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/rods/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when PIRE resource is not chosen and destination is not a PIRE
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/bhpire/other", resource="replRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()


class TestPepResourceResolveHierarchyPrePireResNotDefault(IrodsTestCase):
    """
    Test PIRE instance of pep_resource_resolve_hierarchy_pre when the PIRE resource isn't the same
    as the default resource.
    """

    def tearDown(self):
        self.ensure_obj_absent("/testing/home/shared/bhpire/pire")
        super().tearDown()

    def test_pire_res_and_coll(self):
        """
        Verify that it allows upload when PIRE resource is chosen and destination is a PIRE
        collection.
        """
        try:
            self.irods.data_objects.create("/testing/home/shared/bhpire/pire", resource="pireRes")
        except SYS_INVALID_RESC_INPUT:
            self.fail()

    @unittest.skip
    def test_pire_res_not_coll(self):
        """
        Verify that it forbids upload when PIRE resource is chosen and destination is not a PIRE
        collection.
        """

    @unittest.skip
    def test_not_res_pire_coll(self):
        """
        Verify that it allows upload when PIRE resource is not chosen and destination is a PIRE
        collection.
        """

    @unittest.skip
    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when PIRE resource is not chosen and destination is not a PIRE
        collection.
        """


if __name__ == "__main__":
    unittest.main()
