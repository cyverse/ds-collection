#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse-env.re rule logic"""

import unittest

import test_rules
from test_rules import IrodsTestCase, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class CyverseEnvTest(IrodsTestCase):
    """Tests of cyverse-env.re"""

    def test_cyverseamqpexchange(self):
        """test cyverse_AMQP_EXCHANGE"""
        self.fn_test('cyverse_AMQP_EXCHANGE', [], IrodsVal.string('irods'))

    def test_cyversedefaultreplresc(self):
        """test cyverse_DEFAULT_REPL_RESC"""
        self.fn_test('cyverse_DEFAULT_REPL_RESC', [], IrodsVal.string('replRes'))

    def test_cyversedefaultresc(self):
        """test cyverse_DEFAULT_RESC"""
        self.fn_test('cyverse_DEFAULT_RESC', [], IrodsVal.string('ingestRes'))

    def test_cyverseemailfromaddr(self):
        """test cyverse_EMAIL_FROM_ADDR"""
        self.fn_test(
            'cyverse_EMAIL_FROM_ADDR',
            [],
            IrodsVal.string('irods@dstesting-provider_configured-1.dstesting_default'))

    def test_cyverseemailreportaddr(self):
        """test cyverse_EMAIL_REPORT_ADDR"""
        self.fn_test('cyverse_EMAIL_REPORT_ADDR', [], IrodsVal.string('root@localhost'))

    def test_cyverseinitrepldelay(self):
        """test cyverse_INIT_REPL_DELAY"""
        self.fn_test('cyverse_INIT_REPL_DELAY', [], IrodsVal.integer(0))

    def test_cyversemaxnumreprocs(self):
        """test cyverse_MAX_NUM_RE_PROCS"""
        self.fn_test('cyverse_MAX_NUM_RE_PROCS', [], IrodsVal.integer(4))

    def test_cyverse_rehost(self):
        """test cyverse_RE_HOST"""
        self.fn_test(
            'cyverse_RE_HOST',
            [],
            IrodsVal.string('dstesting-provider_configured-1.dstesting_default'))

    def test_cyverse_zone(self):
        """test cyverse_ZONE"""
        self.fn_test('cyverse_ZONE', [], IrodsVal.string('testing'))


if __name__ == "__main__":
    unittest.main()
