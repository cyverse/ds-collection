#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_json.re rule logic."""

import unittest

import test_rules
from test_rules import IrodsTestCase


def setUpModule():  # pylint: disable=invalid-name
    """Set up the module."""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down the module."""
    test_rules.tearDownModule()


class CyverseJsonTest(IrodsTestCase):
    """Test tje cyverse_json.re rule-base"""

    @unittest.skip("not implemented")
    def test_private(self):
        """test the private entities"""

    @unittest.skip("not implemented")
    def test_public(self):
        """test the public entities"""


if __name__ == "__main__":
    unittest.main()
