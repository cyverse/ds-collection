#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_core.re rule logic."""

from abc import ABC, abstractmethod
import os
import unittest

from irods.exception import (
    CAT_NO_ROWS_FOUND,
    CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME,
    FAIL_ACTION_ENCOUNTERED_ERR,
    UserDoesNotExist,
)

import test_rules
from test_rules import IrodsTestCase, IrodsType, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up the module."""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down the module."""
    test_rules.tearDownModule()


class CyverseCoreTestCase(IrodsTestCase):
    """Base class for CyVerse core tests."""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_file = "/testing/home/rods/tmp"

    @property
    def artifact_file(self) -> str:
        """A file name to be used for testing"""
        return self._test_file

    def setUp(self):
        super().setUp()
        self.update_rulebase(
            [
                ("cyverse_encryption.re", "mocks/cyverse_encryption.re"),
                ("cyverse_logic.re", "mocks/cyverse_logic.re"),
                ("cyverse_repl.re", "mocks/cyverse_repl.re"),
                ("cyverse_trash.re", "mocks/cyverse_trash.re"),
                ("coge.re", "mocks/coge.re"),
            ]
        )

    def tearDown(self):
        self.update_rulebase(
            [
                ("coge.re", "../../files/irods/etc/irods/coge.re"),
                ("cyverse_trash.re", "../../files/irods/etc/irods/cyverse_trash.re"),
                ("cyverse_repl.re", "../../files/irods/etc/irods/cyverse_repl.re"),
                ("cyverse_logic.re", "../../files/irods/etc/irods/cyverse_logic.re"),
                (
                    "cyverse_encryption.re",
                    "../../files/irods/etc/irods/cyverse_encryption.re",
                ),
            ]
        )
        super().tearDown()

    def verify_msg_logged(self, msg_frag) -> bool:
        """Verify that a message fragment was logged"""
        for line in self.tail_rods_log():
            if msg_frag in line:
                return True
        return False


class CyverseCoreMkdataobjsessvarTest(CyverseCoreTestCase):
    """Tests of  _cyverse_core_mkDataObjSessVar"""

    def test(self):
        """Test it"""
        for p in IrodsTestCase.prep_path("/a/path"):
            with self.subTest(p=p):
                self.fn_test(
                    "_cyverse_core_mkDataObjSessVar",
                    [p],
                    IrodsVal.string("ipc-data-obj-/a/path"),
                )


class CyverseCoreDataobjcreated(ABC, CyverseCoreTestCase):
    """The base class for _cyverse_core_dataObjCreated tests"""

    def setUp(self):
        super().setUp()
        test_rules.clear_rods_log()
        rule = f"""
            *dataObjInfo.logical_path = '/{self.irods.zone}/home/{self.irods.username}/obj';
            _cyverse_core_dataObjCreated(
                '{self.irods.username}', '{self.irods.zone}', *dataObjInfo, '{self.step()}' );
        """
        self.exec_rule(self.mk_rule(rule), IrodsType.NONE)

    @abstractmethod
    def step(self) -> str:
        """The step being tested"""

    @property
    def coge_log_msg(self) -> str:
        """The message logged by the coge.re mock"""
        return f"coge_dataObjCreated({self.irods.username}, {self.irods.zone}, DataObjInfo)"

    @property
    def cyverselogic_log_msg(self) -> str:
        """The message logged by the cyverse_logic.re mock"""
        user = self.irods.username
        zone = self.irods.zone
        return (
            f"cyverse_logic_dataObjCreated({user}, {zone}, DataObjInfo, {self.step()})"
        )

    @property
    def cyverserepl_log_msg(self) -> str:
        """The message logged by cyverse_repl.re mock"""
        return f"cyverse_repl_dataObjCreated({self.irods.username}, {self.irods.zone}, DataObjInfo)"


