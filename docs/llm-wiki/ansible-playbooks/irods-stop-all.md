---
type: Playbook
title: irods_stop_all.yml
description: Stops iRODS on all hosts that have the service account — resource servers first, then catalog providers — recording the result in stop_all_result for a parent playbook.
resource: /playbooks/irods_stop_all.yml
tags: [irods, stop, operations]
timestamp: 2026-09-17T00:00:00Z
---

`irods_stop_all.yml` stops iRODS across the grid in three plays.

## Plays

1. **Check if iRODS service account exists** (`irods`, `become: true`): uses
   `ansible.builtin.user` in check mode to see whether
   `_irods_service_account_name` exists. Hosts that have it are added to the
   dynamic group `has_irods_acnt`. Hosts that don't get
   `stop_all_result: {changed: false}`.
2. **Stop iRODS catalog consumers**
   (`irods_resource:!irods_catalog:&has_irods_acnt`, as the service account):
   [irods_ctl](/ansible-plugins/irods-ctl.md) `state: stopped`, registered as
   `stop_all_result`.
3. **Stop iRODS catalog providers** (`irods_catalog:&has_irods_acnt`, as the
   service account): the same, for providers.

Because the consumer and provider plays run in sequence, resource servers
stop before the catalog providers. A parent playbook can inspect
`stop_all_result` afterward to learn whether each host was running.

## Used by

Imported at the start of
[irods_check_routes.yml](/ansible-playbooks/irods-check-routes.md), which
restarts the hosts whose `stop_all_result` changed.

## Tests

`playbooks/tests/irods_stop_all.yml` checks, on each host that has an
`irods` user, that `/var/lib/irods/irodsctl status` output contains
`No iRODS servers running`.

# Citations

[1] `playbooks/irods_stop_all.yml` — the playbook.
[2] `playbooks/tests/irods_stop_all.yml` — the test playbook.
