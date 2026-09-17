---
type: Playbook
title: esiil_usage.yml
description: Creates the ESIIL project's resource hierarchy and project collection in iRODS and binds the collection to the resource.
resource: /playbooks/esiil_usage.yml
tags: [irods, esiil, project, resource-hierarchy]
timestamp: 2026-09-17T00:00:00Z
---

`esiil_usage.yml` configures iRODS for the ESIIL project. Its rule logic is
described in [ESIIL rules](/irods-rules/esiil.md).

## Plays

1. Imports [irods_storage_resources.yml](/ansible-playbooks/irods-storage-resources.md).
2. **Configure iRODS for ESIIL** on `irods_catalog`, `run_once: true`. Every
   task is delegated to `localhost` and runs only when `esiil_base_collection`
   is not empty. The tasks connect to the first `irods_catalog` host as the
   iRODS admin (`_irods_admin_username` / `_irods_admin_password`):
   1. Creates the resource hierarchy `esiil_resource_hierarchy` with
      [irods_resource_hierarchy](/ansible-plugins/irods-resource-hierarchy.md).
   2. Creates the collection `esiil_base_collection`, with parents, using
      [irods_collection](/ansible-plugins/irods-collection.md).
   3. Gives `esiil_manager` recursive `own` permission on it with
      [irods_permission](/ansible-plugins/irods-permission.md).
   4. Sets the AVU `ipc::hosted-collection` = `esiil_base_collection`, units
      `forced`, on the hierarchy's root resource with
      [irods_avu](/ansible-plugins/irods-avu.md).

## Variables

Defaults from `playbooks/group_vars/all/esiil.yml`:

| Variable | Default |
| --- | --- |
| `esiil_base_collection` | none (the play is skipped when empty) |
| `esiil_manager` | the iRODS admin user |
| `esiil_resource_hierarchy` | the first entry of the iRODS resource hierarchies |

## Testing

`playbooks/tests/esiil_usage.yml` checks, against the testing inventory, that
`esiilRes` is a single unixfilesystem resource, that
`/testing/home/shared/esiil` exists and is owned by `rods`, and that exactly
one `ipc::hosted-collection` AVU with units `forced` is on `esiilRes`.

# Citations

[1] `playbooks/esiil_usage.yml` — the playbook.
[2] `playbooks/group_vars/all/esiil.yml` — ESIIL variable defaults.
[3] `playbooks/tests/esiil_usage.yml` — its test playbook.
[4] `testing/ansible-tester/inventory/group_vars/irods.yml` — test values.
