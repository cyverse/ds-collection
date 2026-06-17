#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of avra.re rule logic."""

import unittest

import test_rules
from test_rules import IrodsTestCase


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class TestPepResourceResolveHierarchyPreAvraResDefault(IrodsTestCase):
    """
    Test AVRA instance of pep_resource_resolve_hierarchy_pre when the AVRA resource is the same as
    the default resource.
    """

    @unittest.skip("not implemented")
    def test_avra_res_and_coll(self):
        """
        Verify that it allows upload when AVRA resource is chosen and destination is a AVRA
        collection.
        """

    @unittest.skip("not implemented")
    def test_avra_res_not_coll(self):
        """
        Verify that it allows upload when AVRA resource is chosen and destination is not a AVRA
        collection.
        """

    @unittest.skip("not implemented")
    def test_not_res_avra_coll(self):
        """
        Verify that it allows upload when AVRA resource is not chosen and destination is a AVRA
        collection.
        """

    @unittest.skip("not implemented")
    def test_not_res_nor_coll(self):
        """
        Verify that it allows upload when AVRA resource is not chosen and destination is not a AVRA
        collection.
        """


class TestPepResourceResolveHierarchyPre(IrodsTestCase):
    """Tests of pep_resource_resolve_hierarchy_pre"""

    @unittest.skip("not implemented")
    def test_avra_res_not_default(self):
        """Test AVRA instance when the AVRA resource isn't the same as the default resource."""


if __name__ == "__main__":
    unittest.main()
