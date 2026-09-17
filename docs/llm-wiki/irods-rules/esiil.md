---
type: RuleSet
title: esiil.re and esiil-env.re — ESIIL Project Policy
description: Restricts the ESIIL project resource to data objects in the ESIIL project collection; the root resource name comes from the esiil-env template.
resource: /playbooks/files/irods/etc/irods/esiil.re
tags: [irods, rules, esiil, project, resources]
timestamp: 2026-09-17T00:00:00Z
---

`esiil.re` implements the ESIIL project policy: "Any data object put in an ESIIL
project collection will be stored on the ESIIL resource server, and no other
data objects may be stored there." It includes `esiil-env`.

## Rule

The rule is the same as [avra.re](/irods-rules/avra.md#rule) with `esiil_RESC`
in place of `avra_RESC`: an `on` branch of `pep_resource_resolve_hierarchy_pre`
that uses `cyverse_blockRescReq` from [cyverse.re](/irods-rules/cyverse.md) and
relays its error through
`temporaryStorage.resource_resolve_hierarchy_err` to the catch-all in
[cyverse_core.re](/irods-rules/cyverse-core.md#database-and-resource-peps).
Placement of ESIIL data on the resource is handled by
[cyverse_repl.re](/irods-rules/cyverse-repl.md).

## Environment constant (`esiil-env.re.j2`)

| Constant | Template value | Default |
| --- | --- | --- |
| `esiil_RESC` | `_esiil_resource_hierarchy.name` | `esiil_resource_hierarchy`, else the first entry of `_irods_resource_hierarchies` |

With the default, `esiil_RESC` equals the default resource and the restriction
does nothing.

## Setup

The [esiil_usage playbook](/ansible-playbooks/esiil-usage.md) runs only when
`esiil_base_collection` is set. It follows the same steps as `avra_usage.yml` —
resource hierarchy, base collection, `own` for `_esiil_manager` (default:
`_irods_admin_username`), and a `forced` `ipc::hosted-collection` AVU — but
authenticates with `_irods_admin_username`/`_irods_admin_password` instead of
the clerver credentials.

## Deployment

Installed by the [irods_cfg role](/ansible-roles/irods-cfg.md) and loaded
through `@include 'esiil'` in `cyverse_core.re`.

## Tests

- `playbooks/tests/rules/esiil.py` — 10 test methods in three classes: the ESIIL
  resource equal to the default resource, not equal to it, and operations
  (open, unlink) that don't add a replica.
- `playbooks/tests/rules/esiil-env.py` — checks the deployed `esiil_RESC`.

`playbooks/tests/irods_rule_templates.yml` doesn't check `esiil-env.re.j2`.

# Citations

[1] `playbooks/files/irods/etc/irods/esiil.re` — the rule.
[2] `playbooks/templates/irods/etc/irods/esiil-env.re.j2` — the constant.
[3] `playbooks/group_vars/all/esiil.yml` — ESIIL variable defaults.
[4] `playbooks/esiil_usage.yml` — creates the resource, collection, and AVU.
[5] `playbooks/tests/rules/esiil.py`, `playbooks/tests/rules/esiil-env.py` — tests.
