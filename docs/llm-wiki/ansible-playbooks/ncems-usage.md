---
type: Playbook
title: ncems_usage.yml
description: Creates the NCEMS project's resource hierarchy and project collection in iRODS and binds the collection to the resource with units required.
resource: /playbooks/ncems_usage.yml
tags: [irods, ncems, project, resource-hierarchy]
timestamp: 2026-09-17T00:00:00Z
---

`ncems_usage.yml` configures iRODS for the NCEMS project. Its rule logic is
described in [NCEMS rules](/irods-rules/ncems.md).

## Plays

1. Imports [irods_storage_resources.yml](/ansible-playbooks/irods-storage-resources.md).
2. **Configure iRODS for NCEMS** on `irods_catalog`, `run_once: true`. Every
   task is delegated to `localhost` and runs only when `ncems_base_collection`
   is not empty. The tasks connect to the first `irods_catalog` host as the
   iRODS admin:
   1. Creates the resource hierarchy `ncems_resource_hierarchy` with
      [irods_resource_hierarchy](/ansible-plugins/irods-resource-hierarchy.md).
   2. Creates the collection `ncems_base_collection`, with parents, using
      [irods_collection](/ansible-plugins/irods-collection.md).
   3. Gives `ncems_manager` recursive `own` permission on it with
      [irods_permission](/ansible-plugins/irods-permission.md).
   4. Sets the AVU `ipc::hosted-collection` = `ncems_base_collection` on the
      hierarchy's root resource with [irods_avu](/ansible-plugins/irods-avu.md).
      Unlike the Avra, ESIIL, and PIRE playbooks, the units are `required`, not
      `forced`.

In the hierarchy task, `admin_password` is set to `_irods_admin_username`
rather than `_irods_admin_password`; the other tasks use the password.

## Variables

Defaults from `playbooks/group_vars/all/ncems.yml`:

| Variable | Default |
| --- | --- |
| `ncems_base_collection` | none (the configuration tasks are skipped) |
| `ncems_manager` | the iRODS admin user |
| `ncems_resource_hierarchy` | the first entry of the iRODS resource hierarchies |

## Testing

`playbooks/tests/ncems_usage.yml` checks, against the testing inventory, that
`ncemsRes` is a single unixfilesystem resource, that
`/testing/home/shared/ncems` exists and is owned by `rods`, and that exactly
one `ipc::hosted-collection` AVU with units `required` is on `ncemsRes`.

# Citations

[1] `playbooks/ncems_usage.yml` — the playbook.
[2] `playbooks/group_vars/all/ncems.yml` — NCEMS variable defaults.
[3] `playbooks/tests/ncems_usage.yml` — its test playbook.
[4] `testing/ansible-tester/inventory/group_vars/irods.yml` — test values.
