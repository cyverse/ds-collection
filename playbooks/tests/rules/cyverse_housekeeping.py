#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_housekeeping.re rule logic"""

import unittest

from irods.models import RuleExec

from test_rules import IrodsTestCase, IrodsType


class TestScheduleperiodicpolicy(IrodsTestCase):
    """Tests of _cyverse_housekeeping_schedulePeriodicPolicy"""

    def __init__(self, method_name: str):
        super().__init__(method_name)
        self._deferred_rule = "writeLine('serverLog', 'periodic rule executed')"
        self._rule = None

    def setUp(self):
        super().setUp()
        rule_src = f"""
            _cyverse_housekeeping_schedulePeriodicPolicy(
                ``{self._deferred_rule}``, '1h', 'description' );
        """
        self._rule = self.mk_rule(rule_src)
        self.exec_rule(self._rule, IrodsType.NONE)

    def tearDown(self):
        if self._rule:
            for res in self.irods.query(RuleExec.id).filter(RuleExec.name == self._deferred_rule):
                self._rule.remove_by_id(res[RuleExec.id])
        super().tearDown()

    def test_desc(self):
        """Verify that it logs the correct description"""
        for line in self.tail_rods_log():
            if 'scheduling description' in line:
                return
        self.fail("description not logged")

    def test_freq(self):
        """Test that it sets the execution frequency"""
        q = self.irods.query(RuleExec.frequency).filter(RuleExec.name == self._deferred_rule)
        self.assertEqual(
            q.one()[RuleExec.frequency], '1h', "the rule frequency not scheduled properly")

    def test_rule(self):
        """Test that it schedules the rule"""
        res = self.irods.query(RuleExec.id).filter(RuleExec.name == self._deferred_rule).execute()
        self.assertEqual(len(res), 1, "the rule wasn't scheduled properly")


class TestSharedRules(IrodsTestCase):
    """Tests of the shared rule logic"""

    @unittest.skip("not implemented")
    def test_cyversehousekeepingrecheduleperiodicpolicy(self):
        """Test _cyverse_housekeeping_reschedulePeriodicPolicy"""


class TestCyverseHousekeeping(IrodsTestCase):
    """Tests of cyverse_housekeeping.re"""

    @unittest.skip("not implemented")
    def test_quotas(self):
        """Test quota logic"""

    @unittest.skip("not implemented")
    def test_storage_free_space(self):
        """Test storage free space logic"""

    @unittest.skip("not implemented")
    def test_trash_removal(self):
        """Test trash removal logic"""


if __name__ == "__main__":
    unittest.main()
