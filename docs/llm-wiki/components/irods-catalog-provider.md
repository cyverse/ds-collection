---
type: Component
title: iRODS Catalog Service Provider
description: The iRODS servers in the irods_catalog group that own the ICAT connection, run the rule engine and periodic policies, and publish events to AMQP.
resource: /playbooks/irods_catalog_provider.yml
tags: [irods, catalog-provider, icat, rule-engine, amqp]
timestamp: 2026-09-17T00:00:00Z
---

Catalog service providers are the hosts in the `irods_catalog` inventory
group. They connect directly to the ICAT database and, unlike resource
servers, are configured with the `provider` catalog service role. The
collection treats `groups['irods_catalog'][0]` as the zone's primary host: it
is the default `irods_dbms_host`, `irods_re_host`, and
`irods_canonical_hostname`, and the host `proxy.yml` forwards iRODS traffic to.

## Deployment

`irods_catalog_provider.yml` deploys a provider end to end:

1. Imports `irods_provision.yml`, which installs the iRODS server packages
   pinned to `irods_version` (default `4.3.1`) on CentOS or Ubuntu, the netCDF
   and S3 plugins, the service account and group, and `/etc/hosts` entries
   via `irods_hosts.yml`.
2. Provider-only provisioning: kernel sysctls from `irods_sysctl_kernel`, an
   open-file limit of 2000 for the service account, the `pika` Python package,
   a mail client, PostgreSQL 12 clients and ODBC driver, and
   `irods-database-plugin-postgres`.
3. Runs the `irods_cfg` role's `setup_irods.yml` as the service account with
   the database connection, rule bases, port range, federation, and
   `IRODS_AMQP_URI`/`IRODS_DB_*` environment variables, then starts iRODS with
   the `irods_ctl` module and authenticates the clerver with
   `irods_clerver_auth`.
4. Imports `irods_runtime_init.yml` for run-time initialization.

Day-to-day reconfiguration uses `irods_cfg.yml`; see
[Configure iRODS](/ansible-playbooks/irods-cfg.md). Related playbooks:
[irods_runtime_init](/ansible-playbooks/irods-runtime-init.md),
[irods_resource_hierarchies](/ansible-playbooks/irods-resource-hierarchies.md),
[irods_specific_queries](/ansible-playbooks/irods-specific-queries.md), the
project `*_usage.yml` playbooks, and the restart/stop playbooks
([irods_restart_all](/ansible-playbooks/irods-restart-all.md),
[irods_stop_all](/ansible-playbooks/irods-stop-all.md)).

## Run-time initialization

`irods_runtime_init.yml` ensures the `rodsadmin` group and clerver membership,
removes rodsadmin home/trash collections, fixes the `public` group's home,
ensures the CyVerse curated collection and UUIDs on predefined collections,
creates the `anonymous` user with read access to required collections, and
starts the periodic housekeeping rules
(`cyverse_housekeeping_rescheduleQuotaUsageUpdate`,
`cyverse_housekeeping_rescheduleStorageFreeSpaceDetermination`,
`cyverse_housekeeping_rescheduleTrashRemoval`). It also converts any
`ds-service` type users to `rodsuser` directly in the DBMS and removes that
user type.

## Rule logic and command scripts

The rule bases `cve`, `cyverse_core`, and `cyverse_housekeeping` are added to
the rule engine configuration; all static `*.re` files from
`playbooks/files/irods/etc/irods/` and templated `*.re.j2` files from
`playbooks/templates/irods/etc/irods/` are deployed, along with the command
scripts in `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/`. See
[cyverse_core](/irods-rules/cyverse-core.md),
[cve](/irods-rules/cve.md),
[cyverse_housekeeping](/irods-rules/cyverse-housekeeping.md), and
[iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md).

## Key variables

Defaults come from `playbooks/group_vars/all/irods.yml`; the full table is in
`playbooks/README.md`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `irods_version` | `4.3.1` | Package version to install and lock |
| `irods_zone_name` | `tempZone` | Zone name |
| `irods_clerver_user` / `irods_clerver_password` | `rods` / `rods` | Clerver account |
| `irods_dbms_host` / `irods_dbms_port` | first `irods_catalog` host / `5432` | ICAT DBMS connection |
| `irods_db_username` / `irods_db_password` | `irods` / `testpassword` | ICAT DB account |
| `irods_amqp_host`, `irods_amqp_port`, `irods_amqp_vhost` | `localhost`, `5672`, `/` | Event publishing target |
| `irods_server_port_range_start` / `_end` | `20000` / `20199` | Server port range |
| `irods_max_num_re_procs` | `4` | Concurrent delay rule executors |
| `irods_default_resource` | first `irods_resource_hierarchies` name (`demoResc`) | Default resource |
| `irods_federation` | `[]` | Federated zones |
| `irods_host_aliases` | `[]` | Extra local host entries |
| `irods_restart_allowed` | `false` | Whether handlers may restart iRODS |

Internal constants in the same file fix the client/server policy to
`CS_NEG_REFUSE`, the hash scheme to `MD5`, the zone port to `1247`, and the
control plane port to `1248`.

# Citations

[1] `playbooks/irods_catalog_provider.yml` — provider deployment.
[2] `playbooks/irods_provision.yml` — package installation and service account.
[3] `playbooks/irods_runtime_init.yml` — run-time initialization and periodic policies.
[4] `playbooks/group_vars/all/irods.yml` — variable defaults and internal constants.
[5] `playbooks/README.md` — variable documentation.
[6] `roles/irods_cfg/` — configuration file generation.
