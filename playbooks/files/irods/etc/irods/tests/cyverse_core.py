#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_core.re rule logic."""

import os
import subprocess
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
import unittest

import test_rules
from test_rules import IrodsTestCase, IrodsType

from irods.exception import USER_FILE_DOES_NOT_EXIST


def setUpModule():  # pylint: disable=invalid-name
    """Set up the module."""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down the module."""
    test_rules.tearDownModule()


class CyVerseCoreTestCase(IrodsTestCase):
    """Base class for CyVerse core tests."""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_file = '/testing/home/rods/tmp'

    @property
    def artifact_file(self) -> str:
        """A file name to be used for testing"""
        return self._test_file

    def setUp(self):
        """Set up the test case."""
        super().setUp()
        self.update_rulebase('cyverse_encryption.re', 'mocks/cyverse_encryption.re')

    def tearDown(self):
        """Tear down the test case."""
        self.update_rulebase('cyverse_encryption.re', '../cyverse_encryption.re')
        super().tearDown()

    def verify_msg_logged(self, msg_frag) -> bool:
        """Verify that a message fragment was logged"""
        for line in self.tail_rods_log():
            if msg_frag in line:
                return True
        return False


class PepApiCollCreatePostTest(CyVerseCoreTestCase):
    """Test pep_api_coll_create_post"""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_coll = '/testing/home/rods/test_coll'

    def setUp(self):
        """Add stubbed out version of cyverse_encryption.re to the server."""
        super().setUp()
        self._ensure_test_coll_absent()
        self.irods.collections.create(self._test_coll)

    def tearDown(self):
        """Remove stubbed out version of cyverse_encryption.re from the server."""
        self._ensure_test_coll_absent()
        super().tearDown()

    def _ensure_test_coll_absent(self):
        try:
            self.irods.collections.remove(self._test_coll, force=True)
        except USER_FILE_DOES_NOT_EXIST:
            pass

    def test_cyverseencryption_called(self):
        """Test that the cyverse_encryption PEP is called."""
        if not self.verify_msg_logged('cyverse_encryption_api_coll_create_post'):
            self.fail('cyverse_encryption_api_coll_create_post not called')

    @unittest.skip("not implemented")
    def test_ipctrash_called(self):
        """Test that the ipc-trash PEP is called."""


class PepApiDataObjCopyPreTest(CyVerseCoreTestCase):
    """Test pep_api_data_obj_copy_pre"""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_copy = '/testing/home/rods/test_copy'

    def setUp(self):
        super().setUp()
        self.irods.data_objects.create(self.artifact_file)

    def tearDown(self):
        self.ensure_obj_absent(self._test_copy)
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    def test_cyverseencryption_called(self):
        """Test that the cyverse_encryption version of the rule is called"""
        self.irods.data_objects.copy(self.artifact_file, self._test_copy)
        if not self.verify_msg_logged('cyverse_encryption_api_data_obj_copy_pre'):
            self.fail('cyverse_encryption_api_data_obj_copy_pre not called')


class PepApiDataObjCreatePreTest(CyVerseCoreTestCase):
    """Test pep_api_data_obj_create_pre"""

    def setUp(self):
        """Add stubbed out version of cyverse_encryption.re to the server."""
        super().setUp()
        self.irods.data_objects.create(self.artifact_file)

    def tearDown(self):
        """Remove stubbed out version of cyverse_encryption.re from the server."""
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    def test_cyverseencryption_called(self):
        """Test that the rule is called."""
        if not self.verify_msg_logged('cyverse_encryption_api_data_obj_create_pre'):
            self.fail('cyverse_encryption_api_data_obj_create_pre not called')


class PepApiDataObjCreateAndStatPreTest(CyVerseCoreTestCase):
    """
    Test pep_api_data_obj_create_and_stat_pre.

    NOTE: As of iRODS 4.3.1, this PEP is not currently called by any iRODS client.
    """

    def test_cyverseencryption_called(self):
        """Test that cyverse_encryption's version of this rule"""
        self.exec_rule(
            self.mk_rule("pep_api_data_obj_create_and_stat_pre('', '', '', '')"), IrodsType.NONE)
        if not self.verify_msg_logged('cyverse_encryption_api_data_obj_create_and_stat_pre'):
            self.fail('cyverse_encryption_api_data_obj_create_and_stat_pre not called')


