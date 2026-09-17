---
type: Playbook
title: irods_cfg.yml
description: Re-deploys iRODS configuration, rule files, and command scripts to already set up catalog providers and resource servers through the irods_cfg role, and removes retired files.
resource: /playbooks/irods_cfg.yml
tags: [irods, configuration, rules, irods-cfg]
timestamp: 2026-09-17T00:00:00Z
---

`irods_cfg.yml` updates the configuration of iRODS servers that are already
set up. It imports the [irods_cfg role](/ansible-roles/irods-cfg.md)'s
default task file, while the initial deployment playbooks
([irods_catalog_provider.yml](/ansible-playbooks/irods-catalog-provider.md)
and [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md))
use its `setup_irods.yml`.

## Play order

1. **Enable debugging when not testing** (`hosts: all`): sets
   `_test_log: false` in a task tagged `no_testing`. The role plays default
   `irods_cfg_test_log` to `true` when the fact is unset.
2. **TAR slip workaround** (`irods`, `become: true`): makes the service
   account the recursive owner of `/var/lib/irods/msiExecCmd_bin` (tagged
   `non_idempotent`) so the role can update the command scripts. The playbook
   notes this can be removed after upgrading to iRODS 5.1.0.
3. **Configure iRODS** on `irods_catalog` as the service account: imports the
   role as a `provider` with the ICAT database settings and the
   `IRODS_AMQP_URI` and `IRODS_DB_*` environment variables.
4. **Configure iRODS** on `irods_resource:!irods_catalog` as the service
   account: imports the role as a `consumer` with `irods_cfg_database: null`
   and no environment variables. This group includes containerized resource
   servers.
5. **Remove old rule files and command scripts** (`irods`, `become: true`):
   deletes `/etc/irods/ipc-encryption.re` and
   `/var/lib/irods/msiExecCmd_bin/correct-size`, then makes `root` the
   recursive owner of `msiExecCmd_bin` with `go-w,g+rx`, so the service
   account can't modify the command scripts.

Both configure plays deploy static rule bases from
`files/irods/etc/irods/*.re`, templated ones from
`templates/irods/etc/irods/*.re.j2`, and command scripts from
`files/irods/var/lib/irods/msiExecCmd_bin/*`. They add `cve`,
`cyverse_core`, and `cyverse_housekeeping` as additional rule bases. The
role restarts iRODS only when `irods_restart_allowed` (default `false`) is
true.

## Variables

The plays map `_irods_*` values from `playbooks/group_vars/all/irods.yml`
onto `irods_cfg_*` role variables. Notable defaults include
`irods_default_number_of_transfer_threads` (3),
`irods_parallel_transfer_buffer_size` (100),
`irods_server_port_range_start`/`_end` (20000/20199), `irods_max_num_re_procs`
(4), `irods_default_dir_mode`/`_file_mode` (`0750`/`0600`), and
`irods_host_aliases` (`[]`). When there are host aliases, they become a
`local` host entry together with the inventory hostname.

## Tests

`playbooks/tests/irods_cfg.yml` imports `irods_rule_templates.yml`. On all
`irods` hosts it checks that the configuration files and command scripts are
in place, that old files are gone, that `msiExecCmd_bin` isn't owned by
`irods`, and that `irods_environment.json` has the expected contents. It
checks `server_config.json` separately for catalog providers and resource
servers, including a host-specific check for `consumer_configured_ubuntu`.

## Related

- [iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md)
- [irods-rules section](/irods-rules/cyverse-core.md) — start with `cyverse_core`

# Citations

[1] `playbooks/irods_cfg.yml` — the playbook.
[2] `roles/irods_cfg/` — the role it applies.
[3] `playbooks/files/irods/etc/irods/` — static rule files.
[4] `playbooks/templates/irods/etc/irods/` — templated rule files.
[5] `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/` — command scripts.
[6] `playbooks/group_vars/all/irods.yml` — variable defaults.
[7] `playbooks/tests/irods_cfg.yml` — the test playbook.
