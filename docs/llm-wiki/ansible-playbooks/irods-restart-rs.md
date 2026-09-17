---
type: Playbook
title: irods_restart_rs.yml
description: Restarts iRODS on resource servers that aren't catalog providers, leaving catalog providers running.
resource: /playbooks/irods_restart_rs.yml
tags: [irods, restart, resource-server, operations]
timestamp: 2026-09-17T00:00:00Z
---

`irods_restart_rs.yml` targets `irods_resource:!irods_catalog` as the service
account and is tagged `non_idempotent`. It runs a single
[irods_ctl](/ansible-plugins/irods-ctl.md) task with `state: restarted`.

## Tests

`playbooks/tests/irods_restart_rs.yml` imports
`tests/tasks/irods/test_running.yml` on `irods_resource`. See
[irods_restart_all.yml](/ansible-playbooks/irods-restart-all.md) for the
limits of that check.

## Related

- [iRODS Resource Server](/components/irods-resource-server.md)

# Citations

[1] `playbooks/irods_restart_rs.yml` — the playbook.
[2] `playbooks/tests/irods_restart_rs.yml` — the test playbook.
