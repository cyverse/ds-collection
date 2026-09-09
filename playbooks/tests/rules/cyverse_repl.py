#!/usr/bin/env python  # pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

"""Tests of cyverse_repl.re rule logic."""

import json
import subprocess
from subprocess import CalledProcessError
from typing import Any
import unittest

from irods.column import Criterion
from irods.exception import SYS_INVALID_RESC_INPUT, SYS_NOT_ALLOWED
from irods.models import RuleExec
from irods.path import iRODSPath

import test_rules
from test_rules import IrodsTestCase, IrodsType, IrodsVal, RuleExecFailure


def setUpModule():  # pylint: disable=invalid-name
    """Set up main module"""
    test_rules.setUpModule()


def tearDownModule():  # pylint: disable=invalid-name
    """Tear down main module"""
    test_rules.tearDownModule()


class TestReplReplicateFailureChecksum(IrodsTestCase):
    """Tests _repl_replicate handling of checksum error"""

    def __init__(self, method: str):
        super().__init__(method)
        self._objPath = None
        self._ruleExecOut = None

    def setUp(self):
        super().setUp()
        self._objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        obj = self.irods.data_objects.create(self._objPath)
        self.irods.data_objects.modDataObjMeta({"objPath": self._objPath}, {"chksum": "bad"})
        oid = obj.id  # pylint: disable=no-member  # type: ignore
        ruleSrc = f"""
            *ec = errorcode(_repl_replicate({oid}, 'replRes'));
            writeLine('stdout', *ec);
        """
        self._ruleExecOut = self.exec_rule(self.mk_rule(ruleSrc), IrodsType.INTEGER)

    def tearDown(self):
        if self._objPath:
            self.ensure_obj_absent(self._objPath)
        super().tearDown()

    def test_log_msg(self):
        """Verify that a message is logged"""
        for line in self.tail_rods_log():
            if f'failed to replicate data object {self._objPath} due to checksum error' in line:
                return
        self.fail("Checksum issue not logged")

    def test_resp_code(self):
        """Verify that it returns a 0"""
        self.assertEqual(self._ruleExecOut, IrodsVal.integer(0))


class TestReplReplicateFailureReplGone(IrodsTestCase):
    """Tests _repl_replicate handles an object that has been deleted"""

    def test(self):
        """
        Verify an attempt to replicate an object that no longer exists is logged
        """
        try:
            self.exec_rule(self.mk_rule("_repl_replicate(1, 'ingestRes')"), IrodsType.NONE)
        except RuleExecFailure:
            self.fail("_repl_replicate failed when obj gone")


class TestReplReplicateFailureReplicated(IrodsTestCase):
    """Tests _repl_replicate handling the case when the data object is already replicated"""

    @unittest.skip("not implemented")
    def test_log_msg(self):
        """Verify that a message is logged"""

    @unittest.skip("not implemented")
    def test_resp_code(self):
        """Verify that it returns a 0"""


class TestReplReplicateFailureUnknown(IrodsTestCase):
    """Tests _repl_replicate handling of failure"""

    def __init__(self, method: str):
        super().__init__(method)
        self._objPath = None
        self._ruleExecOut = 0

    def setUp(self):
        super().setUp()
        self._objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        obj = self.irods.data_objects.create(self._objPath)
        try:
            self.exec_rule(self.mk_rule(f"_repl_replicate({obj.id}, 'fakeRes')"), IrodsType.NONE)  # type: ignore  # pylint: disable=no-member,line-too-long  # noqa: E501
        except RuleExecFailure as e:
            self._ruleExecOut = e.resp_code()

    def tearDown(self):
        if self._objPath:
            self.ensure_obj_absent(self._objPath)
        super().tearDown()

    def test_log(self):
        """Test replication failure for an unknown reason"""
        for line in self.tail_rods_log():
            if f'failed to replicate data object {self._objPath}, retry in 8 hours' in line:
                return
        self.fail("unknown failure not logged")

    def test_response_code(self):
        """Verify that an error code is returned"""
        self.assertNotEqual(self._ruleExecOut, 0)


