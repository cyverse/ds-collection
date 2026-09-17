---
type: Playbook
title: irods_free_space.yml
description: Updates each storage resource's free_space value in the iRODS catalog to match the space actually available on its vault file system.
resource: /playbooks/irods_free_space.yml
tags: [irods, storage-resources, free-space]
timestamp: 2026-09-17T00:00:00Z
---

`irods_free_space.yml` targets `irods_resource`. For each item in
`_irods_storage_resources`, it includes `tasks/irods/set_resc_free_space.yml`
with `resource_name` and `vault_path` set.

## What the task file does

1. On the control node, runs `iinit` as the clerver against the resource
   server and reads `RESC_FREE_SPACE` for the resource with `iquest`. It
   fails if the resource doesn't exist.
2. On the resource server, reads available bytes for the vault from
   `df --portability --block-size 1`.
3. If the two differ, runs `iadmin modresc <resource> free_space <bytes>`
   from the control node. This task is tagged `non_idempotent`, because other
   agents change file system usage between runs.

## Used by

Imported at the end of
[irods_storage_resources.yml](/ansible-playbooks/irods-storage-resources.md).

## Tests

`playbooks/tests/irods_free_space.yml` checks on localhost that
`RESC_FREE_SPACE` is non-empty for the test environment's resources `avra`,
`esiilRes`, `ingestRes`, `ncemsRes`, `pire`, and `replRes`.

# Citations

[1] `playbooks/irods_free_space.yml` — the playbook.
[2] `playbooks/tasks/irods/set_resc_free_space.yml` — the task file.
[3] `playbooks/tests/irods_free_space.yml` — the test playbook.
