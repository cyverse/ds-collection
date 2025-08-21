#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_encryption.re rule logic."""

import os
import subprocess
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
import unittest

from irods.exception import CUT_ACTION_PROCESSED_ERR

import test_rules
from test_rules import IrodsTestCase, IrodsType, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up the module."""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down the module."""
    test_rules.tearDownModule()


class _CyverseEncryptionTestCase(IrodsTestCase):

    def setUp(self):
        super().setUp()
        self._enc_coll = '/testing/home/rods/enc_coll'
        self.irods.collections.create(self._enc_coll).metadata.set('encryption::required', 'true')  # type: ignore # noqa: E501 # pylint: disable=line-too-long

    def tearDown(self):
        self.ensure_coll_absent(self._enc_coll)
        super().tearDown()

    @property
    def enc_coll(self) -> str:
        """the path to a collection that requires encryption"""
        return self._enc_coll


class CyVerseEncryptionApiCollCreatePost(_CyverseEncryptionTestCase):
    """Tests of cyverse_encryption_api_coll_create_post"""

    def test_enc_coll_sub_coll_enc(self):
        """
        Test that a collection created in a collection requiring encryption also requires encryption
        """
        child = os.path.join(self.enc_coll, 'child')
        meta = self.irods.collections.create(child).metadata  # type: ignore
        if (
            'encryption::required' not in meta
            or meta.get_one('encryption::required').value != 'true'
        ):
            self.fail("encryption::required AVU not set to 'true'")
        self.ensure_coll_absent(child)

    def test_no_enc_coll_sub_coll_no_enc(self):
        """
        Test that a collection created in a collection not requiring encryption also doesn't require
        encryption
        """
        child = self.irods.collections.create('/testing/home/child')
        try:
            enc_req = child.metadata.get_one('encryption::required')  # type: ignore
            if enc_req.value == 'true':
                self.fail("encryption::required AVU set to 'true'")
        except KeyError:
            pass
        if child:
            child.remove(force=True)


class CyverseEncryptionApiDataObjCopyPre(_CyverseEncryptionTestCase):
    """Tests of cyverse_encryption_api_data_obj_copy_pre"""

    def setUp(self):
        super().setUp()
        self._orig_obj = '/testing/home/orig'
        self.irods.data_objects.create(self._orig_obj)

    def tearDown(self):
        self.ensure_obj_absent(self._orig_obj)
        super().tearDown()

    def test_enc_allowed_in_enc_coll(self):
        """Test that an encrypted files can be created in a collection requiring encryption"""
        copy_obj = os.path.join(self.enc_coll, 'copy.enc')
        self.irods.data_objects.copy(self._orig_obj, copy_obj)
        if not self.irods.data_objects.exists(copy_obj):
            self.fail("encrypted file not copied")
        self.ensure_obj_absent(copy_obj)

    def test_not_enc_not_allowed_in_enc_coll(self):
        """Test that an unencrypted file cannot be created in a collection requiring encryption"""
        copy_obj = os.path.join(self.enc_coll, 'copy')
        try:
            self.irods.data_objects.copy(self._orig_obj, copy_obj)
        except CUT_ACTION_PROCESSED_ERR:
            pass
        if self.irods.data_objects.exists(copy_obj):
            self.fail('unencrypted object copied into folder requiring encryption')
            self.ensure_obj_absent(copy_obj)
        self.ensure_obj_absent(self._orig_obj)

    def test_not_enc_allowed_in_not_enc_coll(self):
        """Test that an unencrypted file can be created in a collection not requiring encryption"""
        copy_obj = '/testing/home/copy'
        self.irods.data_objects.copy(self._orig_obj, copy_obj)
        if not self.irods.data_objects.exists(copy_obj):
            self.fail("file not copied to collection not requiring encryption")
        self.ensure_obj_absent(copy_obj)


