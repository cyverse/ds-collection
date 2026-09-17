---
type: Playbook
title: irods_log.yml
description: Installs rsyslog on iRODS hosts, routes iRODS server, delay server, and agent messages to /var/log/irods/irods.log, and configures weekly log rotation.
resource: /playbooks/irods_log.yml
tags: [irods, logging, rsyslog, logrotate]
timestamp: 2026-09-17T00:00:00Z
---

`irods_log.yml` targets `irods` with `become: true`.

## What it does

1. Sets `_enable_notifications: true` (tagged `no_testing`), so the rsyslog
   restart handler doesn't run in the test harness.
2. On Ubuntu, updates the apt cache (tagged `non_idempotent`).
3. Installs `rsyslog`.
4. Writes `/etc/rsyslog.d/00-irods.conf`, which sends messages from programs
   whose names start with `irodsServer`, `irodsDelayServer`, or `irodsAgent`
   to `/var/log/irods/irods.log`, formatted as the bare message, and stops
   further processing. A change notifies `Restart rsyslog`.
5. Renders `templates/irods/etc/logrotate.d/irods.j2` to
   `/etc/logrotate.d/irods`. The log rotates weekly with compression and date
   extensions, and `_irods_log_retention` rotations are kept.

## Variables

| Variable | Default |
| --- | --- |
| `irods_log_retention` | `26` (weeks) |

## Tests

`playbooks/tests/irods_log.yml` exists, but every task is a placeholder
`debug` message reading `TODO: implement`.

## Related

[irods_resource_container.yml](/ansible-playbooks/irods-resource-container.md)
uses the same logrotate template, with a different rsyslog filter for the
container's syslog tag.

# Citations

[1] `playbooks/irods_log.yml` — the playbook.
[2] `playbooks/templates/irods/etc/logrotate.d/irods.j2` — the logrotate template.
[3] `playbooks/tests/irods_log.yml` — the placeholder test playbook.