class CyverseCoreDataobjcreatedFull(CyverseCoreDataobjcreated):
    """Tests _cyverse_core_dataObjCreated where Step=FULL"""

    def test_coge(self):
        """verify coge called"""
        if not self.verify_msg_logged(self.coge_log_msg):
            self.fail("coge_dataObjCreated not called")

    def test_cyverselogic(self):
        """verify cyverse_logic called"""
        if not self.verify_msg_logged(self.cyverselogic_log_msg):
            self.fail("cyverse_logic_dataObjCreated not called")

    def test_cyverserepl(self):
        """verify cyverse_repl called"""
        if not self.verify_msg_logged(self.cyverserepl_log_msg):
            self.fail("cyverse_repl_dataObjCreated not called")

    def step(self):
        return "FULL"


class CyverseCoreDataobjcreatedStart(CyverseCoreDataobjcreated):
    """Tests _cyverse_core_dataObjCreated where Step=START"""

    def test_coge(self):
        """verify coge called"""
        if not self.verify_msg_logged(self.coge_log_msg):
            self.fail("coge_dataObjCreated not called")

    def test_cyverselogic(self):
        """verify cyverse_logic called"""
        if not self.verify_msg_logged(self.cyverselogic_log_msg):
            self.fail("cyverse_logic_dataObjCreated not called")

    def test_cyverserepl(self):
        """verify cyverse_repl not called"""
        if self.verify_msg_logged(self.cyverserepl_log_msg):
            self.fail("cyverse_repl_dataObjCreated called")

    def step(self):
        return "START"


class CyverseCoreDataobjcreatedFinish(CyverseCoreDataobjcreated):
    """Tests _cyverse_core_dataObjCreated where Step=FINISH"""

    def test_coge(self):
        """verify coge not called"""
        if self.verify_msg_logged(self.coge_log_msg):
            self.fail("coge_dataObjCreated called")

    def test_cyverselogic(self):
        """verify cyverse_logic called"""
        if not self.verify_msg_logged(self.cyverselogic_log_msg):
            self.fail("cyverse_logic_dataObjCreated not called")

    def test_cyverserepl(self):
        """verify cyverse_repl called"""
        if not self.verify_msg_logged(self.cyverserepl_log_msg):
            self.fail("cyverse_repl_dataObjCreated not called")

    def step(self):
        return "FINISH"


class CyverseCoreDataobjmetadatamodifiedTest(CyverseCoreTestCase):
    """Tests of _cyverse_core_dataObjMetadataModified"""

    def test_cyverselogic(self):
        """Verify that cyverse_logic is called"""
        test_rules.clear_rods_log()
        rule = f"""
            _cyverse_core_dataObjMetadataModified(
                '{self.irods.username}', '{self.irods.zone}', /path/to/data );
        """
        self.exec_rule(self.mk_rule(rule), IrodsType.NONE)
        msg = f"""
            cyverse_logic_dataObjMetaMod({self.irods.username}, {self.irods.zone}, /path/to/data)
        """
        if self.verify_msg_logged(msg):
            self.fail("cyverse_repl_dataObjCreated called")


class AccreateuserzonecollectionsGroup(CyverseCoreTestCase):
    """Test acCreateUserZoneCollections group creation"""

    def setUp(self):
        super().setUp()
        self._group_name = "testers"
        try:
            self.irods.groups.create(self._group_name)
        except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            pass

    def tearDown(self):
        self.irods.groups.remove(self._group_name)
        super().tearDown()

    def test_no_home_coll(self):
        """Test that no home collection is created for the group"""
        home = os.path.join("/", self.irods.zone, "home", self._group_name)
        if self.irods.collections.exists(home):
            self.fail("home collection created for group")

    def test_no_trash_coll(self):
        """Test that no trash collection is created for the group"""
        trash = os.path.join("/", self.irods.zone, "trash/home", self._group_name)
        if self.irods.collections.exists(trash):
            self.fail("trash collection created for group")


