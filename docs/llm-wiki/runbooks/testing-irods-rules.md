---
type: Runbook
title: Testing iRODS Rules
description: The Python unittest suite in playbooks/tests/rules/ that exercises the Data Store's iRODS rule files against a live server, its test_rules.py support library and mocks, and the separate template-expansion test playbook.
resource: /playbooks/tests/rules/test_rules.py
tags: [testing, irods, rules, unittest, python-irodsclient, mocks]
timestamp: 2026-09-17T00:00:00Z
---

The rule files in `playbooks/files/irods/etc/irods/` (see the
[irods-rules](/irods-rules/index.md) section) have Python `unittest` tests in
`playbooks/tests/rules/`. These tests execute rule logic on a running iRODS
server and inspect the results through python-irodsclient, SSH, and the
server's test-mode log.

**No script, playbook, or doc in the repo invokes these tests.** The
`testing/` harness (see [Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md))
runs playbook tests only. What follows is what the code requires.

## Test modules

There is one module per rule file, named after it (`cyverse_repl.py` tests
`cyverse_repl.re`; `avra-env.py` tests the rendered `avra-env.re`). Each
module ends with `unittest.main()`, so it can be executed as a script. Every
module does `import test_rules`, so it must run with `playbooks/tests/rules/`
on the Python path.

Some test classes are decorated with `@test_rules.unimplemented`, which strips
their `test_*` methods and fixtures so they are skipped. This appears in
`avra-env.py`, `cyverse.py`, `cyverse_core.py`, `cyverse_encryption.py`,
`cyverse_json.py`, `cyverse_logic.py`, and `cyverse_repl.py`.

## The test_rules library

`test_rules.py` provides the shared fixtures:

- **Connection settings** from environment variables: `IRODS_HOST` (default
  `localhost`), `IRODS_PORT` (`1247`), `IRODS_ZONE_NAME` (`tempZone`),
  `IRODS_USER_NAME` (`anonymous`), and `IRODS_PASSWORD` (empty).
- **`setUpModule()`**, which each test module calls: runs `iinit` with
  `IRODS_PASSWORD`, copies `mocks/amqp-topic-send` over
  `/var/lib/irods/msiExecCmd_bin/amqp-topic-send` on the server so rules don't
  publish real AMQP messages, and truncates
  `/var/lib/irods/log/test_mode_output.log`. `tearDownModule()` restores
  `amqp-topic-send` from `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/`.
- **`IrodsTestCase`**, a `TestCase` with lazily opened `irods`
  (`iRODSSession`), `ssh` (paramiko), and `scp` clients, plus helpers:
  - `fn_test(fn, args, exp_res)` calls a rule function with typed arguments
    and asserts its result.
  - `mk_rule(logic)` and `exec_rule(rule, res_type)` run arbitrary rule
    language through `irods_rule_engine_plugin-irods_rule_language-instance`,
    raising `RuleExecFailure` on an error stack or stderr output.
  - `update_rulebase([(rulebase, local_path)])` copies local files to
    `/etc/irods/<rulebase>` and reloads rules by touching `/etc/irods/core.re`.
  - `ensure_coll_absent`, `ensure_obj_absent`, `ensure_user_absent`,
    `ensure_user_exists`, and `put_empty` manage fixtures.
  - `clear_delay_queue()` runs `iqdel -a`; `tail_rods_log()` reads the
    test-mode log.
- **`IrodsVal` / `IrodsType`**, which format Python values as rule-language
  literals and parse rule output back (booleans, integers, strings, paths,
  string lists, key-value pairs, string tuples).

## Mocks

`mocks/` holds stand-ins that tests swap onto the server and swap back in
`tearDown` or `tearDownModule`:

- Rule base stubs for `coge.re`, `cyverse_core.re`, `cyverse_encryption.re`,
  `cyverse_logic.re`, `cyverse_repl.re`, `cyverse_transfer_tracking.re`,
  `cyverse_trash.re`, and `pire.re`. Their rules mostly write a
  "`<rule>` called" line to the server log; a few add minimal behavior (for
  example, the `cyverse_repl.re` stub sets the default resource to
  `ingestRes`). Tests install them with `update_rulebase` and restore the real
  file from `playbooks/files/irods/etc/irods/`.
- Command scripts for `msiExecCmd_bin`: `amqp-topic-send` (does nothing),
  `add-transfer` and `irepl-exec` (always fail, to test failure handling).

## Prerequisites visible in the code

- A running iRODS server at `IRODS_HOST` started in test mode, so it writes
  `test_mode_output.log`, with the rule files deployed. The testing
  environment's configured provider and consumers start iRODS with
  `irodsctl --test`.
- Passwordless SSH to that host: `ssh.connect(host, password='')` uses the
  local user name, and files are written under `/etc/irods` and
  `/var/lib/irods`. The testing containers allow passwordless root SSH.
- iCommands on the client (`iinit`, `iqdel`), and the Python packages
  `python-irodsclient`, `paramiko`, and `scp`.
- Test data assumes the testing environment's resources: for example,
  `cyverse_repl.py` replicates to `replRes` and moves replicas off `ingestRes`.

The `ansible-tester` image satisfies the client side: it installs iCommands,
`python-irodsclient`, `paramiko`, and `scp`, and sets `IRODS_USER_NAME=rods`
and `IRODS_PASSWORD`, while `testing/ansible-tester/run` sets `IRODS_HOST` and
`IRODS_ZONE_NAME`. Its inspection shell (`test-playbook -i`) mounts
`playbooks/` at `/playbooks-under-test`, so the tests are at
`/playbooks-under-test/tests/rules/` there. That this is the intended way to
run them is an inference; the repo doesn't say.

## Template expansion tests

`playbooks/tests/irods_rule_templates.yml` is a separate playbook, with no
matching playbook in `playbooks/`, that renders `cyverse-env.re.j2`,
`avra-env.re.j2`, `esiil-env.re.j2`, `ncems-env.re.j2`, and `pire-env.re.j2`
with `lookup('template', ...)` and asserts the constants they expand to, using
the defaults in `playbooks/group_vars/all/` and several custom-value plays. It
targets `localhost`, but the template needs an inventory with an
`irods_catalog` group, and the expected defaults name the testing
environment's provider host
(`dstesting-provider_configured-1.dstesting_default`). Run without an
inventory, it fails on the missing `irods_catalog` group.

## Caveats

- In `cyverse_repl.py`, `TestSyncreplicasFailure` builds the remote path of
  `irepl-exec` as `Path('var', 'lib', ...).absolute()`, which resolves against
  the local working directory rather than `/`, so the mock may not land in the
  server's `/var/lib/irods/msiExecCmd_bin/`. This is from reading the code.

# Citations

[1] `playbooks/tests/rules/test_rules.py` — shared test library.
[2] `playbooks/tests/rules/*.py` — per-rule test modules.
[3] `playbooks/tests/rules/mocks/` — rule base stubs and command script mocks.
[4] `playbooks/files/irods/etc/irods/` — rule files under test.
[5] `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/` — real command scripts restored after tests.
[6] `playbooks/tests/irods_rule_templates.yml` — template expansion tests.
[7] `testing/ansible-tester/Dockerfile`, `testing/ansible-tester/run` — tester image environment.
[8] `testing/env/irods-provider/scripts/service.sh.template`, `testing/env/irods-consumer/scripts/service.sh.template` — test-mode iRODS startup.