class TestReplReplicateSuccess(IrodsTestCase):
    """Tests _repl_replicate success"""

    def __init__(self, method: str):
        super().__init__(method)
        self._objPath = None
        self._ruleExecOut = None

    def setUp(self):
        super().setUp()
        self._objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        obj = self.irods.data_objects.create(self._objPath)
        obj.chksum()
        oid = obj.id  # pylint: disable=no-member  # type: ignore
        ruleSrc = f"""
            _repl_replicate({oid}, 'replRes');
            writeLine('stdout', temporaryStorage.cyverse_repl_replicate);
        """
        self._ruleExecOut = self.exec_rule(self.mk_rule(ruleSrc), IrodsType.STRING)

    def tearDown(self):
        if self._objPath:
            self.ensure_obj_absent(self._objPath)
        super().tearDown()

    def test_repl_replicate_sess_var_empty(self):
        """Verify temporaryStorage.repl_replicate is empty"""
        self.assertEqual(self._ruleExecOut, IrodsVal.string(""))

    def test_replicate_success_replicated(self):
        """Verify that the data object was replicated"""
        obj = self.irods.data_objects.get(self._objPath)
        self.assertEqual(len(obj.replicas), 2)

    def test_replicate_success_log_msg(self):
        """Verify that message logged"""
        for line in self.tail_rods_log():
            if f"replicated data object {self._objPath}" in line:
                return
        self.fail("Successful replication not logged")


class TestMvreplicasNoMv(IrodsTestCase):
    """Tests of when no replicas need to be moved"""

    def test(self):
        """Verify no replicas moved"""
        objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        self.ensure_obj_absent(objPath)
        obj = self.irods.data_objects.create(objPath)
        obj.chksum()
        obj.replicate()
        self.exec_rule(
            self.mk_rule(f"_repl_mvReplicas({obj.id}, 'ingestRes', 'replRes')"), IrodsType.NONE)  # type: ignore  # pylint: disable=no-member,line-too-long  # noqa: E501
        obj = self.irods.data_objects.get(objPath)
        if (
            len(obj.replicas) != 2
            or obj.replicas[0].resource_name != 'ingestRes'
            or obj.replicas[1].resource_name != 'replRes'
        ):
            self.fail("Replicas were moved when they shouldn't have been")
        self.irods.data_objects.unlink(objPath, force=True)


class TestMvreplicasMvIngestSuccess(IrodsTestCase):
    """Tests of _mvReplicas, replication to ingest"""

    def test(self):
        """Test when ingest replica move succeeds"""
        objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        self.ensure_obj_absent(objPath)
        obj = self.irods.data_objects.create(objPath, 'replRes')
        obj.chksum()
        self.exec_rule(
            self.mk_rule(f"_repl_mvReplicas({obj.id}, 'ingestRes', 'ingestRes')"), IrodsType.NONE)  # type: ignore  # pylint: disable=no-member,line-too-long  # noqa: E501
        obj = self.irods.data_objects.get(objPath)
        self.assertEqual(
            obj.replicas[0].resource_name, 'ingestRes', "failed to move replica to ingestRes")
        self.irods.data_objects.unlink(objPath, force=True)


class TestMvreplicasMvIngestFailure(IrodsTestCase):
    """Tests of _mvReplicas, unsuccessful replication to ingest"""

    def __init__(self, methodName) -> None:
        super().__init__(methodName)
        self._objPath = None
        self._response_code = IrodsVal.none()

    def setUp(self):
        super().setUp()
        self._objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        self.ensure_obj_absent(self._objPath)
        obj = self.irods.data_objects.create(self._objPath, 'replRes')
        oid = obj.id  # pylint: disable=no-member  # type: ignore
        ruleSrc = f"writeLine('stdout', errorcode(_repl_mvReplicas({oid}, 'pireRes', 'pireRes')));"
        self._response_code = self.exec_rule(self.mk_rule(ruleSrc), IrodsType.INTEGER)

    def tearDown(self):
        if self._objPath:
            self.ensure_obj_absent(self._objPath)
        super().tearDown()

    def test_log_msg(self):
        """Verify that the failure was logged"""
        for line in self.tail_rods_log():
            if f"failed to completely move replicas of data object {self._objPath}" in line:
                return
        self.fail("Failed replica move not logged")

    def test_replica_not_moved(self):
        """Verify that the replica was not moved to the correct resource"""
        self.assertEqual(
            self.irods.data_objects.get(self._objPath).replicas[0].resource_name,
            'replRes',
            "moved replica when it shouldn't have")

    def test_resp_code(self):
        """Verify that the rule response code indicates failure"""
        self.assertNotEqual(self._response_code, IrodsVal.integer(0), "success returned")


