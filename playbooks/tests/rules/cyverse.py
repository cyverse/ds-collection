#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse.re rule logic"""

import os
from typing import Union
import unittest

from irods.access import iRODSAccess
from irods.collection import iRODSCollection
from irods.data_object import iRODSDataObject
from irods.exception import UserDoesNotExist
from irods.rule import Rule
from irods.session import iRODSSession

import test_rules
from test_rules import IrodsTestCase, IrodsType, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class CyverseTestCase(IrodsTestCase):
    """The base class for tests of cyverse.re"""

    def has_perm(
        self, username: str, access: str, entity: Union[iRODSDataObject, iRODSCollection],
    ) -> bool:
        """
        Checks to see if a given user has the given access to the given collection or data object

        Parameters:
            username  the username to check
            access    the level of access to check
            entity    the collection or data object to check

        Returns:
            true if it does, otherwise false
        """
        for acl in self.irods.acls.get(entity):
            if acl.user_name == username and acl.access_name == access:
                return True
        return False


class CyverseConstantsTest(CyverseTestCase):
    """Test the constants defined in cyverse.re"""

    def test_cyversehome(self):
        """Test _cyverse_HOME"""
        self.fn_test(
            '_cyverse_HOME', [], IrodsVal.string(os.path.join('/', self.irods.zone, 'home')))

    def test_cyversecoll(self):
        """Test cyverse_COLL"""
        self.fn_test('cyverse_COLL', [], IrodsVal.string('-C'))

    def test_cyversedataobj(self):
        """Test cyverse_DATA_OBJ"""
        self.fn_test('cyverse_DATA_OBJ', [], IrodsVal.string('-d'))

    def test_cyverseresc(self):
        """Test cyverse_RESC"""
        self.fn_test('cyverse_RESC', [], IrodsVal.string('-R'))

    def test_cyverseuser(self):
        """Test cyverse_USER"""
        self.fn_test('cyverse_USER', [], IrodsVal.string('-u'))


class CyverseEndswith(CyverseTestCase):
    """Test cyverse_endsWith"""

    def test_too_long(self):
        """Test suffix longer than string"""
        self.fn_test(
            'cyverse_endsWith',
            [IrodsVal.string('abc'), IrodsVal.string('abcd')],
            IrodsVal.boolean(False))

    def test_str_not_ends_with_suffix(self):
        """Test when the string doesn't end with suffix"""
        self.fn_test(
            'cyverse_endsWith',
            [IrodsVal.string('abc'), IrodsVal.string('dc')],
            IrodsVal.boolean(False))

    def test_str_ends_with_suffix(self):
        """Test when the string ends with suffix"""
        self.fn_test(
            'cyverse_endsWith',
            [IrodsVal.string('abc'), IrodsVal.string('bc')],
            IrodsVal.boolean(True))


class CyverseStartswith(CyverseTestCase):
    """Test cyverse_startsWith"""

    def test_too_long(self):
        """Test prefix longer than string"""
        self.fn_test(
            'cyverse_startsWith',
            [IrodsVal.string('abc'), IrodsVal.string('abcd')],
            IrodsVal.boolean(False))

    def test_str_not_begins_with_prefix(self):
        """Test when the string doesn't begin with prefix"""
        self.fn_test(
            'cyverse_startsWith',
            [IrodsVal.string('abc'), IrodsVal.string('ac')],
            IrodsVal.boolean(False))

    def test_str_begins_with_prefix(self):
        """Test when the string begins with prefix"""
        self.fn_test(
            'cyverse_startsWith',
            [IrodsVal.string('abc'), IrodsVal.string('ab')],
            IrodsVal.boolean(True))