class CyVerseEncryptionApiDataObjCreatePre(_CyverseEncryptionTestCase):
    """Tests of cyverse_encryption_api_data_obj_create_pre"""

    def test_enc_allowed_in_enc_coll(self):
        """Test that an encrypted files can be created in a collection requiring encryption"""
        obj = os.path.join(self.enc_coll, 'child.enc')
        self.irods.data_objects.create(obj)
        if not self.irods.data_objects.exists(obj):
            self.fail("encrypted file not created")
        self.irods.data_objects.unlink(obj, force=True)

    def test_not_enc_not_allowed_in_enc_coll(self):
        """Test that an unencrypted file cannot be created in a collection requiring encryption"""
        obj = os.path.join(self.enc_coll, 'child')
        try:
            self.irods.data_objects.create(obj)
        except CUT_ACTION_PROCESSED_ERR:
            pass
        if self.irods.data_objects.exists(obj):
            self.fail("unencrypted file created")
            self.irods.data_objects.unlink(obj, force=True)

    def test_not_enc_allowed_in_not_enc_coll(self):
        """Test that an unencrypted file can be created in a collection not requiring encryption"""
        obj = '/testing/home/obj'
        self.irods.data_objects.create(obj)
        if not self.irods.data_objects.exists(obj):
            self.fail("file not created")
        self.irods.data_objects.unlink(obj, force=True)


@test_rules.unimplemented
class CyVerseEncryptionApiDataObjCreateAndStatPre(_CyverseEncryptionTestCase):
    """
    Tests of cyverse_encryption_api_data_obj_create_and_stat_pre

    NOTE: As of iRODS 4.3.1, the pep_api_data_obj_create_and_stat_pre PEP is not
    called by any iRODS client.
    """


class CyverseEncryptionApiDataObjOpenPre(_CyverseEncryptionTestCase):
    """Tests of cyverse_encryption_api_data_obj_open_pre"""

    def test_enc_allowed_in_enc_coll(self):
        """Test that an encrypted files can be created in a collection requiring encryption"""
        obj = os.path.join(self.enc_coll, 'child.enc')
        self.irods.data_objects.open(obj, 'w')
        if not self.irods.data_objects.exists(obj):
            self.fail("encrypted file not created")
        self.irods.data_objects.unlink(obj, force=True)

    def test_not_enc_not_allowed_in_enc_coll(self):
        """Test that an unencrypted file cannot be created in a collection requiring encryption"""
        obj = os.path.join(self.enc_coll, 'child')
        try:
            self.irods.data_objects.open(obj, 'w')
        except CUT_ACTION_PROCESSED_ERR:
            pass
        if self.irods.data_objects.exists(obj):
            self.fail("unencrypted file created")
            self.irods.data_objects.unlink(obj, force=True)

    def test_not_enc_allowed_in_not_enc_coll(self):
        """Test that an unencrypted file can be created in a collection not requiring encryption"""
        obj = '/testing/home/obj'
        self.irods.data_objects.open(obj, 'w')
        if not self.irods.data_objects.exists(obj):
            self.fail("file not created")
        self.irods.data_objects.unlink(obj, force=True)


class CyverseEncryptionApiDataObjPutPre(_CyverseEncryptionTestCase):
    """Tests of cyverse_encryption_api_data_obj_put_pre"""

    def test_enc_allowed_in_enc_coll(self):
        """Test that an encrypted files can be uploaded into a collection requiring encryption"""
        if not self._attempt_put(self.enc_coll, "file.enc"):
            self.fail("Failed to upload encrypted file to collection requiring encryption")

    def test_not_enc_not_allowed_in_enc_coll(self):
        """
        Test that an unencrypted file cannot be uploaded into a collection requiring encryption
        """
        if self._attempt_put(self.enc_coll, 'file'):
            self.fail("Uploaded unencrypted file to collection requiring encryption")

    def test_not_enc_allowed_in_not_enc_coll(self):
        """
        Test that an unencrypted file can be uploaded into a collection not requiring encryption
        """
        if not self._attempt_put('/testing/home', 'file'):
            self.fail("Failed to upload unencrypted file to collection not requiring encryption")

    def _attempt_put(self, dest_coll: str, obj_name: str) -> bool:
        with NamedTemporaryFile(delete=False) as file:
            file.close()
            obj = os.path.join(dest_coll, obj_name)
            try:
                subprocess.run(
                    f"echo '{test_rules.IRODS_PASSWORD}' | iput '{file.name}' '{obj}'",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    check=True,
                    encoding='utf-8')
                self.ensure_obj_absent(obj)
            except CalledProcessError:
                return False
            return True


