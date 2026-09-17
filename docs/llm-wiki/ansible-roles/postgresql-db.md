---
type: Role
title: postgresql_db Role
description: The cyverse.ds.postgresql_db role, which ensures a PostgreSQL database and its admin user exist and grants client hosts md5 access in pg_hba.conf.
resource: /roles/postgresql_db/README.md
tags: [role, postgresql, dbms, icat]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.postgresql_db` ensures a database exists within a PostgreSQL DBMS
and assumes the database has an admin user. `playbooks/dbms_icat.yml` imports it
to create the `ICAT` database on the primary DBMS; see
[dbms_icat.yml](/ansible-playbooks/dbms-icat.md) and
[ICAT DBMS](/components/icat-dbms.md).

## Tasks

`tasks/main.yml` runs three tasks:

1. `community.postgresql.postgresql_db` ensures the database exists on
   `postgresql_db_dbms_port`.
2. `community.postgresql.postgresql_user` ensures the admin user exists with
   the given password and `all` privileges on the database. This task is
   `no_log`.
3. `community.postgresql.postgresql_pg_hba` adds a `host` entry with `md5` auth
   for each client host, allowing the admin user to reach the database. Host
   names are resolved with `dig`. A change notifies the `Reload` handler, which
   reloads `postgresql`.

## Variables

| Variable | Required | Default | Comment |
| --- | --- | --- | --- |
| `postgresql_db_admin_password` | yes | | Password for the admin user |
| `postgresql_db_admin_username` | no | `postgres` | Admin account for the database |
| `postgresql_db_client_hosts` | no | `[]` | Host names or IPs of services connecting as the admin user |
| `postgresql_db_dbms_pg_hba` | no | `/etc/postgresql/12/main/pg_hba.conf` | Path to the service's `pg_hba.conf` |
| `postgresql_db_dbms_port` | no | `5432` | Port the DBMS listens on |
| `postgresql_db_name` | no | `postgres` | Database name |

The role has no dependencies.

## Molecule scenario

`molecule/postgresql_db` uses an Ubuntu 20.04 image with PostgreSQL 12 running
in the foreground as `postgres`. It creates database `db` with admin `username`
and client host `1.1.1.1`. `verify.yml` checks that:

- the database exists;
- the admin user exists;
- the admin user has `CTc` privileges on the database;
- `pg_hba.conf` contains the expected md5 host line.

The password check is a TODO placeholder. See
[Testing Roles with Molecule](/runbooks/testing-roles-with-molecule.md).

# Citations

[1] `roles/postgresql_db/README.md` — role description, variables, and example.
[2] `roles/postgresql_db/tasks/main.yml` — the role's tasks.
[3] `roles/postgresql_db/defaults/main.yml` and `roles/postgresql_db/handlers/main.yml` — defaults and the reload handler.
[4] `molecule/postgresql_db/` — the molecule scenario.
[5] `playbooks/dbms_icat.yml` — the playbook that imports the role.
