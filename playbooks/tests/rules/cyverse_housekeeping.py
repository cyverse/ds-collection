#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_housekeeping.re rule logic"""

import unittest

from test_rules import IrodsTestCase


class TestCyverseHousekeeping(IrodsTestCase):
    """Tests of cyverse_housekeeping.re"""

    @unittest.skip("not implemented")
    def test_cyversehousekeepingscheduleperiodicpolicy(self):
        """Test _cyverse_housekeeping_schedulePeriodicPolicy"""

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
