#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cve.re rule logic."""

import subprocess
from subprocess import PIPE
from tempfile import NamedTemporaryFile
import unittest

import test_rules
from test_rules import IrodsTestCase, IrodsType, IrodsVal

from irods.exception import CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME


_TEST_DATA = "/testing/home/rods/test_data"


class MsisendmailTest(IrodsTestCase):
    """Test the rule msiSendMail"""

    def test_log_msg(self):
        """
        Verify that an intercept message is logged when attempt is made to call the msiSendMail
        microservice.
        """
        rule = self.mk_rule("msiSendMail('', '', '')")
        self.exec_rule(rule, IrodsType.NONE)
        if 'intercepted msiSendMail call' not in self.tail_rods_log(1)[0]:
            self.fail()


class MsiservermonperfTest(IrodsTestCase):
    """Test the rule msiServerMonPerf"""

    def test_log_msg(self):
        """
        Verify that an intercept message is logged when an attempt is made to call msiServerMonPerf
        microservice
        """
        rule = self.mk_rule("msiServerMonPerf('', '')")
        self.exec_rule(rule, IrodsType.NONE)
        if 'intercepted msiServerMonPerf call' not in self.tail_rods_log(1)[0]:
            self.fail()


class PepApiDataObjCopyPreTestP(IrodsTestCase):
    """Test pep_api_data_obj_copy_pre with -p option"""

    @classmethod
    def setUpClass(cls):
        test_rules.clear_rods_log()

    def setUp(self):
        super().setUp()
        try:
            self.irods.data_objects.create(_TEST_DATA)
        except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            pass
        self._copy_data_path = "/testing/home/rods/test_data_copy"
        self.ensure_obj_absent(self._copy_data_path)
        self.update_rulebase('cyverse_core.re', 'mocks/cyverse_core.re')
        _, _, stderr = self.ssh.exec_command(
            f'sudo --login --user=irods'
            f' icp -p /var/lib/irods/test_data {_TEST_DATA} {self._copy_data_path}')
        self._icp_exit_status = stderr.channel.recv_exit_status()

    def tearDown(self):
        self.update_rulebase('cyverse_core.re', '../cyverse_core.re')
        self.ensure_obj_absent(self._copy_data_path)
        self.ensure_obj_absent(_TEST_DATA)
        super().tearDown()

    def test_no_copy(self):
        """Verify that no copy was made"""
        if self.irods.data_objects.exists(self._copy_data_path):
            self.fail("The file was copied when it shouldn't have been")

    def test_copy_failed(self):
        """Verify that a copy command failed"""
        if self._icp_exit_status == 0:
            self.fail("copy succeeded instead of failed")

    def test_cyversecore_not_called(self):
        """Verify that the cyverse-core.re version of the PEP is not called"""
        for line in self.tail_rods_log():
            if 'cyverse_core: pep_api_data_obj_copy_pre' in line:
                self.fail('cyverse_core version called')


class PepApiDataObjCopyPreTestNoP(IrodsTestCase):
    """Test pep_api_data_obj_copy_pre without -p option"""

    @classmethod
    def setUpClass(cls):
        test_rules.clear_rods_log()

    def setUp(self):
        super().setUp()
        try:
            self.irods.data_objects.create(_TEST_DATA)
        except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            pass
        self._copy_data_path = "/testing/home/rods/test_data_copy"
        self.ensure_obj_absent(self._copy_data_path)
        self.update_rulebase('cyverse_core.re', 'mocks/cyverse_core.re')
        _, _, stderr = self.ssh.exec_command(
            f'sudo --login --user=irods icp {_TEST_DATA} {self._copy_data_path}')
        self._icp_exit_status = stderr.channel.recv_exit_status()

    def tearDown(self):
        self.update_rulebase('cyverse_core.re', '../cyverse_core.re')
        self.ensure_obj_absent(self._copy_data_path)
        self.ensure_obj_absent(_TEST_DATA)
        super().tearDown()

    def test_copy_made(self):
        """Verify that a copy was made"""
        if not self.irods.data_objects.exists(self._copy_data_path):
            self.fail("The file wasn't copied")

    def test_copy_succeeded(self):
        """Verify that the copy command succeeded"""
        if self._icp_exit_status != 0:
            self.fail("copy failed")

    def test_cyversecore_called(self):
        """Verify that the cyverse-core.re version of the PEP is called"""
        for line in self.tail_rods_log():
            if 'cyverse_core: pep_api_data_obj_copy_pre' in line:
                return
        self.fail('cyverse_core version not called')


