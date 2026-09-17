---
type: RuleSet
title: cyverse_trash.re — Trash Timestamps
description: Maintains the ipc::trash_timestamp AVU on collections and data objects as they enter, leave, or are created in trash, so housekeeping can purge old trash.
resource: /playbooks/files/irods/etc/irods/cyverse_trash.re
tags: [irods, rules, trash, avu]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse_trash.re` gives anything put into trash an `ipc::trash_timestamp` AVU
whose value is the iRODS timestamp (seconds since the epoch) when it entered
trash, and removes the AVU from anything moved out. When a collection is
trashed, only the collection gets the AVU, not its contents. The weekly purge in
[cyverse_housekeeping.re](/irods-rules/cyverse-housekeeping.md) reads these
AVUs.

AVUs are set and removed through `_cyverse_trash_manageTimeAVU`, which runs the
`imeta-exec` command script. The attribute starts with `ipc`, a prefix
[cyverse_logic.re](/irods-rules/cyverse-logic.md) reserves for `rodsadmin`
users.

## Rules called from cyverse_core.re

| Rule | Behavior |
| --- | --- |
| `cyverse_trash_api_data_obj_unlink_pre` | Without `forceFlag`, sets the timestamp on the object and records the timestamp and data ID in `temporaryStorage` |
| `cyverse_trash_api_data_obj_unlink_post` | Looks up the trashed object's collection by its recorded data ID and sets a timestamp on the collection formed from that path's first five components — per the comment, for "any newly created collections in trash" |
| `cyverse_trash_api_data_obj_unlink_except` | Removes the timestamp set in `pre` if the unlink failed |
| `cyverse_trash_api_rm_coll_pre` / `_except` | Without `forceFlag`, sets the timestamp on the collection; removes it on failure |
| `cyverse_trash_api_coll_create_post` | Timestamps a collection created under `/<zone>/trash/` |
| `cyverse_trash_api_data_obj_create_post`, `_put_post`, `_copy_post` | Timestamp a data object created, uploaded, or copied under `/<zone>/trash/` |
| `cyverse_trash_api_data_obj_rename_pre` | When moving out of trash, records the existing timestamp in `temporaryStorage` |
| `cyverse_trash_api_data_obj_rename_post` | Moving into trash sets a timestamp; moving out removes it, and for a collection also removes timestamps from everything inside |

`cyverse_trash_api_data_obj_put_post` is reached through `acPostProcForPut`
since the iRODS issue 8106 workaround; see
[cyverse_core.re](/irods-rules/cyverse-core.md#issue-8106-workaround).

## Dependencies

Uses `cyverse_ZONE`, `cyverse_COLL`, `cyverse_DATA_OBJ`, `cyverse_isColl`,
`cyverse_isDataObj`, and `cyverse_getEntityType` from
[cyverse.re](/irods-rules/cyverse.md). Included by
[cyverse_core.re](/irods-rules/cyverse-core.md).

## Tests

`playbooks/tests/rules/cyverse_trash.py` has 24 test methods covering
`_cyverse_trash_manageTimeAVU`, the variable-name functions, and each API rule,
including unlink success and failure and rename into and out of trash.
`playbooks/tests/rules/mocks/cyverse_trash.re` is a logging stub for testing
`cyverse_core.re`.

# Citations

[1] `playbooks/files/irods/etc/irods/cyverse_trash.re` — the rules.
[2] `playbooks/files/irods/etc/irods/cyverse_housekeeping.re` — consumer of the timestamps.
[3] `playbooks/tests/rules/cyverse_trash.py` — tests.
[4] `playbooks/tests/rules/mocks/cyverse_trash.re` — stub.
[5] `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/imeta-exec` — command script used to edit AVUs.
