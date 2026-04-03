#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_json.re rule logic."""

import unittest

import test_rules
from test_rules import IrodsTestCase, IrodsVal


def setUpModule():  # pylint: disable=invalid-name
    """Set up the module."""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down the module."""
    test_rules.tearDownModule()


class CyverseJsonListTest(IrodsTestCase):
    """Test the list functions in cyverse_json.re"""

    def test_revaccum_empty(self):
        """test _cyverse_json_revAccum with empty list"""
        rev_acc = IrodsVal.string_list(["hi"])
        self.fn_test("_cyverse_json_revAccum", [rev_acc, IrodsVal.string_list([])], rev_acc)

    def test_revaccum_one_empty_rev(self):
        """
        test _cyverse_json_revAccum with list containing one item and an empty
        reverse list
        """
        item = IrodsVal.string_list(["hi"])
        self.fn_test("_cyverse_json_revAccum", [IrodsVal.string_list([]), item], item)

    def test_revaccum_one_nonempty_rev(self):
        """
        test _cyverse_json_revAccum with list containing one item and a
        non-empty reverse list
        """
        self.fn_test(
            "_cyverse_json_revAccum",
            [IrodsVal.string_list(["1"]), IrodsVal.string_list(["2"])],
            IrodsVal.string_list(["2", "1"]))

    def test_rev(self):
        """test the _cyverse_json_rev"""
        self.fn_test(
            "_cyverse_json_rev",
            [IrodsVal.string_list(["a", "b"])],
            IrodsVal.string_list(["b", "a"]))


class CyverseJsonStringTest(IrodsTestCase):
    """Test the string functions in cyverse_json.re"""

    @unittest.skip("not implemented")
    def test_substrrem_valid(self):
        """test the _cyverse_json_substrRem"""

    @unittest.skip("not implemented")
    def test_strhd(self):
        """test the _cyverse_json_strHd"""

    @unittest.skip("not implemented")
    def test_strtl(self):
        """test the _cyverse_json_strTl"""

    @unittest.skip("not implemented")
    def test_trimleadingspace(self):
        """test the _cyverse_json_trimLeadingSpace"""

    @unittest.skip("not implemented")
    def test_append(self):
        """test the _cyverse_json_append"""

    @unittest.skip("not implemented")
    def test_join(self):
        """test the _cyverse_json_join"""


@test_rules.unimplemented
class CyverseJsonEncodingTest(IrodsTestCase):
    """Test JSON string encoding logic in cyverse_json.re"""


@test_rules.unimplemented
class CyverseJsonVal(IrodsTestCase):
    """Test cyverse_json_val logic"""

    @unittest.skip("not implemented")
    def test_isempty(self):
        """test the _cyverse_json_isEmpty"""

    @unittest.skip("not implemented")
    def test_serializescalarsaccum(self):
        """test the _cyverse_json_serializeScalarsAccum"""

    @unittest.skip("not implemented")
    def test_serializefieldsaccum(self):
        """test the _cyverse_json_serializeFieldsAccum"""

    @unittest.skip("not implemented")
    def test_serializefields(self):
        """test the _cyverse_json_serializeFields"""

    @unittest.skip("not implemented")
    def test_public_logic(self):
        """test the public logic"""


@test_rules.unimplemented
class CyverseJsonDeserializeRes(IrodsTestCase):
    """Tests of cyverse_json_deserialize_res logic"""

    @unittest.skip("not implemented")
    def test_deserializevalue(self):
        """test the _cyverse_json_deserializeValue"""

    @unittest.skip("not implemented")
    def test_deserializearray(self):
        """test the _cyverse_json_deserializeArray"""

    @unittest.skip("not implemented")
    def test_deserializearrayaccum(self):
        """test the _cyverse_json_deserializeArrayAccum"""

    @unittest.skip("not implemented")
    def test_deserializeboolean(self):
        """test the _cyverse_json_deserializeBoolean"""

    @unittest.skip("not implemented")
    def test_deserializenull(self):
        """test the _cyverse_json_deserializeNull"""

    @unittest.skip("not implemented")
    def test_deserializenumber(self):
        """test the _cyverse_json_deserializeNumber"""

    @unittest.skip("not implemented")
    def test_extractdigits(self):
        """test the _cyverse_json_extractDigits"""

    @unittest.skip("not implemented")
    def test_deserializeobject(self):
        """test the _cyverse_json_deserializeObject"""

    @unittest.skip("not implemented")
    def test_deserializeobjectaccum(self):
        """test the _cyverse_json_deserializeObjectAccum"""

    @unittest.skip("not implemented")
    def test_deserializefield(self):
        """test the _cyverse_json_deserializeField"""

    @unittest.skip("not implemented")
    def test_deserializestring(self):
        """test the _cyverse_json_deserializeString"""

    @unittest.skip("not implemented")
    def test_extractstring(self):
        """test the _cyverse_json_extractString"""

    @unittest.skip("not implemented")
    def test_extractstringaccum(self):
        """test the _cyverse_json_extractStringAccum"""

    @unittest.skip("not implemented")
    def test_public(self):
        """test the public entities"""


if __name__ == "__main__":
    unittest.main()
