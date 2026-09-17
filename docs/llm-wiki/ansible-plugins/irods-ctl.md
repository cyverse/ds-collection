---
type: Plugin
title: irods_ctl Module
description: The cyverse.ds.irods_ctl module, which starts, stops, restarts, or conditionally restarts the iRODS server processes with /var/lib/irods/irodsctl, optionally enabling test-mode logging.
resource: /plugins/modules/irods_ctl.py
tags: [plugin, module, irods, service-control]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_ctl` changes the state of the iRODS server processes by
running `/var/lib/irods/irodsctl` in a shell. It decides whether iRODS is
running by checking that `irodsctl status` output doesn't contain "No iRODS
servers running".

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `state` | no | `started` | `started`, `stopped`, `restarted`, or `restarted_if_running` |
| `test_log` | no | `false` | Pass `--test` so server log messages also go to `/var/lib/irods/log/test_mode_output.log`; not applied when stopping |

## State semantics

| State | Action | `changed` |
| --- | --- | --- |
| `started` | Starts iRODS if it isn't running | true only if it started it |
| `stopped` | Stops iRODS if it's running | true only if it stopped it |
| `restarted` | Restarts if running, otherwise starts | always true |
| `restarted_if_running` | Restarts only if running; if the status check itself fails, does nothing | true only if it restarted |

If an `irodsctl` call fails, the module fails with "iRODS server failed to
<state>". The result echoes the module `params`.

## Usage

- The `Restart iRODS` handler of the [irods_cfg role](/ansible-roles/irods-cfg.md)
  (`restarted_if_running`).
- `playbooks/tasks/irods/restart.yml`.
- [irods_catalog_provider.yml](/ansible-playbooks/irods-catalog-provider.md),
  [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md),
  [irods_restart_rs.yml](/ansible-playbooks/irods-restart-rs.md), and
  [irods_stop_all.yml](/ansible-playbooks/irods-stop-all.md).

## Tests

`plugins/modules/tests/irods_ctl.yml` stops the service and then checks each
transition:

- `restarted` on a stopped server, with and without `test_log`;
- `restarted_if_running` on a stopped server, confirming it stays stopped;
- `started` without a test log;
- `restarted` on a running server, with and without `test_log`;
- `restarted_if_running` on a running server, with and without `test_log`.

Each step checks whether the server is running and whether the test log file
exists. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

# Citations

[1] `plugins/modules/irods_ctl.py` — module source and documentation.
[2] `plugins/modules/tests/irods_ctl.yml` — module test playbook.
[3] `roles/irods_cfg/handlers/main.yml` — the handler that calls the module.