class CyverseEncryptionApiDataObjRenamePreData(_CyverseEncryptionTestCase):
    """Data object tests of cyverse_encryption_api_data_obj_rename_pre"""

    def setUp(self):
        super().setUp()
        self._orig_obj = '/testing/home/orig'
        self.irods.data_objects.create(self._orig_obj)

    def tearDown(self):
        self.ensure_obj_absent(self._orig_obj)
        super().tearDown()

    def test_enc_data_allowed_in_enc_coll(self):
        """Test that an encrypted files can be moved into a collection requiring encryption"""
        dest_obj = os.path.join(self.enc_coll, 'dest.enc')
        self.irods.data_objects.move(self._orig_obj, dest_obj)
        if not self.irods.data_objects.exists(dest_obj):
            self.fail("encrypted file not moved into collection requiring encryption")
        self.ensure_obj_absent(dest_obj)

    def test_not_enc_data_not_allowed_in_enc_coll(self):
        """Test that an unencrypted file cannot be moved into a collection requiring encryption"""
        dest_obj = os.path.join(self.enc_coll, 'dest')
        try:
            self.irods.data_objects.move(self._orig_obj, dest_obj)
        except CUT_ACTION_PROCESSED_ERR:
            pass
        if self.irods.data_objects.exists(dest_obj):
            self.fail("unencrypted file moved into collection requiring encryption")

    def test_not_enc_data_allowed_in_not_enc_coll(self):
        """Test that an unencrypted file can be moved into a collection not requiring encryption"""
        dest_obj = '/testing/home/dest'
        self.irods.data_objects.move(self._orig_obj, dest_obj)
        if not self.irods.data_objects.exists(dest_obj):
            self.fail("unencrypted file not moved into collection not requiring encryption")
        self.ensure_obj_absent(dest_obj)


class CyverseEncryptionApiDataObjRenamePreCollection(_CyverseEncryptionTestCase):
    """Collection tests of cyverse_encryption_api_data_obj_rename_pre"""

    def setUp(self):
        super().setUp()
        self._orig_coll = '/testing/home/rods/coll'
        self._new_enc_coll = os.path.join(self.enc_coll, 'coll')
        if not self.irods.collections.exists(self._orig_coll):
            self.irods.collections.create(self._orig_coll)
        if self.irods.collections.exists(self._new_enc_coll):
            self.ensure_coll_absent(self._new_enc_coll)

    def tearDown(self):
        for coll in [self._orig_coll, self._new_enc_coll]:
            if self.irods.collections.exists(coll):
                self.ensure_coll_absent(coll)
        super().tearDown()

    def test_enc_coll_allowed_in_enc_coll(self):
        """
        Test that a collection requiring data to be encrypted can be moved into a collection
        requiring encryption
        """
        self.irods.collections.get(self._orig_coll).metadata.set('encryption::required', 'true')  # type: ignore # noqa: E501 # pylint: disable=line-too-long
        self.irods.data_objects.create(os.path.join(self._orig_coll, 'obj.enc'))
        self.irods.collections.move(self._orig_coll, self._new_enc_coll)
        if not self.irods.collections.exists(self._new_enc_coll):
            self.fail("encrypted collection not moved into collection requiring encryption")

    def test_not_enc_coll_not_allowed_in_enc_coll(self):
        """
        Test that a collection not requiring data to be encrypted cannot be moved into a collection
        requiring encryption
        """
        self.irods.data_objects.create(os.path.join(self._orig_coll, 'obj'))
        try:
            self.irods.collections.move(self._orig_coll, self._new_enc_coll)
        except CUT_ACTION_PROCESSED_ERR:
            pass
        if self.irods.collections.exists(self._new_enc_coll):
            self.fail("unencrypted collection moved into collection requiring encryption")

    def test_not_enc_coll_allowed_in_not_enc_coll(self):
        """
        Test that a collection not requiring encryption can be moved into a collection not
        requiring encryption
        """
        self.irods.data_objects.create(os.path.join(self._orig_coll, 'obj'))
        new_coll = '/testing/home/rods/new_coll'
        self.irods.collections.move(self._orig_coll, new_coll)
        if not self.irods.collections.exists(new_coll):
            self.fail("unencrypted collection not moved into collection not requiring encryption")
        self.ensure_coll_absent(new_coll)


