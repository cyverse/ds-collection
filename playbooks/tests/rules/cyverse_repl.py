#!/usr/bin/env python  # pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_repl.re rule logic."""

import subprocess
import unittest

from irods.models import RuleExec

import test_rules
from test_rules import IrodsTestCase, IrodsType


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class TestReplReplicate(IrodsTestCase):
    """Tests of _repl_replicate"""

    @unittest.skip("not implemented")
    def test_object_exists(self):
        """Tests its handling of a object that still exists"""

    @unittest.skip("not implemented")
    def test_object_gone(self):
        """Tests its handling of an object that not longer exists"""


class TestAcsetrescschemeforcreate(IrodsTestCase):
    """Test cyverse_repl_acSetRescSchemeForCreate"""

    def test_default_resc(self):
        """Verify that the default resource is chosen correctly"""
        objPath = "/testing/home/rods/obj"
        obj = self.irods.data_objects.create(objPath)
        if obj.replicas[0].resource_name != "ingestRes":
            self.fail("cyverse_repl_acSetRescSchemeForCreate failed to set default resource")
        obj.unlink(force=True)

    def test_nondefault_resc(self):
        """Verify that a configured resource is chosen correctly"""
        objPath = "/testing/home/shared/avra/obj"
        obj = self.irods.data_objects.create(objPath)
        if obj.replicas[0].resource_name != "avra":
            self.fail("cyverse_repl_acSetRescSchemeForCreate failed to set nondefault resource")
        obj.unlink(force=True)


class TestAcsetrescschemeforrepl(IrodsTestCase):
    """Tests of cyverse_repl_acSetRescSchemeForRepl"""

    def test_repl_replicate_not_set_custom_resc(self):
        """
        Test that it behaves correctly when temporaryStorage.repl_replicate is not set and a custom
        replication resource is to be used.
        """
        self.irods.resources.get("avraRes").metadata.set("ipc::replica-resource", "pire")
        obj = self.irods.data_objects.create("/testing/home/shared/avra/obj")
        obj.replicate()
        obj = self.irods.data_objects.get("/testing/home/shared/avra/obj")
        if obj.replicas[1].resource_name != "pire":
            self.fail("Failed to replicate to custom resource")
        obj.unlink(force=True)
        self.irods.resources.get("avraRes").metadata.remove("ipc::replica-resource", "pire")

    def test_repl_replicate_not_set_default_resc(self):
        """
        Test that it behaves correctly when temporaryStorage.repl_replicate is not set and the
        default resource is to be used.
        """
        obj = self.irods.data_objects.create("/testing/home/rods/obj")
        obj.replicate()
        obj = self.irods.data_objects.get("/testing/home/rods/obj")
        if obj.replicas[1].resource_name != "replRes":
            self.fail("Failed to replicate to default resource")
        obj.unlink(force=True)


class TestDataobjcreated(IrodsTestCase):
    """Tests of cyverse_repl_dataObjCreated"""

    def test(self):
        """Verify that a replication rule is scheduled when a data object is created"""
        obj = self.irods.data_objects.create('/testing/home/rods/obj')
        rule = """
            *doi.logical_path = "/testing/home/rods/obj";
            *doi.resc_hier = "ingestRes";
            cyverse_repl_dataObjCreated("rods", "testing", *doi);
        """
        self.exec_rule(self.mk_rule(rule), IrodsType.NONE)
        ruleFound = False
        for result in self.irods.query(RuleExec.name):
            if result[RuleExec.name].find('_repl_replicate_workaround') != -1:
                ruleFound = True
                break
        if not ruleFound:
            self.fail(
                "cyverse_repl_dataObjCreated did not schedule the _repl_replicate_workaround rule")
        obj.unlink(force=True)