class TestMvreplicasMvReplSuccess(IrodsTestCase):
    """Test _repl_mvReplicas, successfully moving the replicated replica"""

    def test(self):
        """Test it"""
        objPath = iRODSPath(self.irods.zone, "home", "shared", "avra", "obj")
        self.ensure_obj_absent(objPath)
        self.update_rulebase([('pire.re', 'mocks/pire.re')])
        obj = self.irods.data_objects.create(objPath)
        try:
            obj.chksum()
            obj.replicate('replRes')
            self.exec_rule(
                self.mk_rule(f"_repl_mvReplicas({obj.id}, 'ingestRes', 'pireRes')"),  # type: ignore  # pylint: disable=no-member,line-too-long  # noqa: E501
                IrodsType.NONE)
            obj = self.irods.data_objects.get(objPath)
            if (
                len(obj.replicas) != 2
                or obj.replicas[0].resource_name != 'ingestRes'
                or obj.replicas[1].resource_name != 'pire'
            ):
                self.fail("failed to move both replicas")
        except RuleExecFailure as e:
            self.fail(f"_repl_mvReplicas failed: {e}")
        finally:
            obj.unlink(force=True)
            self.update_rulebase([('pire.re', '../../files/irods/etc/irods/pire.re')])


class TestMvreplicasMvReplFailure(IrodsTestCase):
    """Tests of _repl_mvReplicas, when moving the replica fails"""

    def __init__(self, methodName) -> None:
        super().__init__(methodName)
        self._obj_path = None
        self._resp_code = None

    def setUp(self):
        super().setUp()
        self._obj_path = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        self.ensure_obj_absent(self._obj_path)
        obj = self.irods.data_objects.create(self._obj_path)
        obj.chksum()
        oid = obj.id  # type: ignore  # pylint: disable=no-member
        ruleSrc = f"""
            writeLine('serverLog', errorcode(_repl_mvReplicas({oid}, 'replRes', 'avraRes')));
        """
        self._resp_code = self.exec_rule(self.mk_rule(ruleSrc),  IrodsType.INTEGER)

    def tearDown(self):
        self.irods.data_objects.unlink(self._obj_path, force=True)
        super().tearDown()

    def test_log(self):
        """Verify that a failure message is logged"""
        for line in self.tail_rods_log():
            if f"failed to completely move replicas of data object {self._obj_path}" in line:
                return
        self.fail("Failed replica move not logged")

    def test_replicas(self):
        """Test that repl replica isn't moved"""
        obj = self.irods.data_objects.get(self._obj_path)
        if (
            len(obj.replicas) != 2
            or obj.replicas[0].resource_name != "ingestRes"
            or obj.replicas[1].resource_name != "replRes"
        ):
            self.fail("replicas moved in unexpected ways")

    def test_resp_code(self):
        """Test that the response code isn't 0"""
        self.assertNotEqual(self._resp_code, IrodsVal.integer(0), "success returned")


class TestMvreplicasGone(IrodsTestCase):
    """Tests of _repl_mvReplicas with the data object no longer exists"""

    def test(self):
        """Verify that the rule succeeds"""
        ruleSrc = """
            *rc = _repl_mvReplicas(1, "ingestRes", "replRes");
            writeLine('stdout', *rc);
        """
        rc = self.exec_rule(self.mk_rule(ruleSrc), IrodsType.INTEGER)
        self.assertEqual(rc, IrodsVal.integer(0), "no-op move failed")


class TestSyncreplicasGone(IrodsTestCase):
    """Test _repl_syncReplicas when data object no longer exists"""

    def test(self):
        """Test rule succeeds"""
        rc = self.exec_rule(
            self.mk_rule("writeLine('stdout', _repl_syncReplicas(1))"), IrodsType.INTEGER)
        self.assertEqual(rc, IrodsVal.integer(0), "sync failed when object no longer exists")


