---
type: Playbook
title: dbms.yml
description: Tunes the DBMS hosts' boot parameters and installs and configures PostgreSQL on the primary and replica DBMS hosts using the postgresql role.
resource: /playbooks/dbms.yml
tags: [dbms, postgresql, replication, icat]
timestamp: 2026-09-17T00:00:00Z
---

`dbms.yml` builds the PostgreSQL servers that host the ICAT database. See
[ICAT DBMS](/components/icat-dbms.md). The database itself is created by
[dbms_icat.yml](/ansible-playbooks/dbms-icat.md).

## Plays

1. **Prepare for PostgreSQL** (`dbms`) — applies the Galaxy role
   `adfinis_sygroup.grub` to add `transparent_hugepage=never` to the kernel
   command line, with no consoles and a zero boot timeout. Tagged `no_testing`.
2. **Set up primary DBMS** (`dbms_primary`) — applies the
   [postgresql](/ansible-roles/postgresql.md) role and passes the
   `dbms_replicas` group as `postgresql_downstream_nodes`.
3. **Set up replica DBMSs** (`dbms_replicas`) — applies the same role with the
   first `dbms_primary` host as `postgresql_upstream_node`, and sets
   `postgresql_destroy_default_db_on_init` from `dbms_replication_start`.

## Derived settings

Both PostgreSQL plays compute some settings from host facts:

- `shared_buffers` is a quarter of `memtotal_mb`.
- `effective_cache_size` is `dbms_effective_cache_size` if set, otherwise
  `memtotal_mb // 2048` GB.
- `max_worker_processes` and `max_parallel_workers` are
  `dbms_max_worker_processes` if set, otherwise the processor count.
- `huge_pages` is `on` when `dbms_mem_num_huge_pages` is greater than zero.
- `wal_buffers` is fixed at `16MB` and `standard_conforming_strings` at `off`.
- The listen addresses include all of the host's IPv4 addresses.

## Variables

Defaults from `playbooks/group_vars/all/dbms.yml`:

| Variable | Default |
| --- | --- |
| `dbms_port` | `5432` |
| `dbms_pg_hba` | `/etc/postgresql/12/main/pg_hba.conf` |
| `dbms_max_connections` | `500` |
| `dbms_work_mem` (MB) | `32` |
| `dbms_maintenance_work_mem` (GB) | `2` |
| `dbms_effective_io_concurrency` | `200` |
| `dbms_random_page_cost` | `1.1` |
| `dbms_checkpoint_timeout` (min) | `15` |
| `dbms_checkpoint_completion_target` | `0.9` |
| `dbms_max_wal_size` / `dbms_min_wal_size` (GB) | `8` / `2` |
| `dbms_wal_keep_segments` | `4000` |
| `dbms_mem_num_huge_pages` | `60000` |
| `dbms_max_parallel_workers_per_gather` | `2` |
| `dbms_max_parallel_maintenance_workers` | `2` |
| `dbms_log_line_prefix` | `< %m %r >` |
| `dbms_log_min_duration` (ms) | `1000` |
| `dbms_replication_username` | `postgres` |
| `dbms_replication_password` | none |
| `dbms_replication_start` | `false` |
| `dbms_restart_allowed` / `dbms_reboot_allowed` | `false` / `false` |

`dbms_max_wal_senders` (default `120`) is defined in the defaults file but not
passed to the role by this playbook.

## Testing

`playbooks/tests/dbms.yml` checks the postgresql role's `cyverse.conf.j2` and
`pgpass.j2` templates render correctly with role defaults and with the
overrides in `playbooks/tests/group_vars/dbms/solo_node.yml`, and checks that
the `postgresql`, `postgresql-client`, and `python3-psycopg2` packages and the
`en_US.UTF-8` locale exist on the `dbms` hosts. Many of its tasks, including
the checks of the primary and replica plays, are `TODO implement` placeholders.

# Citations

[1] `playbooks/dbms.yml` — the playbook.
[2] `playbooks/group_vars/all/dbms.yml` — DBMS variable defaults.
[3] `playbooks/tests/dbms.yml` — its test playbook.
[4] `roles/postgresql/` — the role it applies.
