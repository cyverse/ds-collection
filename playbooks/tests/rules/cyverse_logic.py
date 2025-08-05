#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_logic.re rule logic."""

import unittest

from test_rules import IrodsTestCase, IrodsVal


class TestCyverseLogicContains(IrodsTestCase):
    """Tests of the _cyverse_logic_contains"""

    def test_item_not_in_list(self):
        """Verify that it returns false when item not in list"""
        self.fn_test(
            '_cyverse_logic_contains',
            [IrodsVal.string("missing"), IrodsVal.string_list([])],
            IrodsVal.boolean(False))

    @unittest.skip("not implemented")
    def test_item_first(self):
        """Verify that it returns true when item is first in list"""

    @unittest.skip("not implemented")
    def test_item_last(self):
        """Verify that it returns true when item is last in list"""


class TestCyVerseLogic(IrodsTestCase):
    """Test cyverse_logic.re"""

    @unittest.skip("not implemented")
    def test_icat_ids(self):
        """Test the private ICAT Ids rule logic"""

    @unittest.skip("not implemented")
    def test_user_info(self):
        """Test private user info rule logic"""

    @unittest.skip("not implemented")
    def test_avus(self):
        """Test private AVU rule logic"""

    @unittest.skip("not implemented")
    def test_checksum(self):
        """Test private checksum rule logic"""

    @unittest.skip("not implemented")
    def test_uuids(self):
        """Test private UUID rule logic"""

    @unittest.skip("not implemented")
    def test_action_tracking(self):
        """Test private action tracking rule logic"""

    @unittest.skip("not implemented")
    def test_message_publishing(self):
        """Test private message publishing rule logic"""

    @unittest.skip("not implemented")
    def test_protected_avus(self):
        """Test private protected AVUs rule logic"""

    @unittest.skip("not implemented")
    def test_rodsadmin_group_permissions(self):
        """Test private rodsadmin group permissions rule logic"""

    @unittest.skip("Not implemented")
    def test_public(self):
        """Test the public rule logic"""


if __name__ == "__main__":
    unittest.main()