class TestSyncreplicasSuccess(IrodsTestCase):
    """Tests of _repl_syncReplicas success"""

    def test(self):
        """Test it"""
        objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        obj = self.irods.data_objects.create(objPath)
        rc = self.exec_rule(
            self.mk_rule(f"writeLine('stdout', _repl_syncReplicas({obj.id}))"), IrodsType.INTEGER)  # type: ignore  # pylint: disable=no-member,line-too-long  # noqa: E501
        self.assertEqual(rc, IrodsVal.integer(0), "sync failed")
        obj.unlink(force=True)


# NB: I cannot find a way to test this. `irepl -a -U fails` silently when the
# resource with the stale replica is not accessible do to either status=down or
# context=write=0. I don't know another way to make a replica synchronization
# fail.
@test_rules.unimplemented
class TestSyncreplicasFailure(IrodsTestCase):
    """Tests of _repl_syncReplicas failure logic"""

    @unittest.skip("not implemented")
    def test_fail_status(self):
        """Test handling of replication failure other than -808000"""

    @unittest.skip("not implemented")
    def test_log_msg(self):
        """Verify that a retry message was logged"""


class TestConsts(IrodsTestCase):
    """Tests of the private constants"""

    def test_id(self):
        """Verify that _cyverse_repl_ID set correctly"""
        self.fn_test('_cyverse_repl_ID', [], IrodsVal.string('cyverse_repl'))

    def test_action(self):
        """Verify that _cyverse_repl_ACTION set correctly"""
        self.fn_test('_cyverse_repl_ACTION', [], IrodsVal.string('deferred replication'))


class TestDelayTime(IrodsTestCase):
    """Test delay time management logic"""

    def test_delaytime(self):
        """Test _delayTime initial delay time returns initial value"""
        self.fn_test('_delayTime', [], IrodsVal.integer(0))

    def test_incdelaytime(self):
        """Test _incDelayTime adds 1 second to _delayTime"""
        rule = '''
            _incDelayTime;
            writeLine('stdout', _delayTime);
        '''
        delay_time = self.exec_rule(self.mk_rule(rule), IrodsType.INTEGER)
        self.assertEqual(delay_time, IrodsVal.integer(1), "delay time not incremented")


class TestLogging(IrodsTestCase):
    """Test message logging"""

    def test_logmsg(self):
        """Test _repl_logMsg"""
        self.exec_rule(self.mk_rule("_repl_logMsg('test_logmsg')"), IrodsType.NONE)
        for line in self.tail_rods_log():
            if "DS: test_logmsg" in line:
                return
        self.fail("Failed to format log message correctly")


class _TestScheduleRule(IrodsTestCase):

    def __init__(self, methodName, rule) -> None:
        super().__init__(methodName)
        self._rule = rule
        self._delay_time = 0

    def setUp(self):
        super().setUp()
        self.close_irods()
        test_rule = f'''
            {self._rule};
            writeLine('stdout', _delayTime);
        '''
        self._delay_time = int(str(self.exec_rule(self.mk_rule(test_rule), IrodsType.INTEGER)))

    def tearDown(self):
        subprocess.run("iqdel -a", shell=True, check=True, encoding='utf-8')
        super().tearDown()

    @property
    def delay_time(self):
        """the delay time after scheduling a rule"""
        return self._delay_time

    def _is_scheduled(self, rule):
        query = self.irods.query(RuleExec)
        query = query.filter(Criterion('=', RuleExec.name, rule))
        for _ in query.get_results():
            return True
        return False

    def _is_exec_freq(self, rule, freq):
        query = self.irods.query(RuleExec.frequency)
        query = query.filter(Criterion('=', RuleExec.name, rule))
        rec = query.first()
        return not rec or rec[RuleExec.frequency] != freq

    def _is_delay_inc(self):
        return self._delay_time == 1


