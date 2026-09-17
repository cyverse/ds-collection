---
type: RuleSet
title: cyverse_encryption.re — Encryption Enforcement
description: Rejects unencrypted data objects in collections marked encryption::required and propagates that marker to subcollections.
resource: /playbooks/files/irods/etc/irods/cyverse_encryption.re
tags: [irods, rules, encryption, avu, policy]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse_encryption.re` implements CyVerse's opt-in encryption policy. A user
sets the AVU `encryption::required` = `true` on a collection. Afterwards, any
data object created in it, or in a collection under it, must have a name ending
in `.enc`, the extension GoCommands uses when it encrypts a file. Violations call
`failmsg(-815000, 'CYVERSE ERROR:  attempt to create unencrypted data object')`
after `cut`. In iRODS 4.3.1 a failure after `cut` makes the rule return
`CUT_ACTION_PROCESSED_ERR` (-1089000) instead, which is what the tests expect.

## Rules called from cyverse_core.re

| Rule | Behavior |
| --- | --- |
| `cyverse_encryption_api_coll_create_post` | Copies `encryption::required` and any `encryption::mode` from the parent to the new collection and its subcollections |
| `cyverse_encryption_api_data_obj_create_pre` | Checks the new object's name |
| `cyverse_encryption_api_data_obj_open_pre` | Checks the opened object's name |
| `cyverse_encryption_api_data_obj_put_pre` | Checks the uploaded object's name (**not currently called**, see below) |
| `cyverse_encryption_api_data_obj_copy_pre` | Checks the destination name |
| `cyverse_encryption_api_data_obj_rename_pre` | For a data object (`src_opr_type` 11), checks the destination name; for a collection (12), fails if any data object in the source doesn't end in `.enc` |
| `cyverse_encryption_api_data_obj_rename_post` | For a moved collection, copies the parent's encryption AVUs onto it and its subcollections |
| `cyverse_encryption_api_struct_file_ext_and_reg_pre` | Rejects extracting a bundle into a collection that requires encryption (**not currently called**) |

Whether encryption is required is read only from the immediate parent
collection (`_cyverse_encryption_required`); inheritance works because the
AVUs are copied down on creation and move.

`cyverse_core.re` doesn't call two of these rules:

- `pep_api_data_obj_put_pre` in `cyverse_core.re` was commented out by the
  workaround for https://github.com/irods/irods/issues/8106, so
  `DATA_OBJ_PUT` uploads aren't checked.
- The call from `pep_api_struct_file_ext_and_reg_pre` is commented out because
  its input isn't serialized correctly before iRODS 4.3.2.

## Dependencies

Uses `cyverse_endsWith` and `cyverse_COLL` from
[cyverse.re](/irods-rules/cyverse.md). Included by
[cyverse_core.re](/irods-rules/cyverse-core.md).

## Tests

`playbooks/tests/rules/cyverse_encryption.py` has 40 test methods, one class per
public rule and private helper, including collection and data object renames,
`encryption::mode` propagation, and bundle rejection.
`playbooks/tests/rules/mocks/cyverse_encryption.re` is a logging stub used when
testing `cyverse_core.re`.

# Citations

[1] `playbooks/files/irods/etc/irods/cyverse_encryption.re` — the policy.
[2] `playbooks/files/irods/etc/irods/cyverse_core.re` — PEPs that call it.
[3] `playbooks/tests/rules/cyverse_encryption.py` — tests.
[4] `playbooks/tests/rules/mocks/cyverse_encryption.re` — stub.
[5] https://github.com/irods/irods/blob/4.3.1/plugins/rule_engines/irods_rule_language/src/arithmetics.cpp — `evaluateActions` returns `CUT_ACTION_PROCESSED_ERR` for a failure after `cut`.
[6] https://github.com/irods/irods/blob/4.3.1/lib/core/include/irods/rodsErrorTable.h — `CUT_ACTION_PROCESSED_ERR` is -1089000.