class CyverseEncryptionApiDataObjRenamePost(_CyverseEncryptionTestCase):
    """Tests cyverse_encryption_api_data_obj_rename_post"""

    def setUp(self):
        super().setUp()
        self._orig_path = '/testing/home/rods/orig_coll'
        self._mv_enc_path = os.path.join(self.enc_coll, 'moved_coll')
        self._mv_path = '/testing/home/rods/moved_coll'
        self.irods.collections.create(self._orig_path)
        self.ensure_coll_absent(self._mv_enc_path)
        self.ensure_coll_absent(self._mv_path)

    def tearDown(self):
        self.ensure_coll_absent(self._orig_path)
        super().tearDown()

    def test_coll_added_to_enc_coll(self):
        """Test that a collection added to a collection requiring encryption receives the AVU"""
        self.irods.collections.move(self._orig_path, self._mv_enc_path)
        coll = self.irods.collections.get(self._mv_enc_path)
        if coll.metadata.get_one('encryption::required').value != 'true':  # type: ignore
            self.fail("encryption::required AVU not set to 'true'")
        self.ensure_coll_absent(self._mv_enc_path)

    def test_coll_added_to_not_enc_coll(self):
        """
        Test that a collection added to a collection not requiring encryption doesn't receive the
        AVU
        """
        self.irods.collections.move(self._orig_path, self._mv_path)
        if 'encryption::required' in self.irods.collections.get(self._mv_path).metadata:  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail("encryption::required AVU set")
        self.ensure_coll_absent(self._mv_path)


@test_rules.unimplemented
class CyverseEncryptionApiStructFileExtAndRegPre(_CyverseEncryptionTestCase):
    """
    Tests of cyverse_encryption_api_struct_file_ext_and_reg_pre

    NOTE: As of iRODS 4.2.8, this rule is not called by any PEP.
    """


class CyverseEncryptionCheckrequiredcoll(_CyverseEncryptionTestCase):
    """Tests of _cyverse_encryption_checkRequiredColl"""

    def setUp(self):
        super().setUp()
        self._src_coll = '/testing/home/rods/coll'
        self.irods.collections.create(self._src_coll)

    def tearDown(self):
        self.ensure_coll_absent(self._src_coll)
        super().tearDown()

    def test_enc_coll_allowed_in_enc_coll(self):
        """
        Test that a collection requiring data to be encrypted can be moved into a collection
        requiring encryption when passing paths as paths
        """
        self.irods.collections.get(self._src_coll).metadata.set('encryption::required', 'true')  # type: ignore # noqa: E501 # pylint: disable=line-too-long
        self._for_all_str_path_combos(os.path.join(self.enc_coll, 'coll'), self._check_allowed)

    def test_not_enc_coll_not_allowed_in_enc_coll(self):
        """
        Test that a collection not requiring data to be encrypted cannot be moved into a collection
        requiring encryption
        """
        self.irods.data_objects.create(os.path.join(self._src_coll, 'data'))
        self._for_all_str_path_combos(os.path.join(self.enc_coll, 'coll'), self._check_disallowed)

    def test_not_enc_coll_allowed_in_not_enc_coll(self):
        """
        Test that a collection not requiring encryption can be moved into a collection not
        requiring encryption
        """
        self.irods.data_objects.create(os.path.join(self._src_coll, 'data'))
        self._for_all_str_path_combos('/testing/home/rods/new_coll', self._check_allowed)

    def _for_all_str_path_combos(self, dest_coll, test):
        for o in IrodsTestCase.prep_path(self._src_coll):
            for n in IrodsTestCase.prep_path(dest_coll):
                with self.subTest(o=o, n=n):
                    rule = self.mk_rule(
                        f"_cyverse_encryption_checkRequiredColl({repr(o)}, {repr(n)})")  # type: ignore # noqa: E501 # pylint: disable=line-too-long
                    test(rule)

    def _check_allowed(self, rule):
        try:
            self.exec_rule(rule, IrodsType.NONE)
        except CUT_ACTION_PROCESSED_ERR:
            self.fail("placement forbidden")

    def _check_disallowed(self, rule):
        try:
            self.exec_rule(rule, IrodsType.NONE)
            self.fail("placement allowed")
        except CUT_ACTION_PROCESSED_ERR:
            pass