class TestSchedulemv(_TestScheduleRule):
    """Tests of _repl_scheduleMv"""

    def __init__(self, methodName) -> None:
        super().__init__(methodName, "_repl_scheduleMv(1, 'ingestRes', 'replRes')")

    def test_rule_scheduled(self):
        """Verify that the rule _repl_mvReplicas is scheduled correctly"""
        if not self._is_scheduled('_repl_mvReplicas(*Object, *IngestName, *ReplName)'):
            self.fail('Failed to schedule _repl_mvReplicas')

    def test_exec_freq(self):
        """Verify that the execution frequency is set correctly"""
        if (
            self._is_exec_freq(
                '_repl_mvReplicas(*Object, *IngestName, *ReplName)', '8h REPEAT UNTIL SUCCESS')
        ):
            self.fail('The execution frequency is incorrect')

    def test_delay_time_incremented(self):
        """Verify that the delay time counter is incremented by 1 second"""
        if not self._is_delay_inc():
            self.fail('The delay time was not incremented')

    @unittest.skip("not implemented")
    def test_no_dupes(self):
        """
        Verify that it won't schedule multiple replication events for the same
        object during the same session
        """


class TestSchedulerepl(_TestScheduleRule):
    """Tests of _repl_scheduleRepl"""

    def __init__(self, methodName) -> None:
        super().__init__(methodName, "_repl_scheduleRepl(1, 'replRes')")

    def test_rule_scheduled(self):
        """Verify that the rule _repl_scheduleRepl is scheduled correctly"""
        if not self._is_scheduled('_repl_replicate(*Object, *RescName)'):
            self.fail('Failed to schedule _repl_replicate')

    def test_exec_freq(self):
        """Verify that the execution frequency is set correctly"""
        if self._is_exec_freq('_repl_replicate(*Object, *RescName)', '8h REPEAT UNTIL SUCCESS'):
            self.fail('The execution frequency is incorrect')

    def test_delay_time_incremented(self):
        """Verify that the delay time counter is incremented by 1 second"""
        if not self._is_delay_inc():
            self.fail('The delay time was not incremented')

    @unittest.skip("not implemented")
    def test_no_dupes(self):
        """
        Verify that it won't schedule multiple replication events for the same
        object during the same session
        """


class TestSchedulesyncreplicas(IrodsTestCase):
    """Tests of _repl_scheduleSyncReplicas"""

    def __init__(self, methodName) -> None:
        super().__init__(methodName)
        self._objPath = None
        self._delayTime = 0

    def setUp(self):
        super().setUp()
        self._objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        obj = self.irods.data_objects.create(self._objPath)
        obj.chksum()
        obj.replicate()
        with obj.open('r+') as f:
            f.write(b'change')
        obj_id = obj.id  # type: ignore # pylint: disable=no-member
        test_rule = f'''
            _repl_scheduleSyncReplicas({obj_id});
            writeLine('stdout', _delayTime);
        '''
        self._delayTime = int(str(self.exec_rule(self.mk_rule(test_rule), IrodsType.INTEGER)))

    def tearDown(self):
        subprocess.run("iqdel -a", shell=True, check=True, encoding='utf-8')
        self.irods.data_objects.unlink(self._objPath, force=True)
        super().tearDown()

    def test_rule_scheduled(self):
        """Verify that _repl_syncReplicas is scheduled correctly"""
        query = self.irods.query(RuleExec)
        query = query.filter(Criterion('=', RuleExec.name, "_repl_syncReplicas(*Object)"))
        for _ in query.get_results():
            return True
        return False

    def test_exec_freq(self):
        """Verify that the execution frequency is set correctly"""
        query = self.irods.query(RuleExec.frequency)
        query = query.filter(Criterion('=', RuleExec.name, "_repl_syncReplicas(*Object)"))
        rec = query.first()
        return not rec or rec[RuleExec.frequency] != '8h REPEAT UNTIL SUCCESS'

    def test_delay_time_incremented(self):
        """Verify that the delay time counter is incremented by 1 second"""
        self.assertGreater(self._delayTime, 0, "delay time wasn't incremented")


