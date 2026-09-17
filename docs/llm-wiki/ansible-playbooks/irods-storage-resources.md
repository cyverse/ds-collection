---
type: Playbook
title: irods_storage_resources.yml
description: Creates vault directories and unixfilesystem storage resources for native resource servers, then initializes each resource's free space.
resource: /playbooks/irods_storage_resources.yml
tags: [irods, storage-resources, vault, unixfilesystem]
timestamp: 2026-09-17T00:00:00Z
---

`irods_storage_resources.yml` creates the storage resources listed in each
native resource server's `irods_storage_resources`.

## Plays

1. **Create vaults** (`irods_resource_native:!unmanaged_systems`,
   `become: true`): creates each item's `vault` directory, following
   symlinks, owned by the service account and group with mode `u=rwx`.
2. **Create storage resources** (`irods_resource_native`, delegated to the
   control node): defines each item as a `unixfilesystem` resource with
   [irods_unixfilesystem_resource](/ansible-plugins/irods-unixfilesystem-resource.md),
   using its `name`, `vault`, and `context`, the host's inventory name, status
   `up`, and the clerver credentials.
3. Imports [irods_free_space.yml](/ansible-playbooks/irods-free-space.md).

## Variables

`irods_storage_resources` (default `[]`) is a list of objects with `name`,
`vault`, and `context`. `playbooks/README.md` documents the item fields.

## Used by

Imported by [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md),
[avra_usage.yml](/ansible-playbooks/avra-usage.md),
[esiil_usage.yml](/ansible-playbooks/esiil-usage.md),
[ncems_usage.yml](/ansible-playbooks/ncems-usage.md), and
[pire_usage.yml](/ansible-playbooks/pire-usage.md).

## Tests

`playbooks/tests/irods_storage_resources.yml` checks that each vault exists as
a directory owned by `irods` with owner rwx. It checks that the set of
`unixfilesystem` resources in the catalog equals every declared storage
resource plus `bundleResc`, that each resource's context matches, and that
its status is `up`. It then imports the free space test.

# Citations

[1] `playbooks/irods_storage_resources.yml` — the playbook.
[2] `playbooks/README.md` — `irods_storage_resources` item fields.
[3] `playbooks/tests/irods_storage_resources.yml` — the test playbook.