class AccreateuserzonecollectionsUser(CyverseCoreTestCase):
    """Test acCreateUserZoneCollections user creation"""

    def setUp(self):
        super().setUp()
        self._user_name = "tester"
        try:
            self.irods.users.remove(self._user_name)
        except UserDoesNotExist:
            pass
        self.irods.users.create(self._user_name, "rodsuser")

    def tearDown(self):
        self.irods.users.remove(self._user_name)
        super().tearDown()

    def test_home_coll(self):
        """Verify that when a user is created, a home collection is created"""
        home = os.path.join("/", self.irods.zone, "home", self._user_name)
        if not self.irods.collections.exists(home):
            self.fail(f"home collection {home} not created for user {self._user_name}")

    def test_trash_coll(self):
        """Verify that when a user is created, a trash collection is created"""
        trash = os.path.join("/", self.irods.zone, "trash/home", self._user_name)
        if not self.irods.collections.exists(trash):
            self.fail(f"trash collection {trash} created for user {self._user_name}")


class Acsetrescschemeforcreate(CyverseCoreTestCase):
    """Tests of acSetRescSchemeForCreate"""

    def test_cyverserepl_called(self):
        """Verify that the cyverse_repl.re version is called"""
        self.ensure_obj_absent(self.artifact_file)
        self.irods.data_objects.create(self.artifact_file)
        exp_msg = f"cyverse_repl_acSetRescSchemeForCreate({self.artifact_file})"
        if not self.verify_msg_logged(exp_msg):
            self.fail(
                f"cyverse_repl_acSetRescSchemeForCreate({self.artifact_file}) not called"
            )
        self.ensure_obj_absent(self.artifact_file)


class Acsetrescschemeforrepl(CyverseCoreTestCase):
    """Tests of acSetRescSchemeForRepl"""

    def test_cyverserepl_called(self):
        """Verify that the cyverse_repl.re version is called"""
        self.ensure_obj_absent(self.artifact_file)
        obj = self.irods.data_objects.create(self.artifact_file)
        obj.replicate()
        exp_msg = f"cyverse_repl_acSetRescSchemeForRepl({self.artifact_file})"
        if not self.verify_msg_logged(exp_msg):
            self.fail("cyverse_repl_acSetRescSchemeForRepl not called")
        self.ensure_obj_absent(self.artifact_file)


class PepApiCollCreatePostTest(CyverseCoreTestCase):
    """Test pep_api_coll_create_post"""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_coll = "/testing/home/rods/test_coll"

    def setUp(self):
        super().setUp()
        self._ensure_test_coll_absent()
        self.irods.collections.create(self._test_coll)

    def tearDown(self):
        self._ensure_test_coll_absent()
        super().tearDown()

    def _ensure_test_coll_absent(self):
        self.ensure_coll_absent(self._test_coll)

    def test_cyverseencryption_called(self):
        """Test that the cyverse_encryption PEP is called."""
        if not self.verify_msg_logged("cyverse_encryption_api_coll_create_post"):
            self.fail("cyverse_encryption_api_coll_create_post not called")

    def test_cyversetrash_called(self):
        """Test that the cyverse_trash PEP is called."""
        if not self.verify_msg_logged("cyverse_trash_api_coll_create_post"):
            self.fail("cyverse_trash_api_coll_create_post not called")


class PepApiDataObjCopyPostTest(CyverseCoreTestCase):
    """Test pep_api_data_obj_copy_post"""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_copy = "/testing/home/rods/test_copy"

    def setUp(self):
        super().setUp()
        self.ensure_obj_absent(self._test_copy)
        self.irods.data_objects.create(self.artifact_file)

    def tearDown(self):
        self.ensure_obj_absent(self._test_copy)
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    @unittest.skip("not implemented")
    def test_cyverselogic_called(self):
        """Test that the cyverse_logic version of the rule is called"""

    def test_cyversetrash_called(self):
        """Test that the cyverse_trash version of the rule is called"""
        self.irods.data_objects.copy(self.artifact_file, self._test_copy)
        if not self.verify_msg_logged("cyverse_trash_api_data_obj_copy_post"):
            self.fail("cyverse_trash_api_data_obj_copy_post not called")