class PepApiDataObjPutPreTestP(IrodsTestCase):
    """Test pep_api_data_obj_put_pre with -p option"""

    @classmethod
    def setUpClass(cls):
        test_rules.clear_rods_log()

    def setUp(self):
        super().setUp()
        self.update_rulebase('cyverse_core.re', 'mocks/cyverse_core.re')
        self._file = NamedTemporaryFile(delete=False)
        self._file.close()
        iput = f"""
            echo '{test_rules.IRODS_PASSWORD}' \
                | iput -p /var/lib/irods/tmp_file '{self._file.name}' '{_TEST_DATA}'
        """
        self._iput_resp = subprocess.run(
            iput,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            check=False,
            encoding='utf-8')

    def tearDown(self):
        self.update_rulebase('cyverse_core.re', '../cyverse_core.re')
        super().tearDown()

    def test_no_upload(self):
        """Verify that no upload happened"""
        if self.irods.data_objects.exists(_TEST_DATA):
            self.fail("The file was uploaded when it shouldn't have been")

    def test_upload_failed(self):
        """Verify that the upload command failed"""
        if self._iput_resp.returncode == 0:
            self.fail("upload succeeded instead of failed")

    def test_cyversecore_not_called(self):
        """Verify that the cyverse-core.re version of the PEP is not called"""
        for line in self.tail_rods_log():
            if 'cyverse_core: pep_api_data_obj_put_pre' in line:
                self.fail('cyverse_core version called')


class PepApiDataObjPutPreTestNoP(IrodsTestCase):
    """Test pep_api_data_obj_put_pre without -p option"""

    @classmethod
    def setUpClass(cls):
        test_rules.clear_rods_log()

    def setUp(self):
        super().setUp()
        self.update_rulebase('cyverse_core.re', 'mocks/cyverse_core.re')
        self._file = NamedTemporaryFile(delete=False)
        self._file.close()
        self._iput_resp = subprocess.run(
            f"echo '{test_rules.IRODS_PASSWORD}' | iput '{self._file.name}' '{_TEST_DATA}'",
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            check=False,
            encoding='utf-8')

    def tearDown(self):
        self.update_rulebase('cyverse_core.re', '../cyverse_core.re')
        self.ensure_obj_absent(_TEST_DATA)
        super().tearDown()

    def test_upload_exists(self):
        """Verify that no upload happened"""
        if not self.irods.data_objects.exists(_TEST_DATA):
            self.fail("The file wasn't uploaded")

    def test_upload_succeeded(self):
        """Verify that a upload command succeeded"""
        if self._iput_resp.returncode != 0:
            self.fail("upload failed")

    def test_cyversecore_called(self):
        """Verify that the cyverse-core.re version of the PEP is called"""
        for line in self.tail_rods_log():
            if 'cyverse_core: pep_api_data_obj_put_pre' in line:
                return
        self.fail("cyverse_core version wasn't called")


class TestDelVal(IrodsTestCase):
    """Test _cve_DEL_VAL"""

    def test(self):
        """Verify that that is is the delete value"""
        self.fn_test('_cve_DEL_VAL', [], IrodsVal.integer(1130))


@test_rules.unimplemented
class TestDeleteForbidden(IrodsTestCase):
    """Test _cve_delete_forbidden"""


@test_rules.unimplemented
class TestPepApiDataObjUnlinkPre(IrodsTestCase):
    """Test pep_api_data_obj_unlink_pre"""


if __name__ == "__main__":
    unittest.main()