class CyverseRmprefix(CyverseTestCase):
    """Test cyverse_rmPrefix"""

    def test_no_prefixes(self):
        """Test no prefixes provided"""
        self.fn_test(
            'cyverse_rmPrefix',
            [IrodsVal.string('orig'), IrodsVal.string_list([])],
            IrodsVal.string('orig'))

    def test_no_matching_prefix(self):
        """Test none of the provided prefixes match"""
        self.fn_test(
            'cyverse_rmPrefix',
            [IrodsVal.string('orig'), IrodsVal.string_list(['q', 'w'])],
            IrodsVal.string('orig'))

    def test_matching_prefix(self):
        """Test a provided prefix matches"""
        self.fn_test(
            'cyverse_rmPrefix',
            [IrodsVal.string('orig'), IrodsVal.string_list(['e', 'o'])],
            IrodsVal.string('rig'))


class CyverseIscoll(CyverseTestCase):
    """Test cyverse_isColl"""

    def test_not_c(self):
        """Test something other than -c or -C"""
        self.fn_test('cyverse_isColl', [IrodsVal.string('-d')], IrodsVal.boolean(False))

    def test_lowercase_c(self):
        """Test -c"""
        self.fn_test('cyverse_isColl', [IrodsVal.string('-c')], IrodsVal.boolean(True))

    def test_uppercase_c(self):
        """Test -C"""
        self.fn_test('cyverse_isColl', [IrodsVal.string('-C')], IrodsVal.boolean(True))


class CyverseIsdataobj(CyverseTestCase):
    """Test cyverse_isDataObj"""

    def test_not_d(self):
        """Test something other than -d"""
        self.fn_test('cyverse_isDataObj', [IrodsVal.string('-R')], IrodsVal.boolean(False))

    def test_d(self):
        """Test -d"""
        self.fn_test('cyverse_isDataObj', [IrodsVal.string('-d')], IrodsVal.boolean(True))


class CyverseIsfstype(CyverseTestCase):
    """Test cyverse_isFSType"""

    def test_not_fs(self):
        """Test something other than -C or -d"""
        self.fn_test('cyverse_isFSType', [IrodsVal.string('-R')], IrodsVal.boolean(False))

    def test_c(self):
        """Test -C"""
        self.fn_test('cyverse_isFSType', [IrodsVal.string('-C')], IrodsVal.boolean(True))

    def test_d(self):
        """Test -d"""
        self.fn_test('cyverse_isFSType', [IrodsVal.string('-d')], IrodsVal.boolean(True))


class CyverseIsresc(CyverseTestCase):
    """Test cyverse_isResc"""

    def test_not_r(self):
        """Test something other than -r or -R"""
        self.fn_test('cyverse_isResc', [IrodsVal.string('-u')], IrodsVal.boolean(False))

    def test_lowercase_r(self):
        """Test -r"""
        self.fn_test('cyverse_isResc', [IrodsVal.string('-r')], IrodsVal.boolean(True))

    def test_uppercase_r(self):
        """Test -R"""
        self.fn_test('cyverse_isResc', [IrodsVal.string('-R')], IrodsVal.boolean(True))


class CyverseIsuser(CyverseTestCase):
    """Test cyverse_isUser"""

    def test_not_u(self):
        """Test something other than -u"""
        self.fn_test('cyverse_isUser', [IrodsVal.string('-C')], IrodsVal.boolean(False))

    def test_u(self):
        """Test -u"""
        self.fn_test('cyverse_isUser', [IrodsVal.string('-u')], IrodsVal.boolean(True))


class CyverseGetentitytype(CyverseTestCase):
    """Test cyverse_getEntityType"""

    def test_collection(self):
        """Test with collection"""
        for p in IrodsTestCase.prep_path('/testing'):
            with self.subTest(p=p):
                self.fn_test('cyverse_getEntityType', [p], IrodsVal.string('-C'))

    def test_data_obj(self):
        """Test with data object"""
        obj = '/testing/home/rods/test_obj'
        self.irods.data_objects.create(obj)
        for p in IrodsTestCase.prep_path(obj):
            with self.subTest(p=p):
                self.fn_test('cyverse_getEntityType', [p], IrodsVal.string('-d'))
        self.irods.data_objects.unlink(obj, force=True)

    def test_resc(self):
        """Test with resource"""
        self.fn_test('cyverse_getEntityType', [IrodsVal.string('ingestRes')], IrodsVal.string('-R'))

    def test_user(self):
        """Test with user"""
        self.fn_test('cyverse_getEntityType', [IrodsVal.string('rods')], IrodsVal.string('-u'))

    def test_unknown(self):
        """Test with something that can't be identified"""
        self.fn_test('cyverse_getEntityType', [IrodsVal.string('garbage')], IrodsVal.string(''))


