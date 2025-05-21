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
from test_rules import IrodsTestCase

_TEST_FILE = '/testing/home/rods/tmp'


class TestPepApiDataObjCreatePre(IrodsTestCase):
    """Test pep_api_data_obj_create_pre"""

    def setUp(self):
        """Add stubbed out version of cyverse_encryption.re to the server."""
        super().setUp()
        self.update_rulebase('cyverse_encryption.re', 'mocks/cyverse_encryption.re')
        self.irods.data_objects.create(_TEST_FILE)

    def tearDown(self):
        """Remove stubbed out version of cyverse_encryption.re from the server."""
        self.update_rulebase('cyverse_encryption.re', "../cyverse_encryption.re")
        self.ensure_obj_absent(_TEST_FILE)
        super().tearDown()

    def test_ipcencryption_called(self):
        """Test that the rule is called."""
        for line in self.tail_rods_log():
            if 'ipcEncryption_api_data_obj_create_pre' in line:
                return
        self.fail('ipcEncryption_api_data_obj_create_pre not called')


class TestPepApiDataObjOpenPre(IrodsTestCase):
    """Test pep_api_data_obj_open_pre"""

    def setUp(self):
        """Add stubbed out version of cyverse_encryption.re to the server."""
        super().setUp()
        self.irods.data_objects.create(_TEST_FILE)
        self.update_rulebase('cyverse_encryption.re', 'mocks/cyverse_encryption.re')

    def tearDown(self):
        """Remove stubbed out version of cyverse_encryption.re from the server."""
        self.update_rulebase('cyverse_encryption.re', "../cyverse_encryption.re")
        self.ensure_obj_absent(_TEST_FILE)
        super().tearDown()

    def test_ipcencryption_called(self):
        """Test that the rule is called."""
        with self.irods.data_objects.open(_TEST_FILE, mode='r', create=False):
            for line in self.tail_rods_log():
                if 'ipcEncryption_api_data_obj_open_pre' in line:
                    return
            self.fail('ipcEncryption_api_data_obj_open_pre not called')


class TestPepApiDataObjPutPre(IrodsTestCase):
    """Test pep_api_data_obj_put_pre"""

    def setUp(self):
        """Add stubbed out version of cyverse_encryption.re to the server."""
        super().setUp()
        self._file = NamedTemporaryFile(delete=False)
        self._file.close()
        self.update_rulebase('cyverse_encryption.re', 'mocks/cyverse_encryption.re')
        try:
            subprocess.run(
                f"echo '{test_rules.IRODS_PASSWORD}' | iput '{self._file.name}' '{_TEST_FILE}'",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                check=True,
                encoding='utf-8')
        except CalledProcessError as e:
            raise RuntimeError(f"{e.stderr}") from e

    def tearDown(self):
        """Remove stubbed out version of cyverse_encryption.re from the server."""
        self.update_rulebase('cyverse_encryption.re', "../cyverse_encryption.re")
        self.ensure_obj_absent(_TEST_FILE)
        os.unlink(self._file.name)
        super().tearDown()

    def test_ipcencryption_called(self):
        """Test that the rule is called."""
        for line in self.tail_rods_log():
            if 'ipcEncryption_api_data_obj_put_pre' in line:
                return
        self.fail('ipcEncryption_api_data_obj_put_pre not called')


class TestCyVerseCore(IrodsTestCase):

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
    def test_pepcollcreatepost(self):
        """Test pep_coll_create_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcopypre(self):
        """Test pep_api_data_obj_copy_pre"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcopypost(self):
        """Test pep_api_data_obj_copy_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcreatepost(self):
        """Test pep_api_data_obj_create_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcreateandstatpre(self):
        """Test pep_api_data_obj_create_and_stat_pre"""

    @unittest.skip("not implemented")
    def test_pepapidataobjopenandstatpre(self):
        """Test pep_api_data_obj_open_and_stat_pre"""

    @unittest.skip("not implemented")
    def test_pepapidataobjputpost(self):
        """Test pep_api_data_obj_put_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjrenamepre(self):
        """Test pep_api_data_obj_rename_pre"""

    @unittest.skip("not implemented")
    def test_pepapidataobjrenamepost(self):
        """Test pep_api_data_obj_rename_post"""

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
    def test_pepapistructfileextandregpre(self):
        """Test pep_api_struct_file_ext_and_reg_pre"""

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
