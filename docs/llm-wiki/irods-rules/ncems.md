---
type: RuleSet
title: ncems.re and ncems-env.re — NCEMS Project Policy
description: Restricts the NCEMS project resource to data objects in the NCEMS project collection; the root resource name comes from the ncems-env template.
resource: /playbooks/files/irods/etc/irods/ncems.re
tags: [irods, rules, ncems, project, resources]
timestamp: 2026-09-17T00:00:00Z
---

`ncems.re` implements the NCEMS project policy: "Any data object put in the
NCEMS project collection will be stored on the NCEMS resource server, and no
other data objects may be stored there." It includes `ncems-env`.

## Rule

The rule is the same as [avra.re](/irods-rules/avra.md#rule) with `ncems_RESC`
in place of `avra_RESC`: an `on` branch of `pep_resource_resolve_hierarchy_pre`
that uses `cyverse_blockRescReq` from [cyverse.re](/irods-rules/cyverse.md) and
relays its error to the catch-all in
[cyverse_core.re](/irods-rules/cyverse-core.md#database-and-resource-peps).
Placement of NCEMS data on the resource is handled by
[cyverse_repl.re](/irods-rules/cyverse-repl.md).

## Environment constant (`ncems-env.re.j2`)

| Constant | Template value | Default |
| --- | --- | --- |
| `ncems_RESC` | `_ncems_resource_hierarchy.name` | `ncems_resource_hierarchy`, else the first entry of `_irods_resource_hierarchies` |

With the default, `ncems_RESC` equals the default resource and the restriction
does nothing.

## Setup

The [ncems_usage playbook](/ansible-playbooks/ncems-usage.md) runs only when
`ncems_base_collection` is set, and follows the same steps as
`esiil_usage.yml` with two differences in the current file:

- The `ipc::hosted-collection` AVU is set with unit `required`.
  [cyverse_repl.re](/irods-rules/cyverse-repl.md) documents only `forced` and
  `preferred` as units.
- The resource hierarchy task passes `_irods_admin_username` as
  `admin_password`, where the other tasks pass `_irods_admin_password`.

## Deployment

Installed by the [irods_cfg role](/ansible-roles/irods-cfg.md) and loaded
through `@include 'ncems'` in `cyverse_core.re`.

## Tests

- `playbooks/tests/rules/ncems.py` — 10 test methods in three classes: the NCEMS
  resource equal to the default resource, not equal to it, and operations that
  don't add a replica.
- `playbooks/tests/rules/ncems-env.py` — checks the deployed `ncems_RESC`.

`playbooks/tests/irods_rule_templates.yml` also asserts `ncems_RESC = 'ncemsRes'`
when `ncems_resource_hierarchy` is set to `{name: ncemsRes}`.

The `setUp` of `TestPepResourceResolveHierarchyPreNcemsResDefault` copies
`/etc/irods/ncems-env.re` to the local `/tmp` and then runs
`sed --in-place 's/ncems_RESC = .*/ncems_RESC = cyverse_DEFAULT_RESC/'` over
SSH with no file argument, so neither the server's `ncems-env.re` nor the local
copy is edited before the rules are reloaded.

# Citations

[1] `playbooks/files/irods/etc/irods/ncems.re` — the rule.
[2] `playbooks/templates/irods/etc/irods/ncems-env.re.j2` — the constant.
[3] `playbooks/group_vars/all/ncems.yml` — NCEMS variable defaults.
[4] `playbooks/ncems_usage.yml` — creates the resource, collection, and AVU.
[5] `playbooks/tests/rules/ncems.py`, `playbooks/tests/rules/ncems-env.py` — tests.
[6] `playbooks/tests/irods_rule_templates.yml` — template expansion test.
