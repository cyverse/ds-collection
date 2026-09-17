---
type: Playbook
title: irods_restart_all.yml
description: Restarts iRODS on every iRODS host in dependency order — stopping consumers, restarting catalog providers, then starting consumers.
resource: /playbooks/irods_restart_all.yml
tags: [irods, restart, operations]
timestamp: 2026-09-17T00:00:00Z
---

`irods_restart_all.yml` targets `irods` as the service account
(`become: {{ _irods_become_svc_acnt }}`) and is tagged `non_idempotent`. It
includes `tasks/irods/restart.yml` with `restart_op: always`.

## What the task file does

For each host, using [irods_ctl](/ansible-plugins/irods-ctl.md):

1. Stops iRODS if the host is a resource server but not a catalog provider.
2. Restarts iRODS if the host is a catalog provider.
3. Starts iRODS again on the resource servers.

With `restart_op: always`, all three steps run regardless of the current
state. The task file also accepts `restart_op: if running`: it then does
nothing unless `/etc/irods/server_config.json` exists, restarts providers
only if they're already running, and starts consumers only if the stop step
changed something.

Because Ansible runs the task file on all hosts in parallel, the ordering
comes from the task sequence, not from separate plays.

`tasks/irods/restart.yml` passes `test_log: true` to `irods_ctl` only when
tasks tagged `no_testing` are skipped, as in the test harness.

## Tests

`playbooks/tests/irods_restart_all.yml` imports
`tests/tasks/irods/test_running.yml` on every `irods` host. That task file
greps `irodsctl status` output with `--invert` for `No servers running`. The
check passes whenever any line of output doesn't match. No output contains
that string: when no server is running, iRODS 4.3.1's `irodsctl` prints
`No iRODS servers running.`, and the containerized `irodsctl` adapter prints
`No iRODS servers running` when it can't reach the container. So it is a weak
check.

## Related

- [irods_restart_rs.yml](/ansible-playbooks/irods-restart-rs.md)
- [irods_stop_all.yml](/ansible-playbooks/irods-stop-all.md)

# Citations

[1] `playbooks/irods_restart_all.yml` — the playbook.
[2] `playbooks/tasks/irods/restart.yml` — the restart task file.
[3] `playbooks/tests/irods_restart_all.yml` — the test playbook.
[4] `playbooks/tests/tasks/irods/test_running.yml` — the running check.
[5] https://github.com/irods/irods/blob/4.3.1/scripts/irods/controller.py — `irodsctl status` output.