class CyverseEncryptionCheckrequireddataobj(_CyverseEncryptionTestCase):
    """Tests of _cyverse_encryption_checkEncryptionRequiredForDataObj"""

    def test_enc_data_enc_required_path(self):
        """
        Verify doesn't fail for encrypted data when encryption required and path can have type path
        """
        self._for_str_and_path(os.path.join(self.enc_coll, 'data.enc'), self._check_allowed)

    def test_not_enc_data_enc_required_path(self):
        """Verify fails for unencrypted data when encryption required and path can have type path"""
        self._for_str_and_path(os.path.join(self.enc_coll, 'data'), self._check_disallowed)

    def test_enc_not_required_path(self):
        """Verify it works when enc not required and path can have type path"""
        self._for_str_and_path('/testing/home/rods/data', self._check_allowed)

    def _for_str_and_path(self, obj_path, test):
        for o in IrodsTestCase.prep_path(obj_path):
            with self.subTest(o=o):
                test(self.mk_rule(f"_cyverse_encryption_checkRequiredDataObj({repr(o)})"))  # type: ignore # noqa: E501 # pylint: disable=line-too-long

    def _check_allowed(self, rule):
        try:
            self.exec_rule(rule, IrodsType.NONE)
        except CUT_ACTION_PROCESSED_ERR:
            self.fail("placement forbidden")

    def _check_disallowed(self, rule):
        try:
            self.exec_rule(rule, IrodsType.NONE)
            self.fail("placement allowed")
        except CUT_ACTION_PROCESSED_ERR:
            pass


class CyverseEncryptionCopyparentavuEncRequired(_CyverseEncryptionTestCase):
    """Tests of _cyverse_encryption_copyParentAvu when encryption is required"""

    def setUp(self):
        super().setUp()
        self._parent = "/testing/home/rods/parent"
        self._coll = os.path.join(self._parent, "coll")
        self._child_coll = os.path.join(self._coll, "child_coll")
        self.irods.collections.create(self._child_coll)
        self._data = os.path.join(self._coll, "data")
        self.irods.data_objects.create(self._data)
        self._child_data = os.path.join(self._child_coll, "data")
        self.irods.data_objects.create(self._child_data)
        self.irods.collections.get(self._parent).metadata.set('encryption::required', 'true')  # type: ignore # noqa: E501 # pylint: disable=line-too-long
        self._mode = 'mode'
        self.irods.collections.get(self._parent).metadata.set('encryption::mode', self._mode)  # type: ignore # noqa: E501 # pylint: disable=line-too-long
        self.exec_rule(
            self.mk_rule(f"_cyverse_encryption_copyParentAvu({self._coll})"),
            IrodsType.NONE)

    def tearDown(self):
        self.irods.collections.remove(self._parent, force=True)
        super().tearDown()

    def test_enc_required_set_on_coll(self):
        """Test encryption::required AVU set on collection"""
        self._verify_avu(self._coll, "encryption::required", "true")

    def test_mode_set_on_coll(self):
        """Test correct mode set on collection"""
        self._verify_avu(self._coll, "encryption::mode", self._mode)

    def test_enc_required_set_on_sub_coll(self):
        """Test encryption::required AVU set on subcollections"""
        self._verify_avu(self._child_coll, "encryption::required", "true")

    def test_mode_set_on_sub_coll(self):
        """Test correct mode set on subcollections"""
        self._verify_avu(self._child_coll, "encryption::mode", self._mode)

    def test_enc_required_not_set_on_data(self):
        """Test encryption::required AVU not set on member data objects"""
        try:
            self.irods.data_objects.get(self._data).metadata.get_one("encryption::required")  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail("encryption::required set")
        except KeyError:
            pass

    def test_mode_not_set_on_sub_data(self):
        """Test not mode set on member data objects"""
        try:
            self.irods.data_objects.get(self._child_data).metadata.get_one("encryption::mode")  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail("encryption::mode set")
        except KeyError:
            pass

    def _verify_avu(self, coll, attr, val):
        try:
            avu = self.irods.collections.get(coll).metadata.get_one(attr)  # type: ignore
            if avu.value != val:
                self.fail(f"{attr} set incorrectly")
        except KeyError:
            self.fail(f"{attr} not set")


