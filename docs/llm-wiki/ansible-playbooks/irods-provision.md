---
type: Playbook
title: irods_provision.yml
description: Installs the iRODS server packages pinned to the configured version on native CentOS and Ubuntu iRODS hosts, creates the service account, and refreshes /etc/hosts.
resource: /playbooks/irods_provision.yml
tags: [irods, provisioning, packages, centos, ubuntu]
timestamp: 2026-09-17T00:00:00Z
---

`irods_provision.yml` prepares a host to run iRODS but doesn't configure the
server. It targets `irods:!irods_resource_container:!unmanaged_systems`, so
containerized resource servers (see
[irods_resource_container.yml](/ansible-playbooks/irods-resource-container.md))
and unmanaged hosts are skipped. It runs with `become: true`.

## What it does

The package steps branch on `ansible_distribution`.

- **CentOS**: installs the iRODS signing key and the
  `renci-irods.yum.repo` repository, forces `yum updateinfo` to import the
  key, removes `yum versionlock` entries for `irods-*` packages whose
  version differs from `_irods_version`, adds version locks for
  `irods-*-<version>`, `irods-netcdf-*-<version>.*`, and
  `irods-resource-*-<version>.*`, then installs
  `irods-server-<version>` and `uuidd`. The lock step shells out to
  `yum versionlock add` because `community.general.yum_versionlock`
  won't lock packages that aren't installed yet; that task is tagged
  `skip_ansible_lint`.
- **Ubuntu**: installs the signing key and an apt source for
  `packages.irods.org/apt/ <codename>`, updates the apt cache (tagged
  `non_idempotent`), pins `irods-*` and `irods-resource-*` to
  `_irods_version` with priority 1001 in `/etc/apt/preferences.d/irods`,
  and installs `irods-server`, `debianutils`, and `uuid-runtime`.

On both, it then:

1. Installs `irods-netcdf-client_modules`, `irods-netcdf-icommands`,
   `irods-netcdf-server_modules`, and `irods-resource-plugin-s3`. A change
   notifies the `Restart iRODS if needed` handler, which runs
   `tasks/irods/restart.yml` with `restart_op: if running` only when
   `_irods_restart_allowed` is true.
2. Enables the `irods` service on boot.
3. Creates the system group `_irods_service_group_name` and the system user
   `_irods_service_account_name` (home `/var/lib/irods`, shell
   `/bin/bash`, member of `tty`, comment `iRODS Administrator`).
4. Runs `tasks/irods/ensure_irods_ownership.yml`, which recursively sets
   the service account and group as owner of `/var/lib/irods` and
   `/etc/irods`.

Finally it imports [irods_hosts.yml](/ansible-playbooks/irods-hosts.md).

## Variables

From `playbooks/group_vars/all/irods.yml`:

| Variable | Default |
| --- | --- |
| `irods_version` (`_irods_version`) | `4.3.1` |
| `irods_service_account_name` | `irods` |
| `irods_service_group_name` | the service account name |
| `irods_restart_allowed` | `false` |

## Used by

[irods_catalog_provider.yml](/ansible-playbooks/irods-catalog-provider.md)
and [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md)
both import this playbook first.

## Tests

`playbooks/tests/irods_provision.yml` checks, per distribution, the signing
key, the repository, the version locks or apt pins, and the installed
packages; that `irods-server` and `irods-resource-plugin-s3` are installed;
that the service group and user exist with the expected comment and `tty`
membership; and that `irods` owns `/etc/irods` and `/var/lib/irods`.

## Related

- [iRODS Catalog Provider](/components/irods-catalog-provider.md)
- [iRODS Resource Server](/components/irods-resource-server.md)

# Citations

[1] `playbooks/irods_provision.yml` — the playbook.
[2] `playbooks/tasks/irods/ensure_irods_ownership.yml` — ownership tasks.
[3] `playbooks/tasks/irods/restart.yml` — the restart handler's tasks.
[4] `playbooks/group_vars/all/irods.yml` — variable defaults.
[5] `playbooks/tests/irods_provision.yml` — the test playbook.
