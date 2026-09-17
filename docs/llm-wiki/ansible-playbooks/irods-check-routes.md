---
type: Playbook
title: irods_check_routes.yml
description: Verifies network reachability of the iRODS zone, control plane, and ephemeral ports between catalog providers and resource servers, stopping iRODS during the check and restarting it afterward.
resource: /playbooks/irods_check_routes.yml
tags: [irods, networking, ports, diagnostics, operations]
timestamp: 2026-09-17T00:00:00Z
---

`irods_check_routes.yml` checks that the ports iRODS needs are reachable
between hosts. It stops iRODS so that a test listener can bind to those ports.
Every play except the final restart play is tagged `non_idempotent`; that
play's restart task carries the tag instead.

## Play order

1. Imports [irods_stop_all.yml](/ansible-playbooks/irods-stop-all.md).
2. **Start receivers** (`irods`): waits for connections on the zone port to
   drain, then starts
   [port_check_receiver](/ansible-plugins/port-check-receiver.md)
   asynchronously (up to 600 s). It listens on TCP for the zone port, control
   plane port, and ephemeral range, and on UDP for the ephemeral range.
3. **Check ports from catalog service providers** (`irods_catalog`,
   `serial: 1`): uses
   [port_check_sender](/ansible-plugins/port-check-sender.md) to test the
   host's own control plane port, other providers' control plane ports, and
   each resource server's zone and control plane ports.
4. **Check port access from resource servers** (`irods_resource`,
   `serial: 1`): tests each catalog provider's zone port, and the zone port
   plus the full TCP and UDP ephemeral range of each other resource server.
5. **Stop receivers** (`irods`): sends `finished` to each receiver's zone
   port, waits for the async job, and reports a receiver failure message if
   there is one.
6. **Restart previously stopped iRODS servers** (`irods`, as the service
   account): runs `tasks/irods/restart.yml` with `restart_op: always` on hosts
   whose `stop_all_result` changed.

The port check and failure-report tasks set `ignore_errors: true`, so an
unreachable port shows as a failed task without aborting the run.

## Variables

| Variable | Default |
| --- | --- |
| `irods_check_routes_timeout` | `3` (seconds per port check) |
| `irods_server_port_range_start` / `_end` | `20000` / `20199` |

The timeout isn't passed to the providers' own and other-provider control
plane checks, which use the `port_check_sender` default of 4 seconds. The
zone port (1247) and control plane port (1248) are constants in
`playbooks/group_vars/all/irods.yml`.

## Tests

There is no `playbooks/tests/irods_check_routes.yml`.

# Citations

[1] `playbooks/irods_check_routes.yml` — the playbook.
[2] `playbooks/tasks/irods/restart.yml` — the restart task file.
[3] `playbooks/group_vars/all/irods.yml` — variable defaults.
