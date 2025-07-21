#!/usr/bin/env python  # pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of ipc-repl.re rule logic."""

import unittest

from test_rules import IrodsTestCase


class TestReplReplicate(IrodsTestCase):
    """Tests of _repl_replicate"""

    @unittest.skip("not implemented")
    def test_object_exists(self):
        """Tests its handling of a object that still exists"""

    @unittest.skip("not implemented")
    def test_object_gone(self):
        """Tests its handling of an object that not longer exists"""


class TestIpcRepl(IrodsTestCase):
    """Test ipc-repl.re"""

    @unittest.skip("Not implemented")
    def test_mvreplicas(self):
        """Test _repl_mvReplicas logic"""

    @unittest.skip("Not implemented")
    def test_syncreplicas(self):
        """Test _repl_syncReplicas logic"""

    @unittest.skip("Not implemented")
    def test_supporting(self):
        """Test supporting function and rule logic"""

    @unittest.skip("Not implemented")
    def test_public(self):
        """Test the public rule logic"""


if __name__ == "__main__":
    unittest.main()
