---
type: Component
title: ICAT DBMS
description: The PostgreSQL 12 primary and streaming replicas that host the iRODS ICAT database, including the custom r_transfer_totals table.
resource: /playbooks/dbms.yml
tags: [postgresql, dbms, icat, replication]
timestamp: 2026-09-17T00:00:00Z
---

The ICAT database lives on PostgreSQL servers in the `dbms` inventory group,
split into `dbms_primary` and `dbms_replicas`. The `postgresql` role installs the
`postgresql` and `postgresql-client` packages with apt; its replication tasks
use the `postgresql@12-main` service and the default `pg_hba.conf` path is
`/etc/postgresql/12/main/pg_hba.conf`, so version 12 is assumed.

## Deployment

`dbms.yml` has three plays:

1. On all `dbms` hosts, the `adfinis_sygroup.grub` role adds
   `transparent_hugepage=never` to the kernel command line (tagged
   `no_testing`).
2. On `dbms_primary`, the `cyverse.ds.postgresql` role configures the server
   with the tuning variables below, listens on all IPv4 addresses, and lists
   `dbms_replicas` as downstream nodes.
3. On `dbms_replicas`, the same role points at the first primary as the
   upstream node. When `dbms_replication_start` is true, the role stops the
   replica, empties its data directory, copies the primary, and starts it as
   a standby.

Derived settings: `shared_buffers` is a quarter of host memory,
`effective_cache_size` defaults to half of memory, `max_worker_processes` and
`max_parallel_workers` default to the processor count, and huge pages are on
when `dbms_mem_num_huge_pages` is greater than zero.

`dbms_icat.yml` runs once on the primary as `postgres`. It uses the
`postgresql_db` role to create the `ICAT` database owned by
`dbms_irods_username`, allowing connections from the `irods_catalog` hosts,
then creates the `r_transfer_totals` table (`user_id`, `action`, `exbibytes`,
`bytes`) with a unique index on `user_id, action`. The iRODS command script
`add-transfer` writes to that table; see
[iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md).

`irods_runtime_init.yml` also runs a play on `dbms_primary` that changes
`ds-service` type iRODS users to `rodsuser` directly in the database.

## Key variables

Defaults come from `playbooks/group_vars/all/dbms.yml`; the full table is in
`playbooks/README.md`. Memory sizes are in the units the playbook appends.

| Variable | Default | Purpose |
| --- | --- | --- |
| `dbms_irods_username` / `dbms_irods_password` | `irods` / required | ICAT owner account |
| `dbms_port` | `5432` | Listen port |
| `dbms_pg_hba` | `/etc/postgresql/12/main/pg_hba.conf` | Client auth file |
| `dbms_max_connections` | `500` | Connection limit |
| `dbms_work_mem` | `32` (MB) | Per-operation memory |
| `dbms_maintenance_work_mem` | `2` (GB) | Maintenance memory |
| `dbms_min_wal_size` / `dbms_max_wal_size` | `2` / `8` (GB) | WAL sizing |
| `dbms_wal_keep_segments` | `4000` | WAL segments kept for replicas |
| `dbms_mem_num_huge_pages` | `60000` | Huge pages to reserve |
| `dbms_replication_username` / `_password` | `postgres` / none | Replication account |
| `dbms_replication_start` | `false` | Re-seed replicas from the primary |
| `dbms_restart_allowed` / `dbms_reboot_allowed` | `false` / `false` | Whether handlers may restart or reboot |

# Citations

[1] `playbooks/dbms.yml` — primary and replica configuration.
[2] `playbooks/dbms_icat.yml` — ICAT database and transfer totals table.
[3] `playbooks/group_vars/all/dbms.yml` — variable defaults.
[4] `roles/postgresql/` — installation, configuration, and replication tasks.
[5] `roles/postgresql_db/README.md` — database creation role.
[6] `playbooks/README.md` — variable documentation.
