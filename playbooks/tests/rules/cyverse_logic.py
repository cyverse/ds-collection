#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_logic.re rule logic."""

import unittest

from irods.path import iRODSPath

import test_rules
from test_rules import IrodsTestCase, IrodsType, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class IdTest(IrodsTestCase):
    """Tests of _cyverse_logic_ID"""

    def test(self):
        """Verify that it has the correct value"""
        self.fn_test('_cyverse_logic_ID', [], IrodsVal.string('cyverse_logic'))


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
        self.ensure_user_exists(name, user_type='groupadmin')
        try:
            self._test_rule(name, False)
        finally:
            self.irods.users.remove(name)

    def test_isadm_rodsadmin(self):
        """
        Test _cyverse_logic_isAdm correctly identifies a rodsadmin user is a
        rodsadmin
        """
        self._test_rule(self.irods.username, True)

    def test_isadm_rodsgroup(self):
        """
        Test _cyverse_logic_isAdm correctly identifies a group as not a
        rodsadmin
        """
        self._test_rule('public', False)

    def test_isadm_rodsuser(self):
        """
        Test _cyverse_logic_isAdm correctly identifies a rodsuser user as not a
        rodsadmin
        """
        name = 'user'
        self.irods.users.create(name, 'rodsuser')
        try:
            self._test_rule(name, False)
        finally:
            self.irods.users.remove(name)

    def _test_rule(self, name, expected_result):
        self.fn_test(
            '_cyverse_logic_isAdm',
            [IrodsVal.string(name), IrodsVal.string(self.irods.zone)],
            IrodsVal.boolean(expected_result))


class TestAvus(IrodsTestCase):
    """Tests of private AVU rule logic"""

    def test_no_candidates(self):
        """Verify that if no candidates are provided the orignal is returned"""
        self._test_getnewavusetting('orig', 'prefix', [], 'orig')

    def test_one_candidate_unmatched(self):
        """
        Verify that it works correctly when one candidate is provided that
        doesn't start with the prefix.
        """
        self._test_getnewavusetting('orig', 'prefix', ['val'], 'orig')

    def test_one_candidate_matched(self):
        """
        Verify that it works correctly when one candidate is provided that
        starts with the prefix.
        """
        self._test_getnewavusetting('orig', 'prefix', ['prefix' + 'val'], 'val')

    def test_multiple_candidates_unmatched(self):
        """
        Verify that it works correctly when multiple candidates are provided
        and none start with the prefix.
        """
        self._test_getnewavusetting('orig', 'prefix', ['val1', 'val2'], 'orig')

    def test_multiple_candidates_first_match(self):
        """
        Verify that it works correctly when multiple candidates are provided
        and the first starts with the prefix.
        """
        self._test_getnewavusetting('orig', 'prefix', ['prefix' + 'val1', 'val2', 'val3'], 'val1')

    def test_multiple_candidates_second_match(self):
        """
        Verify that it works correctly when multiple candidates are provided
        and the second starts with the prefix.
        """
        self._test_getnewavusetting('orig', 'prefix', ['val1', 'prefix' + 'val2', 'val3'], 'val2')

    @unittest.skip("not implemented")
    def test_multiple_candidates_mult_matches(self):
        """
        Verify that it works correctly when multiple candidates are provided
        and multiple start with the prefix.
        """

    def _test_getnewavusetting(self, orig_val, prefix, candidates, exp_res):
        self.fn_test(
            '_cyverse_logic_getNewAVUSetting',
            [IrodsVal.string(orig_val), IrodsVal.string(prefix), IrodsVal.list_string(candidates)],
            IrodsVal.string(exp_res))


class TestPrivateCyVerseLogic(IrodsTestCase):
    """Tests of the internal logic"""

    @unittest.skip("not implemented")
    def test_checksum(self):
        """Test private checksum rule logic"""

    @unittest.skip("not implemented")
    def test_uuids(self):
        """Test private UUID rule logic"""

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