class TestFileresc(IrodsTestCase):
    """Tests of _repl_findResc"""

    def test_default(self):
        """Test that the default resource is correctly detected"""
        for p in IrodsTestCase.prep_path(iRODSPath(self.irods.zone, 'object')):
            with self.subTest(p=p):
                self.fn_test(
                    '_repl_findResc', [p], IrodsVal.tuple_string_string(('ingestRes', 'preferred')))

    def test_bespoke(self):
        """
        Test that a custom resource is chosen when a collection is assigned to
        it
        """
        for p in (
            IrodsTestCase.prep_path(iRODSPath(self.irods.zone, 'home', 'shared', 'avra', 'object'))
        ):
            with self.subTest(p=p):
                self.fn_test(
                    '_repl_findResc', [p], IrodsVal.tuple_string_string(('avraRes', 'forced')))


class TestFindreplresc(IrodsTestCase):
    """Tests of _repl_findReplResc"""

    def test_default(self):
        """
        Test that the replication resource is correctly determined for the
        default resource
        """
        self.fn_test(
            '_repl_findReplResc',
            [IrodsVal.string('ingestRes')],
            IrodsVal.tuple_string_string(('replRes', 'preferred')))

    def test_bespoke_replicated(self):
        """
        Test that the replication resource is correctly determined for a
        a resource that isn't the default and has specified replication
        resource.
        """
        avra = self.irods.resources.get('avraRes')
        avra.metadata.set("ipc::replica-resource", "ingestRes", "forced")
        self.fn_test(
            '_repl_findReplResc',
            [IrodsVal.string('avraRes')],
            IrodsVal.tuple_string_string(('ingestRes', 'forced')))
        avra.metadata.remove("ipc::replica-resource", "ingestRes", "forced")

    def test_bespoke_unreplicated(self):
        """
        Test that the replication resource is correctly determined for a
        a resource that isn't the default and doesn't have a specified
        replication resource.
        """
        self.fn_test(
            '_repl_findReplResc',
            [IrodsVal.string('avraRes')],
            IrodsVal.tuple_string_string(('avraRes', 'preferred')))


class _CreateoroverwriteTest(IrodsTestCase):

    def __init__(self, method: str):
        super().__init__(method)
        self._objPath = None

    def setUp(self):
        super().setUp()
        self._objPath = iRODSPath(self.irods.zone, "home", self.irods.username, "obj")
        self.irods.data_objects.create(self._objPath).chksum()
        subprocess.run("iqdel -a", shell=True, check=True, encoding='utf-8')
        self.close_irods()

    def tearDown(self):
        self.irods.data_objects.unlink(self._objPath, force=True)
        subprocess.run("iqdel -a", shell=True, check=True, encoding='utf-8')
        super().tearDown()

    @property
    def objPath(self):
        """Return the target iRODS object path for this test."""
        return self._objPath

    def get_rule_exec_context(self, rule) -> Any:
        """Rettrieve the rule execution context for a deferred execution"""
# NB: RuleExec doesn't have the context field in python-irodsclient. Available in 4.3
        query = f"select RULE_EXEC_CONTEXT where RULE_EXEC_NAME = '{rule}'"
        try:
            resp = subprocess.run(
                f'iquest %s "{query}"',
                stdout=subprocess.PIPE,
                shell=True,
                check=True,
                encoding='utf-8')
            return json.loads(resp.stdout)
        except CalledProcessError as e:
            if e.returncode == 1:
                return None
            else:
                raise
# NB: ^^^

    def is_replreplicate_sched(self):
        """
        Indicates whether or not _repl_replicate is scheduled as a deferred
        execution
        """
        query = self.irods.query(RuleExec)
        query = query.filter(Criterion('=', RuleExec.name, '_repl_replicate(*Object, *RescName)'))
        return query.first() is not None


