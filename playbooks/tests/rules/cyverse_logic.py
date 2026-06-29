#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_logic.re rule logic."""

import unittest

from irods.path import iRODSPath

import test_rules
from test_rules import IrodsTestCase, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class TestContains(IrodsTestCase):
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


class TestIcatIds(IrodsTestCase):
    """Tests of ICAT Ids logic"""

    def test_getcollid_present(self):
        """Test _cyverse_logic_getCollId"""
        zone_path = iRODSPath(self.irods.zone)
        zone = self.irods.collections.get(zone_path)
        if zone:
            for p in IrodsTestCase.prep_path(zone_path):
                with self.subTest(p=p):
                    self.fn_test('_cyverse_logic_getCollId', [p], IrodsVal.integer(zone.id))
        else:
            self.fail("zone collection is missing")

    def test_getcollid_missing(self):
        """Test _cyverse_logic_getCollId with the collection doesn't exist"""
        self.fn_test(
            '_cyverse_logic_getCollId',
            [IrodsVal.string(iRODSPath("missing"))],
            IrodsVal.integer(-1))

    def test_getid_coll(self):
        """Test _cyverse_logic_getId for collection"""
        zone_path = iRODSPath(self.irods.zone)
        zone = self.irods.collections.get(zone_path)
        if zone:
            for p in IrodsTestCase.prep_path(zone_path):
                with self.subTest(p=p):
                    self.fn_test('_cyverse_logic_getId', [p], IrodsVal.integer(zone.id))
        else:
            self.fail("zone collection is missing")

    def test_getid_data(self):
        """Test _cyverse_logic_getId for data object"""
        data_path = iRODSPath(self.irods.zone, 'home', self.irods.username, 'obj')
        data = self.irods.data_objects.create(data_path)
        for p in IrodsTestCase.prep_path(data_path):
            with self.subTest(p=p):
                self.fn_test('_cyverse_logic_getId', [p], IrodsVal.integer(data.id))  # pylint: disable=no-member,line-too-long # type: ignore # noqa: E501


class TestUserInfo(IrodsTestCase):
    """Tests of private user info rule logic"""

    def test_isadm_groupadmin(self):
        """
        Test _cyverse_logic_isAdm correctly identifies that a groupadmin user
        is not a rodsadmin
        """
        name = 'grouphandler'
        self.irods.users.create(name, 'groupadmin')
        try:
            self._test_rule(name, False)
        finally:
            self.irods.users.remove(name)

    def test_isadm_rodsadmin(self):
        """
        Test _cyverse_logic_isAdm correctly identifies a rodsadmin user is a
        rodsadmin
        """
        self._test_rule('rods', True)

    def test_isadm_rodsgroup(self):
        """
        Test _cyverse_logic_isAdm correctly identifies a group as not a
        rodsadmin
        """
        self._test_rule('public', False)

    @unittest.skip("not implemented")
    def test_isadm_rodsuser(self):
        """
        Test _cyverse_logic_isAdm correctly identifies a rodsuser user as not a
        rodsadmin
        """

    def _test_rule(self, name, expected_result):
        self.fn_test(
            '_cyverse_logic_isAdm',
            [IrodsVal.string(name), IrodsVal.string(self.irods.zone)],
            IrodsVal.boolean(expected_result))


class TestCyVerseLogic(IrodsTestCase):
    """Test cyverse_logic.re"""

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
    def test_resource_free_space_mgmt(self):
        """Test resource free space management logic"""

    @unittest.skip("not implemented")
    def test_rodsadmin_group_permissions(self):
        """Test private rodsadmin group permissions rule logic"""

    @unittest.skip("Not implemented")
    def test_public(self):
        """Test the public rule logic"""


if __name__ == "__main__":
    unittest.main()