class TestDataobjmodified(IrodsTestCase):
    """Tests of cyverse_repl_dataObjModified"""

    def __init__(self, method: str):
        super().__init__(method)
        self._objPath = "/testing/home/rods/obj"

    def setUp(self):
        super().setUp()
        obj = self.irods.data_objects.create(self._objPath)
        obj.replicate()
        cmd = (
            f"echo '{test_rules.IRODS_PASSWORD}'"
            f" | iadmin modrepl logical_path {self._objPath} replica_number 1 DATA_REPL_STATUS 0")
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=True,
            encoding='utf-8')
        rule = f"""
            *doi.logical_path = "{self._objPath}";
            *doi.resc_hier = "ingestRes";
            cyverse_repl_dataObjModified("rods", "testing", *doi);
        """
        self.exec_rule(self.mk_rule(rule), IrodsType.NONE)

    def tearDown(self):
        self.irods.data_objects.unlink(self._objPath, force=True)
        super().tearDown()

    def test(self):
        """Verify that the replica of a file is updated when the original is updated"""
        ruleFound = False
        for result in self.irods.query(RuleExec.name):
            if result[RuleExec.name].find('_repl_syncReplicas_workaround') != -1:
                ruleFound = True
                break
        if not ruleFound:
            self.fail(
                "cyverse_repl_dataObjModified did not schedule the _repl_syncReplicas_workaround"
                " rule")


class TestPepResourceResolveHierarchyPre(IrodsTestCase):
    """Tests of pep_resource_resolve_hierarchy_pre"""

    def setUp(self):
        super().setUp()
        self.ensure_obj_absent('/testing/home/rods/obj')
        self.update_rulebase([('cyverse_core.re', 'mocks/cyverse_core.re')])

    def tearDown(self):
        self.update_rulebase([('cyverse_core.re', '../../files/irods/etc/irods/cyverse_core.re')])
        self.ensure_obj_absent('/testing/home/rods/obj')
        super().tearDown()

    def test_replreplicate_not_set(self):
        """Verify that default logic happens when temporaryStorage.repl_replicate isn't set"""
        self.irods.data_objects.create('/testing/home/rods/obj')
        for line in self.tail_rods_log():
            if 'cyverse_core: pep_resource_resolve_hierarchy_pre' in line:
                return
        self.fail('intercepted PEP')

    def test_replreplicate_set_to_empty(self):
        """Test logic when temporaryStorage.repl_replicate is set to empty"""
        rule_text = """
            temporaryStorage.repl_replicate = '';
            msiDataObjCreate('/testing/home/rods/obj', '', *out);
        """
        self.exec_rule(self.mk_rule(rule_text), IrodsType.NONE)
        for line in self.tail_rods_log():
            if 'cyverse_core: pep_resource_resolve_hierarchy_pre' in line:
                return
        self.fail('intercepted PEP')

    def test_replreplicate_set_to_replforcedreplresc(self):
        """Test logic when temporaryStorage.repl_replicate is set to 'REPL_FORCED_REPL_RESC'"""
        rule_text = """
            temporaryStorage.repl_replicate = 'REPL_FORCED_REPL_RESC';
            msiDataObjCreate('/testing/home/rods/obj', '', *out);
        """
        test_rules.clear_rods_log()
        self.exec_rule(self.mk_rule(rule_text), IrodsType.NONE)
        for line in self.tail_rods_log():
            if 'cyverse_core: pep_resource_resolve_hierarchy_pre' in line:
                self.fail('did not intercept PEP')
                break


class TestCyverseRepl(IrodsTestCase):
    """Test cyverse_repl.re"""

    @unittest.skip("Not implemented")
    def test_mvreplicas(self):
        """Test _repl_mvReplicas logic"""

    @unittest.skip("Not implemented")
    def test_syncreplicas(self):
        """Test _repl_syncReplicas logic"""

    @unittest.skip("Not implemented")
    def test_supporting(self):
        """Test supporting function and rule logic"""


if __name__ == "__main__":
    unittest.main()
