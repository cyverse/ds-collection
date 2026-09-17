---
type: Playbook
title: pire_usage.yml
description: Creates the BH-PIRE/EHT resource hierarchy, the pire group, and the eht and bhpire shared collections in iRODS, binding the collections to the resource.
resource: /playbooks/pire_usage.yml
tags: [irods, pire, eht, project, resource-hierarchy]
timestamp: 2026-09-17T00:00:00Z
---

`pire_usage.yml` configures iRODS for the BH-PIRE project and its public EHT
collection. Its rule logic is described in [PIRE rules](/irods-rules/pire.md).

## Plays

1. Imports [irods_storage_resources.yml](/ansible-playbooks/irods-storage-resources.md).
2. **Configure iRODS for PIRE** on `irods_catalog`, `run_once: true`, all tasks
   delegated to `localhost` and run as the clerver user against the first
   `irods_catalog` host:
   1. Creates the resource hierarchy `pire_resource_hierarchy`.
   2. Creates the iRODS group `pire` with
      [irods_group](/ansible-plugins/irods-group.md).
   3. Adds `pire_manager` to the group with
      [irods_group_member](/ansible-plugins/irods-group-member.md), if set.
   4. Creates `/<zone>/home/shared/eht` and adds the AVU
      `ipc::hosted-collection` with units `forced` on the hierarchy's root.
   5. If `pire_manager` is set, creates `/<zone>/home/shared/bhpire`, adds the
      same AVU for it, and gives the manager `own` permission on it.
   6. Brings each child of the hierarchy up with
      [irods_resource_up](/ansible-plugins/irods-resource-up.md).

Unlike the Avra, ESIIL, and NCEMS playbooks, the hosted-collection AVUs use
`state: add`, not `state: set`, because the resource hosts two collections.

## Variables

Defaults from `playbooks/group_vars/all/pire.yml`:

| Variable | Default |
| --- | --- |
| `pire_manager` | none (manager-dependent steps are skipped) |
| `pire_resource_hierarchy` | the first entry of the iRODS resource hierarchies |

## Testing

`playbooks/tests/pire_usage.yml` checks, against the testing inventory, that
`pireRes` is a passthru over the `pire` unixfilesystem resource, that the
`pire` group exists and contains `pire_mgr`, that both collections exist and
carry `forced` hosted-collection AVUs on `pireRes`, that `pire_mgr` owns
`bhpire`, and that `pire` and `pireRes` both have status `up`.

# Citations

[1] `playbooks/pire_usage.yml` — the playbook.
[2] `playbooks/group_vars/all/pire.yml` — PIRE variable defaults.
[3] `playbooks/tests/pire_usage.yml` — its test playbook.
