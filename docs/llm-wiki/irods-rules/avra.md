---
type: RuleSet
title: avra.re and avra-env.re — AVRA Project Policy
description: Restricts the AVRA project resource to data objects in the AVRA project collection; the root resource name comes from the avra-env template.
resource: /playbooks/files/irods/etc/irods/avra.re
tags: [irods, rules, avra, project, resources]
timestamp: 2026-09-17T00:00:00Z
---

`avra.re` implements the AVRA project policy: "Any data object put in the AVRA
project collection will be stored on the AVRA resource server, and no other data
objects may be stored there." It includes `avra-env`.

## Rule

`avra.re` defines one PEP, an `on` branch of
`pep_resource_resolve_hierarchy_pre`. When
`cyverse_blockRescReq(*Op, avra_RESC, *Context.resc_hier, *Context.logical_path)`
is true, it stores `CYVERSE ERROR: <op> on <path> not allowed on <avra_RESC>.`
in `temporaryStorage.resource_resolve_hierarchy_err` and fails. The catch-all
version in [cyverse_core.re](/irods-rules/cyverse-core.md#database-and-resource-peps)
then fails with -32000. The comments say the error is relayed this way because
of https://github.com/irods/irods/issues/6463.

`cyverse_blockRescReq` (in [cyverse.re](/irods-rules/cyverse.md)) blocks an
operation other than `OPEN` or `UNLINK` whose requested hierarchy's root is the
AVRA resource, unless the path is under an `ipc::hosted-collection` value on
that resource. It never blocks when `avra_RESC` equals `cyverse_DEFAULT_RESC`.
Getting AVRA data *onto* the AVRA resource is handled by
[cyverse_repl.re](/irods-rules/cyverse-repl.md), which reads the same AVU.

## Environment constant (`avra-env.re.j2`)

| Constant | Template value | Default |
| --- | --- | --- |
| `avra_RESC` | `_avra_resource_hierarchy.name` | `avra_resource_hierarchy`, else the first entry of `_irods_resource_hierarchies` |

Because the default is the first resource hierarchy, which is also the default
for `cyverse_DEFAULT_RESC`, the restriction does nothing unless `avra_RESC` and
`cyverse_DEFAULT_RESC` name different resources.

## Setup

The [avra_usage playbook](/ansible-playbooks/avra-usage.md) runs only when
`avra_base_collection` is set. It creates the AVRA resource hierarchy and the
base collection, gives `_avra_manager` (default: the clerver user) `own`
permission recursively, and sets `ipc::hosted-collection` =
`<avra_base_collection>` with unit `forced` on the AVRA resource.

## Deployment

`avra.re` and the rendered `avra-env.re` are installed by the
[irods_cfg role](/ansible-roles/irods-cfg.md) with the other rule files, and
loaded through `@include 'avra'` in `cyverse_core.re`.

## Tests

- `playbooks/tests/rules/avra.py` — 5 test methods for
  `pep_resource_resolve_hierarchy_pre`; 3 are skipped as not implemented.
- `playbooks/tests/rules/avra-env.py` — a single class marked
  `@test_rules.unimplemented`.
- `playbooks/tests/irods_rule_templates.yml` — asserts
  `avra_RESC = 'demoResc'` with the default variables.

# Citations

[1] `playbooks/files/irods/etc/irods/avra.re` — the rule.
[2] `playbooks/templates/irods/etc/irods/avra-env.re.j2` — the constant.
[3] `playbooks/group_vars/all/avra.yml` — AVRA variable defaults.
[4] `playbooks/avra_usage.yml` — creates the resource, collection, and AVU.
[5] `playbooks/tests/rules/avra.py`, `playbooks/tests/rules/avra-env.py` — tests.
[6] `playbooks/tests/irods_rule_templates.yml` — template expansion test.
