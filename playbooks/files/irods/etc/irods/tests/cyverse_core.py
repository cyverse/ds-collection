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


if __name__ == "__main__":
    unittest.main()
