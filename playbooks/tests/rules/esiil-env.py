#!/usr/bin/env python  # pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of esiil-env.re rule logic."""

import unittest

import test_rules
from test_rules import IrodsTestCase, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class TestEsiilEnv(IrodsTestCase):
    """Tests of esiil-env.re"""

    def test_resc(self):
        """Verify that esiil_RESC is correct"""
        self.fn_test('esiil_RESC', [], IrodsVal.string('esiilRes'))


if __name__ == "__main__":
    unittest.main()
