---
type: Playbook
title: avra_usage.yml
description: Creates the Avra project's resource hierarchy and project collection in iRODS and binds the collection to the resource.
resource: /playbooks/avra_usage.yml
tags: [irods, avra, project, resource-hierarchy]
timestamp: 2026-09-17T00:00:00Z
---

`avra_usage.yml` configures iRODS for the Avra project. Its rule logic is
described in [Avra rules](/irods-rules/avra.md).

## Plays

1. Imports [irods_storage_resources.yml](/ansible-playbooks/irods-storage-resources.md).
2. **Configure iRODS for Avra** on `irods_catalog`, `run_once: true`. Every
   task is delegated to `localhost` and runs only when `avra_base_collection`
   is not empty. The tasks connect to the first `irods_catalog` host as the
   clerver user (`_irods_clerver_user` / `_irods_clerver_password`):
   1. Creates the resource hierarchy `avra_resource_hierarchy` with
      [irods_resource_hierarchy](/ansible-plugins/irods-resource-hierarchy.md).
   2. Creates the collection `avra_base_collection`, with parents, using
      [irods_collection](/ansible-plugins/irods-collection.md).
   3. Gives `avra_manager` recursive `own` permission on it with
      [irods_permission](/ansible-plugins/irods-permission.md).
   4. Sets the AVU `ipc::hosted-collection` = `avra_base_collection`, units
      `forced`, on the hierarchy's root resource with
      [irods_avu](/ansible-plugins/irods-avu.md).

## Variables

Defaults from `playbooks/group_vars/all/avra.yml`:

| Variable | Default |
| --- | --- |
| `avra_base_collection` | none (the play is skipped when empty) |
| `avra_manager` | the clerver user |
| `avra_resource_hierarchy` | the first entry of the iRODS resource hierarchies |

## Testing

`playbooks/tests/avra_usage.yml` uses the testing inventory values
(`avraRes` passthru over `avra` unixfilesystem, collection
`/testing/home/shared/avra`, manager `avra_mgr`). It checks the hierarchy shape
with `ilsresc`, that the collection exists and `avra_mgr` owns it, and that
exactly one `ipc::hosted-collection` AVU with units `forced` is on `avraRes`.

# Citations

[1] `playbooks/avra_usage.yml` — the playbook.
[2] `playbooks/group_vars/all/avra.yml` — Avra variable defaults.
[3] `playbooks/tests/avra_usage.yml` — its test playbook.
[4] `testing/ansible-tester/inventory/group_vars/irods.yml` — test values.
