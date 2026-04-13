#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_housekeeping.re rule logic"""

import unittest

from irods.models import RuleExec

from test_rules import IrodsTestCase, IrodsType


class TestCyverseHousekeeping(IrodsTestCase):
    """Tests of cyverse_housekeeping.re"""

    def test_cyversehousekeepingscheduleperiodicpolicy_rule(self):
        """Test _cyverse_housekeeping_schedulePeriodicPolicy"""
        rule_src = """
            _cyverse_housekeeping_schedulePeriodicPolicy(
                ``writeLine('serverLog', 'periodic rule executed')``, '1h', 'description' );
        """
        rule = self.mk_rule(rule_src)
        self.exec_rule(rule, IrodsType.NONE)
        q = self.irods.query(RuleExec.id)
        q = q.filter(RuleExec.name == "writeLine('serverLog', 'periodic rule executed')")
        results = q.execute()
        self.assertEqual(len(results), 1, "the rule wasn't scheduled properly")
        for res in results:
            rule.remove_by_id(res[RuleExec.id])

    @unittest.skip("not implemented")
    def test_cyversehousekeepingscheduleperiodicpolicy_freq(self):
        """Test _cyverse_housekeeping_schedulePeriodicPolicy sets the execution frequency"""

    @unittest.skip("not implemented")
    def test_cyversehousekeepingrecheduleperiodicpolicy(self):
        """Test _cyverse_housekeeping_reschedulePeriodicPolicy"""

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
