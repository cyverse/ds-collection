#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of coge.re rule logic."""

from os import path
import unittest

from test_rules import IrodsTestCase

from irods.exception import CAT_SQL_ERR, CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME
from irods.models import Collection, CollectionAccess, CollectionUser, DataAccess, DataObject, User


class CogeTestCase(IrodsTestCase):
    """Base class for coge.re rule tests."""

    def setUp(self):
        """Create coge user and coge_data collection."""
        super().setUp()
        self._coge_user = "coge"
        self._coge_coll_path = "/testing/home/rods/coge_data"
        try:
            self.irods.users.create(self._coge_user, "rodsuser")
        except CAT_SQL_ERR as e:
            if not str(e).endswith('CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME'):
                raise e
        except CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            pass
        self.irods.collections.create(self._coge_coll_path)

    def tearDown(self):
        """Remove coge user and coge_data collection."""
        self.ensure_coll_absent(self._coge_coll_path)
        self.irods.users.remove(self._coge_user)
        super().tearDown()

    @property
    def coge_coll_path(self) -> str:
        """The absolute path to the CoGe data directory"""
        return self._coge_coll_path

    @property
    def coge_user(self) -> str:
        """The CoGe username"""
        return self._coge_user


class TestCogeAcpostprocforcollcreate(CogeTestCase):
    """Test the rule coge_acPostProcForCollCreate."""

    def test_coge_access(self):
        """Verify coge is given access to newly created coge_data collection."""
        q = self.irods.query(CollectionAccess.name)
        q = q.filter(Collection.name == self.coge_coll_path, CollectionUser.name == self._coge_user)
        for res in q:
            return self.assertEqual(res[CollectionAccess.name], "modify_object")
        return self.fail()


class TestCogeAcpostprocforobjrename(CogeTestCase):
    """Test the rule coge_acPostProcForObjRename."""

    def setUp(self):
        """Create a data object outside of coge_data and move it inside."""
        super().setUp()
        self._data_name = "test_data"
        self._orig_data_path = path.join("/testing/home/rods", self._data_name)
        self._new_data_path = path.join(self.coge_coll_path, self._data_name)
        self.irods.data_objects.create(self._orig_data_path)
        self.irods.data_objects.move(self._orig_data_path, self._new_data_path)

    def tearDown(self):
        """Remove the test data object."""
        self.ensure_obj_absent(self._new_data_path)
        self.ensure_obj_absent(self._orig_data_path)
        super().tearDown()

    def test_coge_access(self):
        """Verify the rule gives coge access to the entity after it is renamed"""
        q = self.irods.query(DataAccess.name)
        q.filter(
            Collection.name == self.coge_coll_path,
            DataObject.name == self._data_name,
            User.name == self.coge_user)
        for res in q:
            return self.assertEqual(res[DataAccess.name], "modify_object")
        return self.fail()


class TestCogeDataobjcreated(CogeTestCase):
    """Test the rule coge_dataObjCreated."""

    def setUp(self):
        """Create a data object inside of coge_data."""
        super().setUp()
        self._data_name = "test_data"
        self._data_path = path.join(self.coge_coll_path, self._data_name)
        self.irods.data_objects.create(self._data_path)

    def tearDown(self):
        """Remove the test data object."""
        self.ensure_obj_absent(self._data_path)
        super().tearDown()

    def test_coge_access(self):
        """Verify the rule gives coge access to the data object after it is created"""
        q = self.irods.query(DataAccess.name)
        q.filter(
            Collection.name == self.coge_coll_path,
            DataObject.name == self._data_name,
            User.name == self.coge_user)
        for res in q:
            return self.assertEqual(res[DataAccess.name], "modify_object")
        return self.fail()


if __name__ == "__main__":
    unittest.main()