class PepApiDataObjOpenPreTest(CyVerseCoreTestCase):
    """Test pep_api_data_obj_open_pre"""

    def setUp(self):
        """Add stubbed out version of cyverse_encryption.re to the server."""
        super().setUp()
        self.irods.data_objects.create(self.artifact_file)

    def tearDown(self):
        """Remove stubbed out version of cyverse_encryption.re from the server."""
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    def test_cyverseencryption_called(self):
        """Test that the rule is called."""
        with self.irods.data_objects.open(self.artifact_file, mode='r', create=False):
            if not self.verify_msg_logged('cyverse_encryption_api_data_obj_create_pre'):
                self.fail('ipcEncryption_api_data_obj_open_pre not called')


class PepApiDataObjOpenAndStatPreTest(CyVerseCoreTestCase):
    """
    Test pep_api_data_obj_open_and_stat_pre"

    NOTE: As of iRODS 4.3.1, this PEP is not currently called by any iRODS client.
    """

    def test_cyverseencryption_called(self):
        """Test that cyverse_encryption's version of this rule"""
        self.exec_rule(
            self.mk_rule("pep_api_data_obj_open_and_stat_pre('', '', '', '')"), IrodsType.NONE)
        if not self.verify_msg_logged('cyverse_encryption_api_data_obj_open_and_stat_pre'):
            self.fail('cyverse_encryption_api_data_obj_open_and_stat_pre not called')


class PepApiDataObjPutPreTest(CyVerseCoreTestCase):
    """Test pep_api_data_obj_put_pre"""

    def setUp(self):
        """Add stubbed out version of cyverse_encryption.re to the server."""
        super().setUp()
        self._file = NamedTemporaryFile(delete=False)
        self._file.close()
        try:
            cmd = f"""
                echo '{test_rules.IRODS_PASSWORD}' | iput '{self._file.name}' '{self.artifact_file}'
            """
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                check=True,
                encoding='utf-8')
        except CalledProcessError as e:
            raise RuntimeError(f"{e.stderr}") from e

    def tearDown(self):
        """Remove stubbed out version of cyverse_encryption.re from the server."""
        self.ensure_obj_absent(self.artifact_file)
        os.unlink(self._file.name)
        super().tearDown()

    def test_cyverseencryption_called(self):
        """Test that the rule is called."""
        if not self.verify_msg_logged('cyverse_encryption_api_data_obj_put_pre'):
            self.fail('cyverse_encryption_api_data_obj_put_pre not called')


class PepApiDataObjRename(CyVerseCoreTestCase):
    """Test pep_api_data_obj_rename_pre"""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_rename = '/testing/home/rods/test_rename'

    def setUp(self):
        super().setUp()
        self.irods.data_objects.create(self.artifact_file)
        self.irods.data_objects.move(self.artifact_file, self._test_rename)

    def tearDown(self):
        self.ensure_obj_absent(self._test_rename)
        super().tearDown()

    def test_cyverseencryption_post_called(self):
        """Test that the cyverse_encryption logic attached to this post PEP is called"""
        if not self.verify_msg_logged("cyverse_encryption_api_data_obj_rename_post"):
            self.fail('cyverse_encryption_api_data_obj_rename_post not called')

    def test_cyverseencryption_pre_called(self):
        """Test that the cyverse_encryption logic attached to this pre PEP is called"""
        if not self.verify_msg_logged("cyverse_encryption_api_data_obj_rename_pre"):
            self.fail('cyverse_encryption_api_data_obj_rename_pre not called')

    @unittest.skip("not implemented")
    def test_ipctrash_called(self):
        """Test that the ipc-trash logic attached to these PEPs is called"""


@test_rules.unimplemented
class PepApiStructFileExtAndRegPre(CyVerseCoreTestCase):
    """Test pep_api_struct_file_ext_and_reg_pre

    XXX: This PEP is broken because of bug
    https://github.com/irods/irods/issues/7413. It is fixed in iRODS 4.3.
    """