class TestAcpostprocformodifyavumetadataGeneralProcessable(IrodsTestCase):
    """
    Test the form of the command that handles all subcommands except `cp` and
    `mod` and the entity is a collection of data object and the attribute isn't
    `ipc_UUID`.
    """

    def test_add(self):
        """Tests what happens when an AVU was added"""
        if not self._call_rule("add"):
            self.fail("A collection.metadata.add message wasn't published")

    def test_adda(self):
        """Tests what happens when an AVU was administratively added"""
        if not self._call_rule("adda"):
            self.fail("A collection.metadata.adda message wasn't published")

    @unittest.skip("not implemented")
    def test_addw(self):
        """Tests what happens when an AVU was added by wildcard"""

    def test_rm(self):
        """Tests what happens when an AVU was removed"""
        if not self._call_rule("rm"):
            self.fail("A collection.metadata.rm message wasn't published")

    @unittest.skip("not implemented")
    def test_rmw(self):
        """Tests what happens when an AVU was removed by wildcard"""

    def test_set(self):
        """Tests what happens when an AVU was set"""
        if not self._call_rule("set"):
            self.fail("A collection.metadata.set message wasn't published")

    def _call_rule(self, opt):
        coll_path = iRODSPath(self.irods.zone, "home")
        for p in IrodsTestCase.prep_path(coll_path):
            with self.subTest(p=p):
                rule_src = f'''
                    cyverse_logic_acPostProcForModifyAVUMetadata(
                        "{opt}",
                        "-C",
                        {p},
                        "a",
                        "v",
                        "u",
                        "{self.irods.username}",
                        "{self.irods.zone}" );
                '''
                self.exec_rule(self.mk_rule(rule_src), IrodsType.NONE)
                for line in self.tail_rods_log():
                    if 'amqp-topic-send' in line and f'collection.metadata.{opt}' in line:
                        return True
        return False


class TestAcpostprocformodifyavumetadataGeneral(IrodsTestCase):
    """
    Test the form of the command that handles all subcommands except `cp` and
    `mod`.
    """

    @unittest.skip("not implemented")
    def test_fs_entity_uuid(self):
        """
        Tests what happens when the entity is a collection or data object and
        the attributed being modified is ipc_UUID
        """

    @unittest.skip("not implemented")
    def test_not_fs_entity(self):
        """Tests what happens when the entity is a resource or user"""


class TestAcpostprocformodifyavumetadata(IrodsTestCase):
    """Tests of cyverse_logic_acPostProcForModifyAVUMetadata"""

    @unittest.skip("not implemented")
    def test_cp_form(self):
        """Test the form of the command that handles the `cp` subcommand."""

    @unittest.skip("not implemented")
    def test_mod_form(self):
        """Test the form of the command that handles the `mod` subcommand."""


class TestStaticPeps(IrodsTestCase):
    """Tests of the static PEP implementations"""

    @unittest.skip("not implemented")
    def test_acpostprocformodifyaccesscontrol(self):
        """Test cyverse_logic_acPostProcForModifyAccessControl"""

    @unittest.skip("not implemented")
    def test_acpreprocformodifyavumetadata(self):
        """Test cyverse_logic_acPreProcForModifyAVUMetadata"""

    @unittest.skip("not implemented")
    def test_accreatecollbyadmin(self):
        """Test cyverse_logic_acCreateCollByAdmin"""

    @unittest.skip("not implemented")
    def test_acpostprocforcollcreate(self):
        """Test cyverse_logic_acPostProcForCollCreate"""

    @unittest.skip("not implemented")
    def test_acdeletecollbyadminifpresent(self):
        """Test cyverse_logic_acDeleteCollByAdminIfPresent"""

    @unittest.skip("not implemented")
    def test_acpreprocforrmcoll(self):
        """Test cyverse_logic_acPostProcForRmColl"""

    @unittest.skip("not implemented")
    def test_acpreconnect(self):
        """Test cyverse_logic_acPreConnect"""

    @unittest.skip("not implemented")
    def test_acpostprocfordatacopyreceived(self):
        """Test cyverse_logic_acPostProcForDataCopyReceived"""

    @unittest.skip("not implemented")
    def test_acdatadeletepolicy(self):
        """Test cyverse_logic_acDataDeletePolicy"""

    @unittest.skip("not implemented")
    def test_acpostprocfordelete(self):
        """Test cyverse_logic_acPostProcForDelete"""

    @unittest.skip("not implemented")
    def test_acpostprocforopen(self):
        """Test cyverse_logic_acPostProcForOpen"""

    @unittest.skip("not implemented")
    def test_acpostprocforobjrename(self):
        """Test cyverse_logic_acPostProcForObjRename"""

    @unittest.skip("not implemented")
    def test_acpostprocforparalleltransferreceived(self):
        """Test cyverse_logic_acPostProcForParallelTransferReceived"""


@test_rules.unimplemented
class TestDynamicPeps(IrodsTestCase):
    """Tests of dynamic PEP implementations"""


if __name__ == "__main__":
    unittest.main()