class CyverseIsforsvc(CyverseTestCase):
    """Test cyverse_isForSvc"""

    def test_path_in_shared(self):
        """Test entity path in projects folder"""
        self._is_for_svc_test('/testing/home/shared/project', False)

    def test_path_in_home_not_svc(self):
        """Test entity path in home folder, but not service folder"""
        self._is_for_svc_test('/testing/home/rods/obj', False)

    def test_path_in_svc_user_home(self):
        """Test entity path in the home folder of the service account"""
        self._is_for_svc_test('/testing/home/rods/svc_data/obj', False)

    def test_path_in_svc_folder(self):
        """Test entity path in the service folder for user"""
        self._is_for_svc_test('/testing/home/user/svc_data/obj', True)

    def _is_for_svc_test(self, path: str, exp_res: bool):
        for p in IrodsTestCase.prep_path(path):
            with self.subTest(p=p):
                self.fn_test(
                    'cyverse_isForSvc',
                    [IrodsVal.string('rods'), IrodsVal.string('svc_data'), p],
                    IrodsVal.boolean(exp_res))


class CyverseGiveaccesscoll(CyverseTestCase):
    """Tests of cyverse_giveAccessColl"""

    def setUp(self):
        super().setUp()
        try:
            self.irods.users.remove('user')
        except UserDoesNotExist:
            pass
        self.irods.users.create('user', 'rodsuser')
        self.exec_rule(
            self.mk_rule('cyverse_giveAccessColl("user", "read", /testing/home)'),
            IrodsType.NONE)

    def tearDown(self):
        self.irods.users.remove('user')
        super().tearDown()

    def test_coll_acl_set(self):
        """Test that a collection was given a given permission to a given user"""
        if not self.has_perm('user', 'read_object', self.irods.collections.get('/testing/home')):  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail('user did not receive read permission on /testing/home')

    def test_child_acl_set(self):
        """Test that a collection member is given a given permission to a given user"""
        if not self.has_perm(
            'user', 'read_object', self.irods.collections.get('/testing/home/rods')  # type: ignore
        ):
            self.fail('user did not receive read permission on member of /testing/home')


class CyVerseGiveaccessdataobj(CyverseTestCase):
    """Tests of  cyverse_giveAccessDataObj"""

    def setUp(self):
        super().setUp()
        self._obj = '/testing/home/rods/obj'
        self.ensure_user_exists('user')
        self.irods.data_objects.create(self._obj)
        self.exec_rule(
            self.mk_rule(f'cyverse_giveAccessDataObj("user", "read", {self._obj})'),
            IrodsType.NONE)

    def tearDown(self):
        self.irods.data_objects.unlink(self._obj, forced=True)
        self.irods.users.remove('user')
        super().tearDown()

    def test_obj_acl_set(self):
        """Test that a data object was given a given permission to a given user"""
        if not self.has_perm('user', 'read_object', self.irods.data_objects.get(self._obj)):
            self.fail('user did not receive read permission on data object')


