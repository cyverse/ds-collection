#!/usr/bin/env python  # pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_repl.re rule logic."""

import unittest

from irods.exception import SYS_INVALID_RESC_INPUT, SYS_NOT_ALLOWED
from irods.models import RuleExec
from irods.path import iRODSPath

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


class TestAcsetrescschemeforreplCustom(IrodsTestCase):
    """
    Test that it behaves correctly when temporaryStorage.repl_replicate is not
    set and a custom replication resource is to be used.
    """

    def test(self):
        """Perform test"""
        objPath = iRODSPath(self.irods.zone, "home", "shared", "avra", "obj")
        self.ensure_obj_absent(objPath)
        avra = self.irods.resources.get("avraRes")
        avra.metadata.set("ipc::replica-resource", "ingestRes")
        obj = self.irods.data_objects.create(objPath)
        try:
            obj.replicate()
            obj = self.irods.data_objects.get(objPath)
            if obj.replicas[1].resource_name != "ingestRes":
                self.fail("Failed to replicate to custom resource")
        except SYS_INVALID_RESC_INPUT as e:
            self.fail(str(e))
        finally:
            obj.unlink(force=True)
            avra.metadata.remove("ipc::replica-resource", "ingestRes")


class TestAcsetrescschemeforreplDefault(IrodsTestCase):
    """
    Test that it behaves correctly when temporaryStorage.repl_replicate is not
    set and the default resource is to be used.
    """

    def test(self):
        """Perform test"""
        obj = self.irods.data_objects.create("/testing/home/rods/obj")
        try:
            obj.replicate()
            obj = self.irods.data_objects.get("/testing/home/rods/obj")
            if obj.replicas[1].resource_name != "replRes":
                self.fail("Failed to replicate to default resource")
        except SYS_NOT_ALLOWED as e:
            self.fail(str(e))
        finally:
            obj.unlink(force=True)


class TestDataobjcreated(IrodsTestCase):
    """Tests of cyverse_repl_dataObjCreated"""

    def test(self):
        """
        Verify that a replication rule is scheduled when a data object is
        created
        """
        obj = self.irods.data_objects.create('/testing/home/rods/obj')
        rule = """
            *doi.logical_path = "/testing/home/rods/obj";
            *doi.resc_hier = "ingestRes";
            cyverse_repl_dataObjCreated("rods", "testing", *doi);
        """
        self.exec_rule(self.mk_rule(rule), IrodsType.NONE)
        ruleFound = False
        for result in self.irods.query(RuleExec.name):
            if result[RuleExec.name].find('_repl_replicate') != -1:
                ruleFound = True
                break
        if not ruleFound:
            self.fail(
                "cyverse_repl_dataObjCreated did not schedule the _repl_replicate rule")
        obj.unlink(force=True)


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
        """
        Verify that default logic happens when temporaryStorage.repl_replicate
        isn't set
        """
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
        """
        Test logic when temporaryStorage.cyverse_repl_replicate is set to
        'REPL_FORCED_REPL_RESC'
        """
        rule_text = """
            temporaryStorage.cyverse_repl_replicate = 'REPL_FORCED_REPL_RESC';
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
