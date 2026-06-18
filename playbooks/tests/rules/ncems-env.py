#!/usr/bin/env python  # pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of ncems-env.re rule logic."""

import unittest

import test_rules
from test_rules import IrodsTestCase, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class TestNcemsEnv(IrodsTestCase):
    """Tests of ncems-env.re"""

    def test_resc(self):
        """Verify that ncems_RESC is correct"""
        self.fn_test('ncems_RESC', [], IrodsVal.string('ncemsRes'))


if __name__ == "__main__":
    unittest.main()
