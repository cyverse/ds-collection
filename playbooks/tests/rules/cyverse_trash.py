#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_trash.re rule logic."""

from os import path
import unittest

from irods.access import iRODSAccess
from irods.exception import (
    CAT_COLLECTION_NOT_EMPTY, CAT_NO_ACCESS_PERMISSION, CUT_ACTION_PROCESSED_ERR)

import test_rules
from test_rules import IrodsTestCase


def setUpModule():  # pylint: disable=invalid-name
    """Set up the module."""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down the module."""
    test_rules.tearDownModule()


class CyverseTrashApiCollCreatePostTest(IrodsTestCase):
    """Tests of cyverse_trash_api_coll_create_post"""

    def test_coll_in_trash(self):
        """Verify that a collection created in trash gets a timestamp AVU"""
        coll = self.irods.collections.create("/testing/trash/home/rods/coll")
        if 'ipc::trash_timestamp' not in coll.metadata:  # type: ignore
            self.fail("collection did not receive trash timestamp")
        coll.remove(force=True)  # type: ignore

    def test_coll_not_in_trash(self):
        """Verify that a collection created outside of trash doesn't get a timestamp AVU"""
        coll = self.irods.collections.create("/testing/home/rods/coll")
        if 'ipc::trash_timestamp' in coll.metadata:  # type: ignore
            self.fail("collection received trash timestamp")
        coll.remove(force=True)  # type: ignore


class CyverseTrashApiDataObjCopyPostTest(IrodsTestCase):
    """Tests of cyverse_trash_api_data_obj_copy_post"""

    def test_copy_into_trash(self):
        """Verify that a data object copy in trash has a timestamp AVU"""
        obj_path = "/testing/home/rods/obj"
        copy_path = "/testing/trash/home/rods/obj"
        self.irods.data_objects.create(obj_path)
        self.irods.data_objects.copy(obj_path, copy_path)
        if 'ipc::trash_timestamp' not in self.irods.data_objects.get(copy_path).metadata:
            self.fail("copy did not receive trash timestamp")
        self.irods.data_objects.unlink(copy_path, force=True)
        self.irods.data_objects.unlink(obj_path, force=True)

    def test_copy_outside_trash(self):
        """Verify that a data object copy outside of trash has no timestamp AVU"""
        obj_path = "/testing/home/rods/obj"
        copy_path = "/testing/home/rods/copy"
        self.irods.data_objects.create(obj_path)
        self.irods.data_objects.copy(obj_path, copy_path)
        if 'ipc::trash_timestamp' in self.irods.data_objects.get(copy_path).metadata:
            self.fail("copy received trash timestamp")
        self.irods.data_objects.unlink(copy_path, force=True)
        self.irods.data_objects.unlink(obj_path, force=True)


class CyverseTrashApiDataObjCreatePostTest(IrodsTestCase):
    """Tests of cyverse_trash_api_data_obj_create_post"""

    def test_data_in_trash(self):
        """Verify that a data object created in trash has a timestamp AVU"""
        obj = self.irods.data_objects.create('/testing/trash/home/rods/obj')
        if 'ipc::trash_timestamp' not in obj.metadata:
            self.fail("data didn't receive trash timestamp")
        obj.unlink(force=True)

    def test_data_not_in_trash(self):
        """Verify that a data object created outside of trash nas no timestamp AVU"""
        obj = self.irods.data_objects.create('/testing/home/rods/obj')
        if 'ipc::trash_timestamp' in obj.metadata:
            self.fail("data received trash timestamp")
        obj.unlink(force=True)


class CyverseTrashApiDataObjPutPostTest(IrodsTestCase):
    """Tests of cyverse_trash_api_data_obj_put_post"""

    def test_data_in_trash(self):
        """Verify that data object uploaded to trash has timestamp AVU"""
        obj_path = '/testing/trash/home/rods/obj'
        self.put_empty(obj_path)
        if 'ipc::trash_timestamp' not in self.irods.data_objects.get(obj_path).metadata:
            self.fail("data didn't receive trash timestamp")
        self.irods.data_objects.unlink(obj_path, force=True)

    def test_data_not_in_trash(self):
        """Verify that data object uploaded outside of trash has timestamp AVU"""
        obj_path = '/testing/home/rods/obj'
        self.put_empty(obj_path)
        if 'ipc::trash_timestamp' in self.irods.data_objects.get(obj_path).metadata:
            self.fail("data received trash timestamp")
        self.irods.data_objects.unlink(obj_path, force=True)


