---
type: Playbook
title: dbms_icat.yml
description: Creates the ICAT database and its iRODS admin user on the primary DBMS, plus the r_transfer_totals table and its unique index.
resource: /playbooks/dbms_icat.yml
tags: [dbms, postgresql, icat, database]
timestamp: 2026-09-17T00:00:00Z
---

`dbms_icat.yml` creates the iRODS catalog database on the PostgreSQL server
built by [dbms.yml](/ansible-playbooks/dbms.md). See
[ICAT DBMS](/components/icat-dbms.md).

## Hosts

One play on `dbms_primary`, `run_once: true`, becoming the `postgres` user.

## What it does

1. Imports the [postgresql_db](/ansible-roles/postgresql-db.md) role to create
   a database named `ICAT` owned by `dbms_irods_username` (default `irods`)
   with password `dbms_irods_password` (required, no default). The hosts in
   `irods_catalog` are passed as the database's client hosts. `dbms_pg_hba`
   and `dbms_port` are passed through.
2. Creates the table `r_transfer_totals` in `ICAT`, owned by the iRODS DB
   user, with columns `user_id BIGINT`, `action VARCHAR(250)`,
   `exbibytes BIGINT`, and `bytes BIGINT`, all `NOT NULL`.
3. Creates a unique index `unique_user_action` on
   `r_transfer_totals (user_id, action)`.

## Testing

`playbooks/tests/dbms_icat.yml` verifies that the `ICAT` database and the
`irods` DB user exist, that the user can connect from the control node, and
that the user holds `CTc` privileges on `ICAT`. Checks for client host access
and for the transfer totals table and index are `TODO implement` placeholders.

# Citations

[1] `playbooks/dbms_icat.yml` — the playbook.
[2] `playbooks/group_vars/all/dbms.yml` — `dbms_irods_username`,
`dbms_irods_password`, `dbms_pg_hba`, and `dbms_port` defaults.
[3] `playbooks/tests/dbms_icat.yml` — its test playbook.
[4] `roles/postgresql_db/README.md` — the role it imports.
