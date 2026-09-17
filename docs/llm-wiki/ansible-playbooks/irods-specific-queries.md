---
type: Playbook
title: irods_specific_queries.yml
description: Registers the SQL files in files/irods/specific-queries/ as iRODS specific queries, using each file name as the query alias.
resource: /playbooks/irods_specific_queries.yml
tags: [irods, specific-queries, sql, catalog]
timestamp: 2026-09-17T00:00:00Z
---

`irods_specific_queries.yml` targets `irods_catalog` with `run_once: true`
and runs as the service account.

## What it does

It collects `files/irods/specific-queries/*.sql` and uses each file's base
name without extension as its alias. For each file, it checks
`iquest --sql ls` for the alias and runs `iadmin asq '<sql>' '<alias>'` only
when the alias isn't registered. Changing the SQL of an already registered
alias doesn't re-register it.

The 16 queries are all prefixed `IPC`:

- `IPCCountCollectionsUnderPath`, `IPCCountDataObjectsAndCollections`,
  `IPCCountDataObjectsUnderPath`
- `IPCEntryListing{Created,LastMod,Name,Path,Size}Sort{ASC,DESC}`
- `IPCListCollectionsUnderPath`
- `IPCUserCollectionPerms`, `IPCUserDataObjectPerms`

## Tests

`playbooks/tests/irods_specific_queries.yml` verifies that all 16 aliases
appear in `iquest --sql ls`.

## Related

- [iRODS Catalog Provider](/components/irods-catalog-provider.md)

# Citations

[1] `playbooks/irods_specific_queries.yml` — the playbook.
[2] `playbooks/files/irods/specific-queries/` — the SQL files.
[3] `playbooks/tests/irods_specific_queries.yml` — the test playbook.