class CyverseTrashApiDataObjRenameTest(IrodsTestCase):
    """Tests of cyverse_trash_api_data_obj_rename_post"""

    def test_mv_outside_trash(self):
        """
        Verify that a data object moved doesn't get a trash AVU when both the source and destination
        are outside of trash.
        """
        self._check_mv('/testing/home/rods/obj', '/testing/home/rods/mv', self._fail_if_timestamp)

    def test_mv_into_trash(self):
        """Verify that a data object moved into trash gets a timestamp AVU"""
        self._check_mv(
            '/testing/home/rods/obj', '/testing/trash/home/rods/obj', self._fail_if_no_timestamp)

    def test_mv_inside_trash(self):
        """
        Verify that a data object moved keeps its trash AVU when both the source and destination are
        inside of trash
        """
        obj = self.irods.data_objects.create('/testing/trash/home/rods/obj')
        timestamp = int(obj.metadata.get_one('ipc::trash_timestamp').value)
        timestamp = timestamp - 1
        obj.metadata.set('ipc::trash_timestamp', str(timestamp - 1), '')
        new_path = '/testing/trash/home/rods/moved'
        self.irods.data_objects.move(obj.path, new_path)
        mv_obj = self.irods.data_objects.get(new_path)
        new_timestamp = mv_obj.metadata.get_all('ipc::trash_timestamp')
        if len(new_timestamp) != 1:
            self.fail('data does not have a unique trash timestamp')
        elif int(new_timestamp[0].value) <= timestamp:
            self.fail('data timestamp not updated on move')
        mv_obj.unlink(force=True)

    def test_mv_out_of_trash(self):
        """Verify that a data object moved out of trash has its trash AVU removed"""
        self._check_mv(
            '/testing/trash/home/rods/obj', '/testing/home/rods/obj', self._fail_if_timestamp)

    def _fail_if_no_timestamp(self, obj):
        if 'ipc::trash_timestamp' not in self.irods.data_objects.get(obj).metadata:
            self.fail('data did not receive trash timestamp')

    def _fail_if_timestamp(self, obj):
        if 'ipc::trash_timestamp' in self.irods.data_objects.get(obj).metadata:
            self.fail('data received trash timestamp')

    def _check_mv(self, src, dest, test):
        self.irods.data_objects.create(src)
        self.irods.data_objects.move(src, dest)
        test(dest)
        self.irods.data_objects.unlink(dest, force=True)


class CyverseTrashApiDataObjUnlinkTest(IrodsTestCase):
    """Tests of cyverse_trash_api_data_obj_unlink PEPs"""

    def test_failed_move_to_trash(self):
        """Verify that a data object that couldn't be moved to trash doesn't get a timestamp"""
        user = 'user'
        obj = path.join('/testing/home', user, 'data')
        self.ensure_user_exists(user)
        self.irods.data_objects.create(obj)
        self.irods.acls.set(iRODSAccess('write', obj, 'rods'), admin=True)
        self.irods.acls.set(iRODSAccess('write', obj, 'rodsadmin'), admin=True)
        try:
            self.irods.data_objects.unlink(obj)
        except CUT_ACTION_PROCESSED_ERR:
            pass
        if 'ipc::trash_timestamp' in self.irods.data_objects.get(obj).metadata:
            self.fail('data that could not be moved to trash received timestamp')
        self.irods.acls.set(iRODSAccess('own', obj, 'rods'), admin=True)
        self.ensure_obj_absent(obj)
        try:
            self.irods.users.remove(user)
        except CAT_COLLECTION_NOT_EMPTY:
            home = self.irods.collections.get(path.join('/testing/home', user))
            for coll in home.subcollections:  # type: ignore
                coll.remove(force=True)
            for obj in home.data_objects:  # type: ignore
                obj.unlink(force=True)
            self.irods.users.remove(user)

    def test_successful_move_to_trash(self):
        """Verify that a data object that was moved to trash gets a timestamp"""
        self.irods.data_objects.create('/testing/home/rods/data').unlink()
        obj = self.irods.data_objects.get('/testing/trash/home/rods/data')
        if 'ipc::trash_timestamp' not in obj.metadata:
            self.fail('data moved to trash did not receive timestamp')
        obj.unlink(force=True)


class CyverseTrashApiRmCollTest(IrodsTestCase):
    """Tests of cyverse_trash_api_rm_coll PEPs"""

    def test_failed_moved_to_trash(self):
        """Verify that a collection that couldn't be moved to trash doesn't get a timestamp"""
        user = 'user'
        coll = path.join('/testing/home', user, 'coll')
        self.ensure_user_exists(user)
        self.irods.collections.create(coll)
        self.irods.acls.set(iRODSAccess('write', coll, 'rods'), admin=True)
        self.irods.acls.set(iRODSAccess('write', coll, 'rodsadmin'), admin=True)
        try:
            self.irods.collections.remove(coll)
        except CAT_NO_ACCESS_PERMISSION:
            pass
        if 'ipc::trash_timestamp' in self.irods.collections.get(coll).metadata:  # type: ignore
            self.fail('collection that could not be moved to trash did not receive timestamp')
        self.irods.acls.set(iRODSAccess('own', coll, 'rods'), admin=True)
        self.ensure_coll_absent(coll)
        self.irods.users.remove(user)

    def test_successful_move_to_trash(self):
        """Verify that a collection that was moved to trash gets a timestamp"""
        self.irods.collections.create('/testing/home/rods/coll').remove()  # type: ignore
        coll = self.irods.collections.get('/testing/trash/home/rods/coll')
        if 'ipc::trash_timestamp' not in coll.metadata:  # type: ignore
            self.fail('collection moved to trash did not receive timestamp')
        coll.remove(force=True)  # type: ignore


class CyverseTrashTest(IrodsTestCase):
    """Test the cyverse_trash.re rule-base"""

    @unittest.skip("not implemented")
    def test_ipctrash_mktimestampvar(self):
        """Test _ipcTrash_mkTimestampVar"""

    @unittest.skip("not implemented")
    def test_ipctrash_mkobjdataidvar(self):
        """Test _ipcTrash_mkObjDataIdVar"""

    @unittest.skip("not implemented")
    def test_ipctrash_managetimeavu(self):
        """Test _ipcTrash_manageTimeAVU"""


if __name__ == "__main__":
    unittest.main()