class CyVerseCoreTest(CyVerseCoreTestCase):
    """Test the cyverse_core.re rule-base"""

    @unittest.skip("not implemented")
    def test_accreatecollbyadmin(self):
        """Test acCreateCollByAdmin"""

    @unittest.skip("not implemented")
    def test_accreatedefaultcollections(self):
        """Test acCreateDefaultCollections"""

    @unittest.skip("not implemented")
    def test_acdatadeletepolicy(self):
        """Test acDataDeletePolicy"""

    @unittest.skip("not implemented")
    def test_acdeletecollbyadmin(self):
        """Test acDeleteCollByAdmin"""

    @unittest.skip("not implemented")
    def test_acdeleteobjbyadminifpresent(self):
        """Test acDeleteObjByAdminIfPresent"""

    @unittest.skip("not implemented")
    def test_acpreconnect(self):
        """Test acPreConnect"""

    @unittest.skip("not implemented")
    def test_acsetnumthreads(self):
        """Test acSetNumThreads"""

    @unittest.skip("not implemented")
    def test_acsetrescschemeforcreate(self):
        """Test acSetRescSchemeForCreate"""

    @unittest.skip("not implemented")
    def test_acsetrescschemeforrepl(self):
        """Test acSetRescSchemeForRepl"""

    @unittest.skip("not implemented")
    def test_acsetreservernumproc(self):
        """Test acSetReserveNumProc"""

    @unittest.skip("not implemented")
    def test_acpreprocformodifyaccesscontrol(self):
        """Test acPreProcForModifyAccessControl"""

    @unittest.skip("not implemented")
    def test_acpreprocformodifyavumetadata(self):
        """Test acPreProcForModifyAVUMetadata"""

    @unittest.skip("not implemented")
    def test_acppreprocforrmcoll(self):
        """Test acPreProcForRmColl"""

    @unittest.skip("not implemented")
    def test_acpostprocforcollcreate(self):
        """Test acPostProcForCollCreate"""

    @unittest.skip("not implemented")
    def test_acpostprocfordatacopyreceived(self):
        """Test acPostProcForDataCopyReceived"""

    @unittest.skip("not implemented")
    def test_acpostprocfordelete(self):
        """Test acPostProcForDelete"""

    @unittest.skip("not implemented")
    def test_acpostprocformodifyaccesscontrol(self):
        """Test acPostProcForModifyAccessControl"""

    @unittest.skip("not implemented")
    def test_acpostprocformodifyavumetadata(self):
        """Test acPostProcForModifyAVUMetadata"""

    @unittest.skip("not implemented")
    def test_acpostprocforobjrename(self):
        """Test acPostProcForObjRename"""

    @unittest.skip("not implemented")
    def test_acpostprocforopen(self):
        """Test acPostProcForOpen"""

    @unittest.skip("not implemented")
    def test_acpostprocforparalleltransferreceived(self):
        """Test acPostProcForParallelTransferReceived"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcopypost(self):
        """Test pep_api_data_obj_copy_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcreatepost(self):
        """Test pep_api_data_obj_create_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjputpost(self):
        """Test pep_api_data_obj_put_post"""

    @unittest.skip("not implemented")
    def test_pepapiadataobjunlinkpre(self):
        """Test pep_api_data_obj_unlink_pre"""

    @unittest.skip("not implemented")
    def test_pepapiadataobjunlinkpost(self):
        """Test pep_api_data_obj_unlink_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjunlinkexcept(self):
        """Test pep_api_data_obj_unlink_except"""

    @unittest.skip("not implemented")
    def test_pepapirmcollpre(self):
        """Test pep_api_rm_coll_pre"""

    @unittest.skip("not implemented")
    def test_pepapirmcollexcept(self):
        """Test pep_api_rm_coll_except"""

    @unittest.skip("not implemented")
    def test_getobjpath(self):
        """ Test _cyverse_core_getObjPath """

    @unittest.skip("not implemented")
    def test_mkdataobjsessvar(self):
        """ Test _cyverse_core_mkDataObjSessVar """

    @unittest.skip("not implemented")
    def test_dataobjcreated(self):
        """ Test _cyverse_core_dataObjCreated """

    @unittest.skip("not implemented")
    def test_dataobjmodified(self):
        """ Test _cyverse_core_dataObjModified """

    @unittest.skip("not implemented")
    def test_dataobjmetadatamodified(self):
        """ Test _cyverse_core_dataObjMetadataModified """

    @unittest.skip("not implemented")
    def test_pepdatabaseclosepost(self):
        """ Test pep_database_close_post """

    @unittest.skip("not implemented")
    def test_pepdatabaseclosefinally(self):
        """ Test pep_database_close_finally """

    @unittest.skip("not implemented")
    def test_pepdatabasemoddataobjmetapost(self):
        """ Test pep_database_mod_data_obj_meta_post """

    @unittest.skip("not implemented")
    def test_pepdatabaseregdataobjpost(self):
        """ Test pep_database_reg_data_obj_post """

    @unittest.skip("not implemented")
    def test_pepresourceresolvehierarchypre(self):
        """ Test pep_resource_resolve_hierarchy_pre """


if __name__ == "__main__":
    unittest.main()