class CyverseEncryptionCopyparentavuEncNotRequired(_CyverseEncryptionTestCase):
    """Tests of _cyverse_encryption_copyParentAvu when encryption is not required"""

    def test_enc_required_not_set(self):
        """Test encryption::required not set on collection when not set on parent"""
        coll = "/testing/home/rods/coll"
        self.irods.collections.create(coll)
        self.exec_rule(self.mk_rule(f"_cyverse_encryption_copyParentAvu({coll})"), IrodsType.NONE)
        try:
            self.irods.collections.get(coll).metadata.get_one("encryption::required")  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail("encryption::required set")
        except KeyError:
            pass
        self.ensure_coll_absent(coll)


class CyverseEncryptionRejectbulkregifencryptionrequired(_CyverseEncryptionTestCase):
    """Tests of _cyverse_encryption_rejectBulkRegIfRequired"""

    def test_required_path(self):
        """
        Test that it fails when the parent requires encryption and the collection is provided as a
        path.
        """
        for p in IrodsTestCase.prep_path(os.path.join(self.enc_coll, 'coll')):
            with self.subTest(p=p):
                call = self.mk_rule(f"_cyverse_encryption_rejectBulkRegIfRequired({p})")
                try:
                    self.exec_rule(call, IrodsType.NONE)
                    self.fail("should fail when encryption required")
                except CUT_ACTION_PROCESSED_ERR:
                    pass

    def test_not_required_path(self):
        """
        Test that it succeeds when the parent doesn't require encryption and the collection is
        provided as a path.
        """
        for p in IrodsTestCase.prep_path('/testing/home/rods/coll'):
            with self.subTest(p=p):
                call = self.mk_rule(f"_cyverse_encryption_rejectBulkRegIfRequired('{p}')")
                try:
                    self.exec_rule(call, IrodsType.NONE)
                except CUT_ACTION_PROCESSED_ERR:
                    self.fail("should not fail when encryption not required")


class CyverseEncryptionRequired(_CyverseEncryptionTestCase):
    """Tests of _cyverse_encryption_required"""

    def test_attr_set_true_path(self):
        """test when collection is provided as path with encryption::required set to true"""
        for p in IrodsTestCase.prep_path(self.enc_coll):
            with self.subTest(p=p):
                self.fn_test('_cyverse_encryption_required', [p], IrodsVal.boolean(True))

    def test_attr_set_false_path(self):
        """test when collection is provided as path with encryption::required set to false"""
        coll = '/testing/home/rods'
        self.irods.collections.get(coll).metadata.set('encryption::required', 'false')  # type: ignore # noqa: E501 # pylint: disable=line-too-long
        for p in IrodsTestCase.prep_path(coll):
            with self.subTest(p=p):
                self.fn_test('_cyverse_encryption_required', [p], IrodsVal.boolean(False))
        self.irods.collections.get(coll).metadata.remove('encryption::required', 'false', '')  # type: ignore # noqa: E501 # pylint: disable=line-too-long

    def test_attr_not_set_path(self):
        """test when collection is provided as path with encryption::required unset"""
        for p in IrodsTestCase.prep_path('/testing/home'):
            with self.subTest(p=p):
                self.fn_test('_cyverse_encryption_required', [p], IrodsVal.boolean(False))


if __name__ == "__main__":
    unittest.main()
