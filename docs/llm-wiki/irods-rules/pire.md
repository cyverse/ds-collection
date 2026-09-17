---
type: RuleSet
title: pire.re and pire-env.re — BH-PIRE and EHT Project Policy
description: Restricts the BH-PIRE resource to data objects in the BH-PIRE and EHT project collections; the root resource name comes from the pire-env template.
resource: /playbooks/files/irods/etc/irods/pire.re
tags: [irods, rules, pire, eht, project, resources]
timestamp: 2026-09-17T00:00:00Z
---

`pire.re` implements the BH-PIRE and EHT project policy: "Any data object put in
the BH-PIRE or EHT project collection will be stored on the BH-PIRE resource
server. No other data objects may be stored there." It includes `pire-env`.

## Rule

The rule is the same as [avra.re](/irods-rules/avra.md#rule) with `pire_RESC`
in place of `avra_RESC`: an `on` branch of `pep_resource_resolve_hierarchy_pre`
that uses `cyverse_blockRescReq` from [cyverse.re](/irods-rules/cyverse.md) and
relays its error to the catch-all in
[cyverse_core.re](/irods-rules/cyverse-core.md#database-and-resource-peps).
Placement of project data on the resource is handled by
[cyverse_repl.re](/irods-rules/cyverse-repl.md).

## Environment constant (`pire-env.re.j2`)

| Constant | Template value | Default |
| --- | --- | --- |
| `pire_RESC` | `_pire_resource_hierarchy.name` | `pire_resource_hierarchy`, else the first entry of `_irods_resource_hierarchies` |

With the default, `pire_RESC` equals the default resource and the restriction
does nothing.

## Setup

The [pire_usage playbook](/ansible-playbooks/pire-usage.md) differs from the
other project playbooks:

- It always creates the PIRE hierarchy, a `pire` group, and
  `/<zone>/home/shared/eht`, and adds an `ipc::hosted-collection` AVU (unit
  `forced`) for that collection to the PIRE resource.
- When `pire_manager` is set, it adds the manager to the `pire` group, creates
  `/<zone>/home/shared/bhpire`, adds a second `ipc::hosted-collection` AVU for
  it, and gives the manager `own`.
- It brings up each child resource of the PIRE hierarchy.

## Deployment

Installed by the [irods_cfg role](/ansible-roles/irods-cfg.md) and loaded
through `@include 'pire'` in `cyverse_core.re`.

## Tests

- `playbooks/tests/rules/pire.py` — 10 test methods in three classes: the PIRE
  resource equal to the default resource, not equal to it, and operations that
  don't add a replica (the last class is named
  `TestPepResourceResolveHierarchyPreNcemsResNoAdd`, though it tests PIRE).
- `playbooks/tests/rules/pire-env.py` — checks the deployed `pire_RESC`.
- `playbooks/tests/irods_rule_templates.yml` — asserts `pire_RESC = 'demoResc'`
  with the default variables.
- `playbooks/tests/rules/mocks/pire.re` — an empty stub that
  `cyverse_repl.py` swaps in to remove this rule.

# Citations

[1] `playbooks/files/irods/etc/irods/pire.re` — the rule.
[2] `playbooks/templates/irods/etc/irods/pire-env.re.j2` — the constant.
[3] `playbooks/group_vars/all/pire.yml` — PIRE variable defaults.
[4] `playbooks/pire_usage.yml` — creates the resource, group, collections, and AVUs.
[5] `playbooks/tests/rules/pire.py`, `playbooks/tests/rules/pire-env.py`, `playbooks/tests/rules/mocks/pire.re` — tests and stub.
[6] `playbooks/tests/irods_rule_templates.yml` — template expansion test.
