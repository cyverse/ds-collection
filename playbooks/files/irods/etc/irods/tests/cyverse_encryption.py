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
from test_rules import IrodsTestCase


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
        coll = self.irods.collections.get(self._enc_coll)
        if coll:
            coll.metadata.remove('encryption::required', 'true', '')
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
        child = self.irods.collections.create(os.path.join(self.enc_coll, 'child'))
        if child.metadata.get_one('encryption::required').value != 'true':  # type: ignore
            self.fail("encryption::required AVU not set to 'true'")
        child.remove(force=True)  # type: ignore

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


@test_rules.unimplemented
class CyverseEncryptionApiDataObjOpenStatPre(_CyverseEncryptionTestCase):
    """
    Tests of cyverse_encryption_api_data_obj_open_stat_pre

    NOTE: As of iRODS 4.3.1, the pep_api_data_obj_open_and_stat_pre PEP is not
    called by any iRODS client.
    """


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
            self.irods.collections.remove(self._new_enc_coll, force=True, recurse=True)

    def tearDown(self):
        for coll in [self._orig_coll, self._new_enc_coll]:
            if self.irods.collections.exists(coll):
                self.irods.collections.remove(coll, force=True, recurse=True)
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
        self.irods.collections.remove(new_coll, force=True, recurse=True)


class CyverseEncryptionApiDataObjRenamePost(_CyverseEncryptionTestCase):
    """Tests cyverse_encryption_api_data_obj_rename_post"""

    def test_coll_added_to_enc_coll(self):
        """Test that a collection added to a collection requiring encryption receives the AVU"""
        orig_path = '/testing/home/rods/orig_coll'
        self.irods.collections.create(orig_path)
        mv_path = os.path.join(self.enc_coll, 'moved_coll')
        self.irods.collections.move(orig_path, mv_path)
        coll = self.irods.collections.get(mv_path)
        if coll.metadata.get_one('encryption::required').value != 'true':  # type: ignore
            self.fail("encryption::required AVU not set to 'true'")
        coll.remove(force=True)  # type: ignore

    @unittest.skip("not implemented")
    def test_coll_added_to_not_enc_coll(self):
        """
        Test that a collection added to a collection not requiring encryption doesn't receive the
        AVU
        """
        orig_path = '/testing/home/rods/orig_coll'
        self.irods.collections.create(orig_path)
        mv_path = '/testing/home/rods/moved_coll'
        self.irods.collections.move(orig_path, mv_path)
        coll = self.irods.collections.get(mv_path)
        if self.irods.collections.get(mv_path).metadata.items().get('encryption::required'):  # type: ignore # noqa: E501 # pylint: disable=line-too-long
            self.fail("encryption::required AVU not set to 'true'")
        coll.remove(force=True)  # type: ignore


@test_rules.unimplemented
class CyverseEncryptionApiStructFileExtAndRegPre(_CyverseEncryptionTestCase):
    """
    Tests of cyverse_encryption_api_struct_file_ext_and_reg_pre

    NOTE: As of iRODS 4.2.8, this rule is not called by any PEP.
    """


class CyverseEncryptionTests(_CyverseEncryptionTestCase):
    """The cyverse_encryption.re tests"""

    @unittest.skip("not implemented")
    def test_ipcisencryptionrequired(self):
        """Test _ipcIsEncryptionRequired"""

    @unittest.skip("not implemented")
    def test_ipcencryptioncheckencryptionrequiredfordataobj(self):
        """Test _ipcEncryptionCheckEncryptionRequiredForDataObj"""

    @unittest.skip("not implemented")
    def test_ipcencryptioncheckencryptionrequiredforcollinternal(self):
        """Test _ipcEncryptionCheckEncryptionRequiredForCollInternal"""

    @unittest.skip("not implemented")
    def test_ipcencryptioncheckencryptionrequiredforcoll(self):
        """Test _ipcEncryptionCheckEncryptionRequiredForColl"""

    @unittest.skip("not implemented")
    def test_ipcencryptionrejectbulkregifencryptionrequired(self):
        """Test _ipcEncryptionRejectBulkRegIfEncryptionRequired"""

    @unittest.skip("not implemented")
    def test_ipcencryptioncopyavufromparentinternal(self):
        """Test _ipcEncryptionCopyAVUFromParentInternal"""

    @unittest.skip("not implemented")
    def test_ipcencryptioncopyavufromparent(self):
        """Test _ipcEncryptionCopyAVUFromParent"""


if __name__ == "__main__":
    unittest.main()