class PepApiDataObjCopyPreTest(CyverseCoreTestCase):
    """Test pep_api_data_obj_copy_pre"""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_copy = "/testing/home/rods/test_copy"

    def setUp(self):
        super().setUp()
        self.ensure_obj_absent(self._test_copy)
        self.irods.data_objects.create(self.artifact_file)

    def tearDown(self):
        self.ensure_obj_absent(self._test_copy)
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    def test_cyverseencryption_called(self):
        """Test that the cyverse_encryption version of the rule is called"""
        self.irods.data_objects.copy(self.artifact_file, self._test_copy)
        if not self.verify_msg_logged("cyverse_encryption_api_data_obj_copy_pre"):
            self.fail("cyverse_encryption_api_data_obj_copy_pre not called")


class PepApiDataObjCreatePostTest(CyverseCoreTestCase):
    """Test pep_api_data_obj_create_post"""

    def setUp(self):
        super().setUp()
        self.irods.data_objects.create(self.artifact_file)

    def tearDown(self):
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    @unittest.skip("not implemented")
    def test_cyverselogic_called(self):
        """Test that the rule is called."""

    def test_cyversetrash_called(self):
        """Test that the rule is called."""
        if not self.verify_msg_logged("cyverse_trash_api_data_obj_create_post"):
            self.fail("cyverse_trash_api_data_obj_create_post not called")


class PepApiDataObjCreatePreTest(CyverseCoreTestCase):
    """Test pep_api_data_obj_create_pre"""

    def setUp(self):
        super().setUp()
        self.irods.data_objects.create(self.artifact_file)

    def tearDown(self):
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    def test_cyverseencryption_called(self):
        """Test that the rule is called."""
        if not self.verify_msg_logged("cyverse_encryption_api_data_obj_create_pre"):
            self.fail("cyverse_encryption_api_data_obj_create_pre not called")


class PepApiDataObjCreateAndStatPreTest(CyverseCoreTestCase):
    """
    Test pep_api_data_obj_create_and_stat_pre.

    NOTE: As of iRODS 4.3.3, this PEP is not currently called by any iRODS client.
    """

    def test_cyverseencryption_called(self):
        """Test that cyverse_encryption's version of this rule"""
        self.exec_rule(
            self.mk_rule("pep_api_data_obj_create_and_stat_pre('', '', '', '')"),
            IrodsType.NONE,
        )
        if not self.verify_msg_logged("pep_api_data_obj_create_and_stat_pre"):
            self.fail("pep_api_data_obj_create_and_stat_pre call not logged")


class PepApiDataObjOpenPreTest(CyverseCoreTestCase):
    """Test pep_api_data_obj_open_pre"""

    def setUp(self):
        super().setUp()
        self.irods.data_objects.create(self.artifact_file)

    def tearDown(self):
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    def test_cyverseencryption_called(self):
        """Test that the rule is called."""
        with self.irods.data_objects.open(self.artifact_file, mode="r", create=False):
            if not self.verify_msg_logged("cyverse_encryption_api_data_obj_create_pre"):
                self.fail("ipcEncryption_api_data_obj_open_pre not called")


class PepApiDataObjOpenAndStatPreTest(CyverseCoreTestCase):
    """
    Test pep_api_data_obj_open_and_stat_pre"

    NOTE: As of iRODS 4.3.3, this PEP is not currently called by any iRODS client.
    """

    def test_cyverseencryption_called(self):
        """Test that cyverse_encryption's version of this rule"""
        self.exec_rule(
            self.mk_rule("pep_api_data_obj_open_and_stat_pre('', '', '', '')"),
            IrodsType.NONE,
        )
        if not self.verify_msg_logged("pep_api_data_obj_open_and_stat_pre"):
            self.fail("pep_api_data_obj_open_and_stat_pre call not logged")


