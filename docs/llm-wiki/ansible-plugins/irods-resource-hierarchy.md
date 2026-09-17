---
type: Plugin
title: irods_resource_hierarchy Module
description: The cyverse.ds.irods_resource_hierarchy module, which creates missing coordinating resources and attaches child resources to build an iRODS resource hierarchy.
resource: /plugins/modules/irods_resource_hierarchy.py
tags: [plugin, module, irods, resource, hierarchy]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_resource_hierarchy` creates or extends an iRODS resource
hierarchy. It creates any coordinating resources in the requested hierarchy
that don't exist, and attaches children to their parents. It uses
python-irodsclient with a TLS context.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `admin_username` | yes | | rodsadmin user authorizing the change |
| `admin_password` | yes | | Password for `admin_username` (`no_log`) |
| `hierarchy` | yes | | The root `hierarchy` dictionary, described below |
| `host` | no | `localhost.localdomain` | iRODS server |
| `port` | no | `1247` | TCP port |
| `zone` | yes | | Zone containing the hierarchy |

A `hierarchy` dictionary has these fields:

- `name` (required) — the resource name;
- `type` — the resource type. Required when `children` or `context` is given.
  A node without a `type` is treated as a reference to an existing resource;
- `children` — a list of child `hierarchy` dictionaries;
- `context` — the resource's context string.

## Behavior

For each node that has a `type`, the module works top-down:

1. If the resource exists, its type and context must match the request, or the
   module fails.
2. If it doesn't exist, the module creates it with the given type and context
   and sets its status to `up`.
3. It processes each child's subtree, then attaches the child. A child must
   exist, or the module fails with "referenced resource … does not exist". If
   the child already has a different parent, the module fails; if it already
   has this parent, nothing changes.

`changed` is true if any resource was created or attached. `RETURN` is empty.

## Usage

Used by [irods_resource_hierarchies.yml](/ansible-playbooks/irods-resource-hierarchies.md)
and the project playbooks [avra_usage.yml](/ansible-playbooks/avra-usage.md),
[esiil_usage.yml](/ansible-playbooks/esiil-usage.md),
[ncems_usage.yml](/ansible-playbooks/ncems-usage.md), and
[pire_usage.yml](/ansible-playbooks/pire-usage.md).

## Tests

`plugins/modules/tests/irods_resource_hierarchy.yml` checks that the task fails
when `admin_password`, `admin_username`, `hierarchy`, or `zone` is missing.
The checks for missing hierarchy fields, a fully specified call, `up` status,
and the `hierarchy`, `host`, and `port` parameters are TODO placeholders. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

# Citations

[1] `plugins/modules/irods_resource_hierarchy.py` — module source, documentation, and examples.
[2] `plugins/modules/tests/irods_resource_hierarchy.yml` — module test playbook.