class CyverseEnsureaccessoncreatecoll(CyverseTestCase):
    """Tests of cyverse_ensureAccessOnCreateColl"""

    def setUp(self):
        super().setUp()
        self.ensure_user_exists('svc')
        self._svc_coll = '/testing/home/rods/svc_data'
        self._coll = os.path.join(self._svc_coll, 'coll')
        self.irods.collections.create(self._coll, recursive=True)

    def tearDown(self):
        self.irods.collections.remove(self._svc_coll, recursive=True, force=True)
        self.irods.users.remove('svc')
        super().tearDown()

    def test_coll_in_svc_coll(self):
        """Test that a collection in a service collection gets service permission"""
        rule = self.mk_rule(
            f'cyverse_ensureAccessOnCreateColl("svc", "svc_data", "write", {self._coll})')
        self.exec_rule(rule, IrodsType.NONE)
        if not self.has_perm('svc', 'modify_object', self.irods.collections.get(self._coll)):  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail('svc did not receive write permission on collection')

    def test_coll_not_in_svc_coll(self):
        """Test that a collection not in a service collection doesn't get service permission"""
        other_coll = '/testing/home/rods/coll'
        child = os.path.join(other_coll, 'child')
        self.irods.collections.create(child, recursive=True)
        rule = self.mk_rule(
            f'cyverse_ensureAccessOnCreateColl("svc", "child", "write", {other_coll})')
        self.exec_rule(rule, IrodsType.NONE)
        if self.has_perm('rods', 'modify_object', self.irods.collections.get(self._coll)):  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail('svc did not receive write permission on collection')
        self.irods.collections.remove(other_coll, recursive=True, force=True)


class CyverseEnsureaccessoncreatedataobj(CyverseTestCase):
    """Tests of cyverse_ensureAccessOjCreateDataObj"""

    def setUp(self):
        super().setUp()
        self.ensure_user_exists('svc')
        self._svc_coll = '/testing/home/rods/svc_data'
        self.irods.collections.create(self._svc_coll)

    def tearDown(self):
        self.irods.collections.remove(self._svc_coll, recursive=True, force=True)
        self.irods.users.remove('svc')
        super().tearDown()

    def test_obj_in_svc_coll(self):
        """Test that a data object in a service collection gets service permission"""
        obj = os.path.join(self._svc_coll, 'obj')
        self.irods.data_objects.create(obj)
        rule = self.mk_rule(
            f'cyverse_ensureAccessOnCreateDataObj("svc", "svc_data", "write", {obj})')
        self.exec_rule(rule, IrodsType.NONE)
        if not self.has_perm('svc', 'modify_object', self.irods.data_objects.get(obj)):
            self.fail('svc did not receive write permission on collection')
        self.ensure_obj_absent(obj)

    def test_obj_not_in_svc_coll(self):
        """Test that a data object not in a service collection doesn't get service permission"""
        obj = os.path.join('/testing/home/rods/obj')
        self.irods.data_objects.create(obj)
        rule = self.mk_rule(
            f'cyverse_ensureAccessOnCreateDataObj("svc", "svc_data", "write", {obj})')
        self.exec_rule(rule, IrodsType.NONE)
        if self.has_perm('svc', 'modify_object', self.irods.data_objects.get(obj)):
            self.fail('svc received write permission on data object')
        self.ensure_obj_absent(obj)