class PepApiDataObjPutTest(CyverseCoreTestCase):
    """Tests pep_api_data_obj_put_*"""

    def setUp(self):
        super().setUp()
        if not self.put_empty(self.artifact_file):
            raise RuntimeError(f"Failed to upload {self.artifact_file}")

    def tearDown(self):
        self.ensure_obj_absent(self.artifact_file)
        super().tearDown()

    def test_cyverseencryption_called(self):
        """Test that the rule is called."""
        if not self.verify_msg_logged("cyverse_encryption_api_data_obj_put_pre"):
            self.fail("cyverse_encryption_api_data_obj_put_pre not called")

    @unittest.skip("not implemented")
    def test_cyverselogic_called(self):
        """Test that cyverse_logic's version of this rule is called."""

    def test_cyversetrash_called(self):
        """Test that cyverse_trash's version of this rule is called."""
        if not self.verify_msg_logged("cyverse_trash_api_data_obj_put_post"):
            self.fail("cyverse_trash_api_data_obj_put_post not called")


class PepApiDataObjRenameTest(CyverseCoreTestCase):
    """Test pep_api_data_obj_rename_pre"""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._test_rename = "/testing/home/rods/test_rename"

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
            self.fail("cyverse_encryption_api_data_obj_rename_post not called")

    def test_cyverseencryption_pre_called(self):
        """Test that the cyverse_encryption logic attached to this pre PEP is called"""
        if not self.verify_msg_logged("cyverse_encryption_api_data_obj_rename_pre"):
            self.fail("cyverse_encryption_api_data_obj_rename_pre not called")

    def test_cyversetrash_post_called(self):
        """Test that the cyverse_trash logic attached to the post PEP is called"""
        if not self.verify_msg_logged("cyverse_trash_api_data_obj_rename_post"):
            self.fail("cyverse_trash_api_data_obj_rename_post not called")

    def test_cyversetrash_pre_called(self):
        """Test that the cyverse_trash logic attached to the pre PEP is called"""
        if not self.verify_msg_logged("cyverse_trash_api_data_obj_rename_pre"):
            self.fail("cyverse_trash_api_data_obj_rename_pre not called")


class PepApiDataObjUnlinkTest(CyverseCoreTestCase):
    """Tests of pep_api_data_obj_unlink PEPs"""

    def setUp(self):
        super().setUp()
        self._data = "/testing/home/rods/file"
        self.irods.data_objects.create(self._data)

    def tearDown(self):
        self.ensure_obj_absent("/testing/trash/home/rods/file")
        self.ensure_obj_absent(self._data)

    def test_cyversetrash_except_called(self):
        """Test that the cyverse_trash logic attached to the except version of this PEP is called"""
        no_unlink = "/testing/home/rods/no-unlink"
        try:
            self.irods.data_objects.create(no_unlink)
            self.irods.data_objects.unlink(no_unlink)
        except FAIL_ACTION_ENCOUNTERED_ERR:
            pass
        if not self.verify_msg_logged("cyverse_trash_api_data_obj_unlink_except"):
            self.fail("cyverse_trash_api_data_obj_unlink_except not called")
        self.ensure_obj_absent(no_unlink)

    def test_cyversetrash_post_called(self):
        """Test that the cyverse_trash logic attached to the post version of this  PEP is called"""
        self.irods.data_objects.unlink(self._data)
        if not self.verify_msg_logged("cyverse_trash_api_data_obj_unlink_post"):
            self.fail("cyverse_trash_api_data_obj_unlink_post not called")

    def test_cyversetrash_pre_called(self):
        """Test that the cyverse_trash logic attached to the pre version of this  PEP is called"""
        self.irods.data_objects.unlink(self._data)
        if not self.verify_msg_logged("cyverse_trash_api_data_obj_unlink_pre"):
            self.fail("cyverse_trash_api_data_obj_unlink_pre not called")


