---
type: RuleSet
title: cyverse_repl.re — Resource Residency and Replication
description: Chooses the resource for a data object's primary replica from ipc::hosted-collection AVUs, and schedules asynchronous replication, replica moves, and replica syncs on the delay queue.
resource: /playbooks/files/irods/etc/irods/cyverse_repl.re
tags: [irods, rules, replication, resources, delay-rules]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse_repl.re` implements where a data object's primary replica lives and
where it is asynchronously replicated. The header says that by default primary
replicas go to `CyVerseRes` and are replicated to `taccRes`; in the code those
are the environment constants `cyverse_DEFAULT_RESC` and
`cyverse_DEFAULT_REPL_RESC` (see [cyverse.re](/irods-rules/cyverse.md)).

## Policy AVUs

Both AVUs are attached to resources, and their unit is `forced` or `preferred`
(a user may override `preferred`):

- `ipc::hosted-collection <COLL>` — data objects under `COLL` have their primary
  replica on this resource. If several match, the longest `COLL` wins.
- `ipc::replica-resource <REPL-RESC>` — this resource's contents are
  asynchronously replicated to `REPL-RESC`. When the resource is
  `cyverse_DEFAULT_RESC`, `cyverse_DEFAULT_REPL_RESC` is used instead.

The project usage playbooks create `ipc::hosted-collection` AVUs; see
[avra.re](/irods-rules/avra.md), [esiil.re](/irods-rules/esiil.md),
[ncems.re](/irods-rules/ncems.md), and [pire.re](/irods-rules/pire.md).

## Resource selection

- `cyverse_repl_acSetRescSchemeForCreate` calls
  `msiSetDefaultResc(<resource>, <forced|preferred>)` using
  `_repl_findResc`, which defaults to `cyverse_DEFAULT_RESC` and `preferred`.
- `cyverse_repl_acSetRescSchemeForRepl` does the same with the replica resource
  from `_repl_findReplResc`, unless a deferred replication has set
  `temporaryStorage.cyverse_repl_replicate` to `REPL_FORCED_REPL_RESC`.
- `pep_resource_resolve_hierarchy_pre` has an `on` branch with an empty body
  that matches when `cyverse_repl_replicate` is `REPL_FORCED_REPL_RESC`.

## Deferred work

All three deferred rules are scheduled with
`delay('<PLUSET>Ns</PLUSET><EF>8h REPEAT UNTIL SUCCESS</EF>')`. `N` starts at
`cyverse_INIT_REPL_DELAY` and increases by one second for each rule scheduled in
the same session. `cyverse_registerAction` ensures only one replication action
is scheduled per data object per session.

| Deferred rule | Scheduled by | Action |
| --- | --- | --- |
| `cyverse_repl_replicate(DataId, Resc)` | `_repl_scheduleRepl` | Runs `irepl-exec -M -B -R <resc> <path>`. An already-replicated object (`SYS_NOT_ALLOWED`) or checksum mismatch is logged without retrying; other failures retry in 8 hours. |
| `cyverse_repl_mvReplicas(DataId, Ingest, Repl)` | `_repl_scheduleMv` | Replicates to the ingest and replica resources if missing, then trims replicas on any other resource. |
| `cyverse_repl_syncReplicas(DataId)` | `_repl_scheduleSyncReplicas` | Runs `irepl-exec -M -a -U <path>` to update stale replicas. |

The comments explain that `irepl` is run through the `irepl-exec` command script
instead of `msiDataObjRepl` because, as of iRODS 4.3.1, ticket information
isn't passed to deferred rules. A deleted object is logged and treated as
success.

`_ipcRepl_createOrOverwrite(Path, DestRescHier, New)` is the common entry
point. For a new object it schedules replication to the replica resource, or to
the ingest resource if the object landed on the replica resource. For an
overwrite it schedules a sync when any replica is stale
(`DATA_REPL_STATUS` 0).

## Rules called from cyverse_core.re

| Rule | Behavior |
| --- | --- |
| `cyverse_repl_dataObjCreated` | New object → `_ipcRepl_createOrOverwrite` |
| `cyverse_repl_api_bulk_data_obj_put_post` | Each `logical_path_*` → new |
| `cyverse_repl_api_data_obj_put_post`, `_copy_post` | New if `openType` is create, else overwrite |
| `cyverse_repl_api_phy_path_reg_post` | New unless `regRepl` is set |
| `cyverse_repl_api_touch_post` | Parses the JSON input with [cyverse_json.re](/irods-rules/cyverse-json.md); treats the object as new unless `no_create`, `replica_number`, or `leaf_resource_name` is given |
| `cyverse_repl_api_data_obj_create_post`, `_open_post`, `_write_post` | Record path, hierarchy, and created/modified state in `temporaryStorage` |
| `cyverse_repl_api_data_obj_close_post` | Uses the recorded state to call `_ipcRepl_createOrOverwrite` |
| `cyverse_repl_api_replica_open_post`, `_close_post` | Same pattern for `istream`-style replica open/close |
| `cyverse_repl_api_data_obj_rename_post` | If the source and destination map to different ingest resources, schedules `mvReplicas` for the object or every object in the moved collection |

`cyverse_repl_api_data_obj_put_post` is reached through `acPostProcForPut`
since the iRODS issue 8106 workaround; see
[cyverse_core.re](/irods-rules/cyverse-core.md#issue-8106-workaround).

## Dependencies

Uses [cyverse.re](/irods-rules/cyverse.md) helpers and constants, and
[cyverse_json.re](/irods-rules/cyverse-json.md) for the touch input. Included by
[cyverse_core.re](/irods-rules/cyverse-core.md).

## Tests

`playbooks/tests/rules/cyverse_repl.py` has 48 test methods covering replicate,
move, and sync success and failure paths (using the failing
`mocks/irepl-exec`), delay time and scheduling, `_repl_findResc` and
`_repl_findReplResc`, `_ipcRepl_createOrOverwrite`, the resource scheme rules,
`cyverse_repl_dataObjCreated`, and `pep_resource_resolve_hierarchy_pre`. The
dynamic API PEP test class is marked `@test_rules.unimplemented`. Some tests
replace `pire.re` with the empty `mocks/pire.re` and `cyverse_core.re` with
`mocks/cyverse_core.re`. `mocks/cyverse_repl.re` stubs this file for
`cyverse_core.re` tests.

# Citations

[1] `playbooks/files/irods/etc/irods/cyverse_repl.re` — the rules.
[2] `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/irepl-exec` — command script wrapping `irepl`.
[3] `playbooks/tests/rules/cyverse_repl.py` — tests.
[4] `playbooks/tests/rules/mocks/irepl-exec`, `mocks/pire.re`, `mocks/cyverse_core.re`, `mocks/cyverse_repl.re` — stubs.
[5] `docs/deployment-artifacts/irods.md` — storage policy description.