class TestCreateoroverwriteCreateIngestPath(_CreateoroverwriteTest):
    """
    Tests of _ipcRepl_createOrOverwrite when the data object path is provided by
    path
    """

    def setUp(self):
        super().setUp()
        self.exec_rule(
            self.mk_rule(f"_ipcRepl_createOrOverwrite({self.objPath}, 'ingestRes', true)"),
            IrodsType.NONE)

    def test_rule_sched(self):
        """
        Verify that a _repl_replicate is scheduled when a replica is created on
        the ingest resource when the data path is provided as a path
        """
        if not self.is_replreplicate_sched():
            self.fail("_repl_replicate not scheduled")

    def test_rule_correct_id(self):
        """
        Verify that when called for a data object replica that is being created
        on the ingest resource, the correct Id is passed to the rule.
        """
        context = self.get_rule_exec_context('_repl_replicate(*Object, *RescName)')
        if not context:
            self.fail("_repl_replicate not scheduled")
        objectParam = context['ms_param_array']['ms_params'][0]['in_out_struct']
        oid = self.irods.data_objects.get(self.objPath).id  # type: ignore  # pylint: disable=no-member,line-too-long  # noqa: E501
        self.assertEqual(objectParam, oid, "Scheduled replication of wrong data object")

    def test_rule_correct_resc(self):
        """
        Verify that when called for a data object replica that is being created
        on the ingest resource, the repl resource is passed to the rule.
        """
        context = self.get_rule_exec_context('_repl_replicate(*Object, *RescName)')
        if not context:
            self.fail("_repl_replicate not scheduled")
        rescNameParam = context['ms_param_array']['ms_params'][1]['in_out_struct']
        self.assertEqual(rescNameParam, 'replRes', "Scheduled replication on wrong resource")


class TestCreateoroverwriteCreateIngestStr(_CreateoroverwriteTest):
    """
    Tests of _ipcRepl_createOrOverwrite when the data object path is provided by
    string
    """

    def test(self):
        """
        Verify that it handles replica creation on ingest resource correctly
        when the object is provided as a string
        """
        self.exec_rule(
            self.mk_rule(f"_ipcRepl_createOrOverwrite('{self.objPath}', 'ingestRes', true)"),
            IrodsType.NONE)
        if not self.is_replreplicate_sched():
            self.fail("_repl_replicate not scheduled")


class TestCreateoroverwriteCreateRepl(_CreateoroverwriteTest):
    """
    Verify that _ipcRepl_createOrOverwrite handles replica creation of repl
    resource correctly.
    """

    def test(self):
        """Verify that it passes the ingest resource to _repl_replicate"""
        self.exec_rule(
            self.mk_rule(f"_ipcRepl_createOrOverwrite({self.objPath}, 'replRes', true)"),
            IrodsType.NONE)
        context = self.get_rule_exec_context('_repl_replicate(*Object, *RescName)')
        if not context:
            self.fail("_repl_replicate not scheduled")
        rescNameParam = context['ms_param_array']['ms_params'][1]['in_out_struct']
        self.assertEqual(rescNameParam, 'ingestRes', "Scheduled replication on wrong resource")


class TestCreateoroverwriteOverwrite(_CreateoroverwriteTest):
    """Tests of _ipcRepl_createOrOverwrite"""

    def setUp(self):
        super().setUp()
        obj = self.irods.data_objects.get(self.objPath)
        obj.replicate()
        subprocess.run(
            f"iadmin modrepl data_id {obj.id} replica_number 1 DATA_REPL_STATUS 0",  # type: ignore  # pylint: disable=no-member,line-too-long  # noqa: E501
            shell=True,
            check=True,
            encoding='utf-8')
        self.exec_rule(
            self.mk_rule(f"_ipcRepl_createOrOverwrite({self.objPath}, 'replRes', false)"),
            IrodsType.NONE)

    def test_sched(self):
        """Verify that it schedules a _repl_syncReplicas rule."""
        query = self.irods.query(RuleExec)
        query = query.filter(Criterion('=', RuleExec.name, '_repl_syncReplicas(*Object)'))
        if not query.first():
            self.fail("_repl_syncReplicas not scheduled")

    def test_rule_correct_id(self):
        """Verify that the correct data id is passed to the rule."""
        context = self.get_rule_exec_context('_repl_syncReplicas(*Object)')
        if not context:
            self.fail("_repl_syncReplicas not scheduled")
        objectParam = context['ms_param_array']['ms_params'][0]['in_out_struct']
        oid = self.irods.data_objects.get(self.objPath).id  # type: ignore  # pylint: disable=no-member,line-too-long  # noqa: E501
        self.assertEqual(objectParam, oid, "Scheduled replica synchronization of wrong data object")


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


@test_rules.unimplemented
class TestDynamicApiPeps(IrodsTestCase):
    """Tests of the dynamic API PEPs"""


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


if __name__ == "__main__":
    unittest.main()