class PepApiRmCollTest(CyverseCoreTestCase):
    """Tests of pep_api_rm_coll PEPs"""

    def setUp(self):
        super().setUp()
        try:
            self.irods.collections.remove(f"/{self.irods.zone}/missing")
        except CAT_NO_ROWS_FOUND:
            pass

    def test_cyversetrash_except_called(self):
        """Test that the cyverse_trash logic attached to the except version of this PEP is called"""
        if not self.verify_msg_logged("cyverse_trash_api_rm_coll_except"):
            self.fail("cyverse_trash_api_rm_coll_except not called")

    def test_cyversetrash_pre_called(self):
        """Test that the cyverse_trash logic attached to the pre version of this PEP is called"""
        if not self.verify_msg_logged("cyverse_trash_api_rm_coll_pre"):
            self.fail("cyverse_trash_api_rm_coll_pre not called")


@test_rules.unimplemented
class PepApiStructFileExtAndRegPre(CyverseCoreTestCase):
    """Test pep_api_struct_file_ext_and_reg_pre

    XXX: This PEP is broken because of bug
    https://github.com/irods/irods/issues/7413. It is fixed in iRODS 4.3.
    """


class CyverseCorePublicTest(CyverseCoreTestCase):
    """Test the public entities cyverse_core.re rule-base"""

    @unittest.skip("not implemented")
    def test_accreatecollbyadmin(self):
        """Test acCreateCollByAdmin"""

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
    def test_pepapibulkdataobjputpost(self):
        """Test pep_api_bulk_data_obj_put_post"""

    @unittest.skip("not implemented")
    def test_pepapibulkdataobjregpost(self):
        """Test pep_api_bulk_data_obj_reg_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjclosepost(self):
        """Test pep_api_data_close_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcopypost(self):
        """Test pep_api_data_obj_copy_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcreatepost(self):
        """Test pep_api_data_obj_create_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjcreateandstatpost(self):
        """Test pep_api_data_obj_create_and_stat_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjopenandstatpost(self):
        """Test pep_api_data_obj_open_and_stat_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjopenpost(self):
        """Test pep_api_data_obj_open_post"""

    @unittest.skip("not implemented")
    def test_pepapidataobjopenandstatpre(self):
        """Test pep_api_data_obj_open_and_stat_pre"""

    @unittest.skip("not implemented")
    def test_pepapidataobjwritepost(self):
        """Test pep_api_data_obj_write_post"""

    @unittest.skip("not implemented")
    def test_pepapiphypathregpost(self):
        """Test pep_api_phy_path_reg_post"""

    @unittest.skip("not implemented")
    def test_pepapireplicaclosepost(self):
        """Test pep_api_replica_close_post"""

    @unittest.skip("not implemented")
    def test_pepapireplicaopenpost(self):
        """Test pep_api_replica_open_post"""

    @unittest.skip("not implemented")
    def test_pepapirmcollpre(self):
        """Test pep_api_rm_coll_pre"""

    @unittest.skip("not implemented")
    def test_pepapitouchpost(self):
        """Test pep_api_touch_post"""

    @unittest.skip("not implemented")
    def test_pepdatabaseclosepost(self):
        """Test pep_database_close_post"""

    @unittest.skip("not implemented")
    def test_pepdatabaseclosefinally(self):
        """Test pep_database_close_finally"""

    @unittest.skip("not implemented")
    def test_pepdatabasemoddataobjmetapost(self):
        """Test pep_database_mod_data_obj_meta_post"""

    @unittest.skip("not implemented")
    def test_pepdatabaseregdataobjpost(self):
        """Test pep_database_reg_data_obj_post"""

    @unittest.skip("not implemented")
    def test_pepresourceresolvehierarchypre(self):
        """Test pep_resource_resolve_hierarchy_pre"""


if __name__ == "__main__":
    unittest.main()
