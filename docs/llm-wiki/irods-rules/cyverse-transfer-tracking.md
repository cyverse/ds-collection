---
type: RuleSet
title: cyverse_transfer_tracking.re — Transfer Volume Tracking
description: Records per-user upload and download byte counts in the ICAT's r_transfer_totals table through the add-transfer command script.
resource: /playbooks/files/irods/etc/irods/cyverse_transfer_tracking.re
tags: [irods, rules, transfer-tracking, icat]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse_transfer_tracking.re` "contains the iRODS transfer tracking logic
prototype created by RENCI". It adds the size of each transfer to a running
total per user and direction (`in` for uploads, `out` for downloads).

## Rules called from cyverse_core.re

| Rule | Direction | Volume recorded |
| --- | --- | --- |
| `cyverse_transfer_tracking_api_bulk_data_obj_put_post` | in | Sum of `data_size_*` entries in the bulk request |
| `cyverse_transfer_tracking_api_data_obj_put_post` | in | `data_size` of the upload |
| `cyverse_transfer_tracking_api_data_obj_write_post` | in | `len` of the write |
| `cyverse_transfer_tracking_api_data_obj_get_post` | out | `data_size` of the download |
| `cyverse_transfer_tracking_api_data_obj_read_post` | out | `len` of the read |

The bulk rule guards against iRODS rule language integer overflow
(max 2147483647): sizes over nine digits are recorded as separate transfers, and
the running total is flushed before it would overflow. `cyverse_core.re` only
calls it on the catalog provider (`cyverse_IS_CATALOG_PROVIDER`). The put rule
is reached through `acPostProcForPut` since the iRODS issue 8106 workaround.

## Recording

`_cyverse_transfer_tracking_addTransfer` skips the `anonymous` user and users
whose type isn't `rodsuser`. For others it looks up the user ID and runs the
`add-transfer` command script with the ID, direction, and volume. The script
connects to PostgreSQL using the `IRODS_DB_HOST`, `IRODS_DB_PORT`,
`IRODS_DB_USERNAME`, and `IRODS_DB_PASSWORD` environment variables and upserts
into `r_transfer_totals(user_id, action, exbibytes, bytes)`, carrying overflow
past 2^60 bytes into `exbibytes`. A failure is logged and fails the rule, which
`cyverse_core.re` logs.

The table and its unique `(user_id, action)` index are created by the
[dbms_icat playbook](/ansible-playbooks/dbms-icat.md).

## Dependencies

No other CyVerse rules. Included by
[cyverse_core.re](/irods-rules/cyverse-core.md).

## Tests

`playbooks/tests/rules/cyverse_transfer_tracking.py` has 13 test methods, about
half marked skipped or not implemented, covering `addTransfer` success and
failure and the public rules. `playbooks/tests/rules/mocks/add-transfer` stubs
the command script, and `mocks/cyverse_transfer_tracking.re` stubs the rule base
for `cyverse_core.re` tests.

# Citations

[1] `playbooks/files/irods/etc/irods/cyverse_transfer_tracking.re` — the rules.
[2] `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/add-transfer` — the upsert script.
[3] `playbooks/dbms_icat.yml` — creates `r_transfer_totals`.
[4] `playbooks/tests/rules/cyverse_transfer_tracking.py` — tests.
[5] `playbooks/tests/rules/mocks/add-transfer`, `playbooks/tests/rules/mocks/cyverse_transfer_tracking.re` — stubs.
