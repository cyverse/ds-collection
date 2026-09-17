---
type: Role
title: postgresql Role
description: The cyverse.ds.postgresql role, which installs PostgreSQL from apt, applies CyVerse tuning through a conf.d file, and sets up streaming replication between a primary and its replicas.
resource: /roles/postgresql/tasks/main.yml
tags: [role, postgresql, dbms, replication, icat]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.postgresql` installs and tunes the PostgreSQL server that hosts the
ICAT database. The role has no README. `playbooks/dbms.yml` applies it twice:
to the `dbms_primary` group, with `postgresql_downstream_nodes` set to the
`dbms_replicas` group, and to the `dbms_replicas` group. See
[dbms.yml](/ansible-playbooks/dbms.md) and [ICAT DBMS](/components/icat-dbms.md).

## Task flow

`tasks/main.yml` runs these steps in order:

1. Sets `_notifications_enabled` (tagged `no_testing`), which every handler
   requires before it will act.
2. `variables.yml` — when an upstream node or downstream nodes are configured,
   asserts that `postgresql_replication_username` and
   `postgresql_replication_password` are defined.
3. `install.yml` — installs `postgresql`, `postgresql-client`, and
   `python3-psycopg2` with apt, and generates the `en_US.UTF-8` locale.
4. `configure.yml`:
   - sets `vm.nr_hugepages` (notifies `Reboot`) and `vm.swappiness=5` (both
     tagged `no_testing`);
   - gives `postgres` ownership of `/var/lib/postgresql`;
   - creates `<db_path>/archive` and `<conf_path>/conf.d`;
   - templates `conf.d/cyverse.conf` (notifies `Restart postgres`);
   - adds `pg_hba.conf` replication entries (md5) for the upstream and
     downstream nodes (notifies `Reload postgres`);
   - templates `/var/lib/postgresql/.pgpass` when replication is configured.
5. Flushes handlers.
6. `replication.yml`:
   - creates the replication user with the `replication` attribute when there
     are downstream nodes;
   - when `postgresql_upstream_node` is set **and**
     `postgresql_destroy_default_db_on_init` is true, stops
     `postgresql@12-main`, deletes the data directory, runs `pg_basebackup`
     from the upstream node, creates `standby.signal`, and starts the service
     again.

## cyverse.conf

`templates/cyverse.conf.j2` sets:

- listen addresses and port, and `max_connections`;
- memory, parallel worker, WAL, checkpoint, and planner settings;
- `log_min_duration_statement` and `log_line_prefix`;
- `shared_preload_libraries = 'pg_stat_statements'`, with
  `pg_stat_statements.max = 10000` and `track = all`;
- `max_wal_senders` and `wal_keep_segments`, only when there are downstream
  nodes;
- `hot_standby = on` and `hot_standby_feedback`, only when there is an upstream
  node.

The parallel-worker settings are capped at the lower of
`postgresql_max_parallel_workers` and `postgresql_max_worker_processes`.

## Key variables

| Variable | Default |
| --- | --- |
| `postgresql_conf_path` | `/etc/postgresql/12/main` |
| `postgresql_db_path` | `/var/lib/postgresql/12/main` |
| `postgresql_pg_hba` | `/etc/postgresql/12/main/pg_hba.conf` |
| `postgresql_listen_port` | `5432` |
| `postgresql_extra_listen_addresses` | `[]` (localhost is always included) |
| `postgresql_max_connections` | `100` |
| `postgresql_shared_buffers` / `postgresql_effective_cache_size` | `128MB` / `4GB` |
| `postgresql_huge_pages` / `postgresql_num_huge_pages` | `try` / `0` |
| `postgresql_upstream_node` / `postgresql_downstream_nodes` | `null` / `[]` |
| `postgresql_destroy_default_db_on_init` | `false` |
| `postgresql_restart_allowed` / `postgresql_reboot_allowed` | `false` / `false` |

`defaults/main.yml` also holds the checkpoint, WAL, worker, logging, and
planner tuning defaults. The replication username and password have no
defaults.

## Handlers

- `Reload postgres` reloads the service.
- `Restart postgres` runs only if `postgresql_restart_allowed` is true.
- `Reboot` runs only if both `postgresql_restart_allowed` and
  `postgresql_reboot_allowed` are true.

When a restart or reboot is skipped, the
[warn_if_false](/ansible-plugins/warn-if-false.md) test prints a warning.

## Testing

`molecule/postgresql` converges the role on an Ubuntu 20.04 container. Its
`verify.yml` only checks that `cyverse.conf` is marked Ansible managed and
renders `listen_addresses = 'localhost'` by default; the rest are TODO
placeholders. `playbooks/tests/dbms.yml` also renders `cyverse.conf.j2` and
`pgpass.j2` against default and custom variables. See
[Testing Roles with Molecule](/runbooks/testing-roles-with-molecule.md) and
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

# Citations

[1] `roles/postgresql/tasks/` — `main.yml`, `variables.yml`, `install.yml`, `configure.yml`, and `replication.yml`.
[2] `roles/postgresql/templates/cyverse.conf.j2` — the PostgreSQL tuning template.
[3] `roles/postgresql/templates/pgpass.j2` — the replication `.pgpass` template.
[4] `roles/postgresql/defaults/main.yml` — defaults.
[5] `roles/postgresql/handlers/main.yml` — handlers.
[6] `molecule/postgresql/` — the molecule scenario.
[7] `playbooks/dbms.yml` — the playbook that applies the role.
[8] `playbooks/tests/dbms.yml` — template expansion tests.
