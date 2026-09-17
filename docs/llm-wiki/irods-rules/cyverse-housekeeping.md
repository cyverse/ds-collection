---
type: RuleSet
title: cyverse_housekeeping.re — Periodic Tasks
description: Delay-queue rules for hourly quota usage updates, daily storage free-space determination, and weekly removal of trash older than 30 days.
resource: /playbooks/files/irods/etc/irods/cyverse_housekeeping.re
tags: [irods, rules, housekeeping, quota, trash, delay-rules]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse_housekeeping.re` is "a library of rules for periodic tasks". It defines
no PEPs. Each task has a worker rule that runs from the iRODS delay queue and a
`reschedule` rule that ensures exactly one delay-queue entry with the right
frequency exists.

## Tasks

| Task | Worker rule | Schedule rule | Frequency |
| --- | --- | --- | --- |
| Quota usage | `cyverse_housekeeping_updateQuotaUsage` calls `msiQuota` | `cyverse_housekeeping_rescheduleQuotaUsageUpdate` | `1h REPEAT FOR EVER` |
| Storage free space | `cyverse_housekeeping_determineAllStorageFreeSpace` runs `msi_update_unixfilesystem_resource_free_space` remotely on the host of every `unixfilesystem` resource whose status is `up` | `cyverse_housekeeping_rescheduleStorageFreeSpaceDetermination` | `1d REPEAT FOR EVER` |
| Trash removal | `cyverse_housekeeping_rmTrash` | `cyverse_housekeeping_rescheduleTrashRemoval` | `7d REPEAT FOR EVER` |

The file header describes user storage usage tracking as "once a day", but the
code schedules it hourly.

`_cyverse_housekeeping_reschedulePeriodicPolicy` looks up delay-queue entries by
rule name. It deletes duplicates or entries with the wrong frequency through
the `delete-scheduled-rule` command script, and schedules a new entry if none
remains. It writes `scheduled <desc>` or `<desc> already scheduled` to stdout.

## Trash removal

`cyverse_housekeeping_rmTrash` computes a cutoff 30 days (2,592,000 seconds)
before now, zero-padded to match iRODS timestamps, then:

1. Unlinks every data object under `/<zone>/trash/` whose `ipc::trash_timestamp`
   is at or before the cutoff, with `irodsAdminRmTrash`.
2. Walks trash collections under `/<zone>/trash/home/` in descending path order,
   so children are removed before parents. A collection is skipped if it still
   contains timestamped data objects or child collections, or if it has no
   timestamp but an ancestor within the user's trash does. Otherwise it is
   removed when its timestamp is missing or at or before the cutoff.
3. Removes `/<zone>/trash/orphan` if it exists.

It then emails `<zone> trash removal succeeded` or `failed` from
`cyverse_EMAIL_FROM_ADDR` to `cyverse_EMAIL_REPORT_ADDR` through the `send-mail`
command script. The timestamps are maintained by
[cyverse_trash.re](/irods-rules/cyverse-trash.md).

## Dependencies

The file has no `@include`. It uses `cyverse_ZONE`, `cyverse_EMAIL_FROM_ADDR`,
and `cyverse_EMAIL_REPORT_ADDR` from `cyverse-env` (see
[cyverse.re](/irods-rules/cyverse.md)), which is loaded through
`cyverse_core`, the rule base listed before it.

## Deployment

`cyverse_housekeeping` is the third entry in `re_rulebase_set`, after `cve` and
`cyverse_core` and before `core`; `playbooks/tests/irods_catalog_provider.yml`
and `playbooks/tests/irods_resource_server.yml` assert that position. The
[irods_runtime_init playbook](/ansible-playbooks/irods-runtime-init.md) runs
the three `reschedule` rules with `irule` as the admin user on the
`irods_catalog` hosts, and reports a change when the rule prints `scheduled ...`.

## Tests

`playbooks/tests/rules/cyverse_housekeeping.py` has 7 test methods, most marked
skipped or not implemented, covering `_cyverse_housekeeping_schedulePeriodicPolicy`
and the shared rules. `playbooks/tests/irods_runtime_init.yml` checks that the
three worker rules appear in `iqstat -u rods` output.

# Citations

[1] `playbooks/files/irods/etc/irods/cyverse_housekeeping.re` — the rules.
[2] `playbooks/irods_runtime_init.yml` — schedules the periodic tasks.
[3] `playbooks/tests/irods_runtime_init.yml` — verifies the delay queue.
[4] `playbooks/tests/rules/cyverse_housekeeping.py` — rule tests.
[5] `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/delete-scheduled-rule`, `send-mail` — command scripts used.
