#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cve.re rule logic."""

import unittest

import test_rules
from test_rules import IrodsTestCase, IrodsType


class TestMsisendmail(IrodsTestCase):
    """Test the rule msiSendMail"""

    def test_log_msg(self):
        """
        Verify that an intercept message is logged when attempt is made to call the msiSendMail
        microservice.
        """
        rule = self._mk_rule("msiSendMail('root@localhost', 'test', 'SSIA')")
        self._exec_rule(rule, IrodsType.NONE)
        if 'intercepted msiSendMail call' not in self.tail_rods_log(1)[0]:
            self.fail()


# TODO: implement below


@test_rules.unimplemented
class TestMsiservermonperf(IrodsTestCase):
    """Test the rule msiServerMonPerf"""


@test_rules.unimplemented
class TestPepApiDataObjCopyPre(IrodsTestCase):
    """Test pep_api_data_obj_copy_pre"""


@test_rules.unimplemented
class TestPepApiDataObjPutPre(IrodsTestCase):
    """Test pep_api_data_obj_put_pre"""


@test_rules.unimplemented
class TestDelVal(IrodsTestCase):
    """Test _cve_DEL_VAL"""


@test_rules.unimplemented
class TestDeleteForbidden(IrodsTestCase):
    """Test _cve_delete_forbidden"""


@test_rules.unimplemented
class TestPepApiDataObjUnlinkPre(IrodsTestCase):
    """Test pep_api_data_obj_unlink_pre"""


if __name__ == "__main__":
    unittest.main()
