#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_logic.re rule logic."""

import unittest

from irods.path import iRODSPath

from test_rules import IrodsTestCase, IrodsVal


class TestCyverseLogicContains(IrodsTestCase):
    """Tests of _cyverse_logic_contains"""

    def test_item_not_in_list(self):
        """Verify that it returns false when item not in list"""
        self.fn_test(
            '_cyverse_logic_contains',
            [IrodsVal.string("missing"), IrodsVal.string_list([])],
            IrodsVal.boolean(False))

    def test_item_in_singleton_list(self):
        """Verify that it returns true when item in list with only one item"""
        self.fn_test(
            '_cyverse_logic_contains',
            [IrodsVal.string("item"), IrodsVal.string_list(["item"])],
            IrodsVal.boolean(True))

    def test_item_first(self):
        """Verify that it returns true when item is first in list"""
        self.fn_test(
            '_cyverse_logic_contains',
            [IrodsVal.string("item"), IrodsVal.string_list(["item", "last"])],
            IrodsVal.boolean(True))

    def test_item_last(self):
        """Verify that it returns true when item is last in list"""
        self.fn_test(
            '_cyverse_logic_contains',
            [IrodsVal.string("item"), IrodsVal.string_list(["first", "item"])],
            IrodsVal.boolean(True))


class TestCyverseLogicIcatIds(IrodsTestCase):
    """Tests of ICAT Ids logic"""

    def test_getcollid_path(self):
        """Test _cyverse_logic_getCollId with path"""
        zone_path = iRODSPath(self.irods.zone)
        zone = self.irods.collections.get(zone_path)
        if zone:
            self.fn_test(
                '_cyverse_logic_getCollId', [IrodsVal.path(zone_path)], IrodsVal.integer(zone.id))
        else:
            self.fail("zone collection is missing")

    @unittest.skip("not implemented")
    def test_getcollid_str(self):
        """Test _cyverse_logic_getCollId with string"""

    @unittest.skip("not implemented")
    def test_getdataobjid(self):
        """Test _cyverse_logic_getDataObjId"""

    @unittest.skip("not implemented")
    def test_getid(self):
        """Test _cyverse_logic_getId"""


class TestCyVerseLogic(IrodsTestCase):
    """Test cyverse_logic.re"""

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