class CyverseEnsureaccessonmv(CyverseTestCase):
    """Tests of cyverse_ensureAccessOnMov"""

    def setUp(self):
        super().setUp()
        self.ensure_user_exists('svc')
        self._svc_coll = '/testing/home/rods/svc_data'
        self.irods.collections.create(self._svc_coll)

    def tearDown(self):
        self.irods.collections.remove(self._svc_coll, recursive=True, force=True)
        self.irods.users.remove('svc')
        super().tearDown()

    def test_mv_coll_into_svc_coll(self):
        """Test move collection into service collection gets service permission"""
        coll = os.path.join(self._svc_coll, 'coll')
        self.irods.collections.create(coll)
        rule = self.mk_rule(
            f'''
            cyverse_ensureAccessOnMv("svc", "svc_data", "write", /testing/home/rods/coll, {coll})
            ''')
        self.exec_rule(rule, IrodsType.NONE)
        if not self.has_perm('svc', 'modify_object', self.irods.collections.get(coll)):  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail('svc did not receive write permission on collection')
        self.irods.collections.remove(coll, force=True, recursive=True)

    def test_mv_coll_into_not_svc_coll(self):
        """
        Test move collection into collection that doesn't belong to a service doesn't gets service
        permission.
        """
        coll = '/testing/home/rods/coll'
        self.irods.collections.create(coll)
        rule = self.mk_rule(
            f'cyverse_ensureAccessOnMv("svc", "svc_data", "write", /testing/home/coll, {coll})')
        self.exec_rule(rule, IrodsType.NONE)
        if self.has_perm('svc', 'modify_object', self.irods.collections.get(coll)):  # type: ignore
            self.fail('svc received write permission on collection')
        self.irods.collections.remove(coll, force=True)

    def test_mv_data_into_svc_coll(self):
        """Test move data object into service collection gets service permission"""
        obj = os.path.join(self._svc_coll, 'obj')
        self.irods.data_objects.create(obj)
        rule = self.mk_rule(
            f'cyverse_ensureAccessOnMv("svc", "svc_data", "write", /testing/home/rods/obj, {obj})')
        self.exec_rule(rule, IrodsType.NONE)
        if not self.has_perm('svc', 'modify_object', self.irods.data_objects.get(obj)):
            self.fail('svc did not receive write permission on data object')
        self.irods.data_objects.unlink(obj, force=True)

    def test_mv_data_into_not_svc_coll(self):
        """
        Test move data object into collection that doesn't belong to a service doesn't gets service
        permission.
        """
        obj = '/testing/home/rods/obj'
        self.irods.data_objects.create(obj)
        rule = self.mk_rule(
            f'cyverse_ensureAccessOnMv("svc", "svc_data", "write", /testing/home/obj, {obj})')
        self.exec_rule(rule, IrodsType.NONE)
        if self.has_perm('svc', 'modify_object', self.irods.data_objects.get(obj)):
            self.fail('svc received write permission on data object')
        self.irods.data_objects.unlink(obj, force=True)


class CyverseSetprotectedavu(CyverseTestCase):
    """Tests of cyverse_setProtectedAVU"""

    def setUp(self):
        super().setUp()
        self.ensure_user_exists('user', 'password')

    def tearDown(self):
        self.irods.users.remove('user')
        super().tearDown()

    def test_avu_set_on_coll(self):
        """Test that an AVU is set on a collection"""
        self.irods.acls.set(iRODSAccess('read', '/testing/home/rods', 'user'))
        with iRODSSession(
            host=self.irods.host,
            port=self.irods.port,
            zone=self.irods.zone,
            user='user',
            password='password'
        ) as user_sess:
            rule = Rule(
                session=user_sess,
                instance_name='irods_rule_engine_plugin-irods_rule_language-instance',
                body="cyverse_setProtectedAVU(/testing/home/rods, 'key', 'value', 'unit')",
                output='ruleExecOut')
            rule.execute()
        try:
            coll = self.irods.collections.get('/testing/home/rods')
            coll.metadata.get_one('key')  # type: ignore
            coll.metadata.remove('key', 'value', 'unit')  # type: ignore
        except KeyError:
            self.fail("AVU 'key' not set on collection '/testing/home/rods'")

    def test_avu_set_on_data(self):
        """Test that an AVU is set on a data object"""
        obj = '/testing/home/rods/test_obj'
        self.irods.data_objects.create(obj)
        self.irods.acls.set(iRODSAccess('read', '/testing/home/rods', 'user'), recursive=True)
        with iRODSSession(
            host=self.irods.host,
            port=self.irods.port,
            zone=self.irods.zone,
            user='user',
            password='password'
        ) as user_sess:
            rule = Rule(
                session=user_sess,
                instance_name='irods_rule_engine_plugin-irods_rule_language-instance',
                body=f"cyverse_setProtectedAVU({obj}, 'key', 'value', 'unit')",
                output='ruleExecOut')
            rule.execute()
        try:
            self.irods.data_objects.get(obj).metadata.get_one('key')  # type: ignore
            self.irods.data_objects.unlink(obj, force=True)
        except KeyError:
            self.fail("AVU 'key' not set on data object")


if __name__ == "__main__":
    unittest.main()
