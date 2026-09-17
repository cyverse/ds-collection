---
type: RuleSet
title: coge.re — CoGe Service Policy
description: Gives the coge user write access to coge_data collections at the top of user home collections and to anything created in or moved into them.
resource: /playbooks/files/irods/etc/irods/coge.re
tags: [irods, rules, coge, service, permissions]
timestamp: 2026-09-17T00:00:00Z
---

`coge.re` supports the CoGe service. CoGe "is given write access to any
collection named `coge_data` in the top level of a user's home collection" and
to any data object placed in such a collection.

## Constants

| Constant | Value |
| --- | --- |
| `_coge_COLL` | `coge_data` |
| `_coge_PERM` | `write` |
| `_coge_USER` | `coge` |

These are hard-coded; there is no `coge-env` template.

## Rules

| Rule | Called from | Behavior |
| --- | --- | --- |
| `coge_acPostProcForCollCreate(*CollPath)` | `acPostProcForCollCreate` | `cyverse_ensureAccessOnCreateColl` — recursive `write` for `coge` on the new collection |
| `coge_acPostProcForObjRename(*SrcEntity, *DestEntity)` | `acPostProcForObjRename` | `cyverse_ensureAccessOnMv` — grants `write` when an entity moves into a `coge_data` collection |
| `coge_dataObjCreated(*User, *Zone, *DataObjInfo)` | `_cyverse_core_dataObjCreated` (steps `START` and `FULL`) | `cyverse_ensureAccessOnCreateDataObj` — `write` on the new data object |

The helper functions in [cyverse.re](/irods-rules/cyverse.md) apply only to
paths matching `/<zone>/home/<user>/coge_data` or below, and skip the `coge`
user's own home and `home/shared`.

## Deployment

Installed by the [irods_cfg role](/ansible-roles/irods-cfg.md) and loaded
through `@include 'coge'` in [cyverse_core.re](/irods-rules/cyverse-core.md).
Nothing in `playbooks/` creates the `coge` user.

## Tests

`playbooks/tests/rules/coge.py` has one test per rule, verifying `coge` gets
access after collection creation, rename, and data object creation.
`playbooks/tests/rules/mocks/coge.re` is a logging stub for testing
`cyverse_core.re`.

# Citations

[1] `playbooks/files/irods/etc/irods/coge.re` — the rules.
[2] `playbooks/files/irods/etc/irods/cyverse.re` — service access helpers.
[3] `playbooks/tests/rules/coge.py` — tests.
[4] `playbooks/tests/rules/mocks/coge.re` — stub.
