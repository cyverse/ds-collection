---
type: RuleSet
title: cyverse_core.re — PEP Switchyard
description: The root CyVerse rule base that includes every other policy file and attaches their logic to iRODS policy enforcement points, including the iRODS issue 8106 memory-leak workaround.
resource: /playbooks/files/irods/etc/irods/cyverse_core.re
tags: [irods, rules, pep, policy, dispatch]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse_core.re` is the rule base that binds CyVerse Data Store policy to iRODS
policy enforcement points (PEPs). Its header says all policy logic is "in this
file or included by this file". It holds almost no policy of its own: each PEP
forwards to rules named `<rulebase>_<pep>` in the included files. The overall
set of deployed rule files, command scripts, and configuration values is
described in [iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md).

## Includes

The file starts by including, in this order:

| Include | Purpose |
| --- | --- |
| [cyverse](/irods-rules/cyverse.md) | shared library, pulls in `cyverse-env` |
| [cyverse_json](/irods-rules/cyverse-json.md) | JSON serialization |
| [cyverse_logic](/irods-rules/cyverse-logic.md) | general policy (UUIDs, AMQP, checksums, protected AVUs) |
| [cyverse_encryption](/irods-rules/cyverse-encryption.md) | encryption enforcement |
| [cyverse_repl](/irods-rules/cyverse-repl.md) | resource residency and replication |
| [cyverse_transfer_tracking](/irods-rules/cyverse-transfer-tracking.md) | transfer volume tracking |
| [cyverse_trash](/irods-rules/cyverse-trash.md) | trash timestamps |
| [avra](/irods-rules/avra.md), [coge](/irods-rules/coge.md), [esiil](/irods-rules/esiil.md), [ncems](/irods-rules/ncems.md), [pire](/irods-rules/pire.md) | service- and project-specific rules |

A comment reserves the last group for service-specific logic: each service gets
its own file, and its rules are prefixed with the file name and suffixed with
the PEP that calls them (e.g. `coge_acPostProcForCollCreate`).

## Dispatch pattern

Most post-processing PEPs call each delegate inside
`errormsg(..., *msg)` and write failures to the server log, so one delegate's
failure doesn't stop the others. Pre-processing PEPs (e.g. the encryption
checks) call the delegate directly so its failure aborts the operation.

## Static PEPs

| PEP | Delegates to |
| --- | --- |
| `acCreateCollByAdmin` | `msiCreateCollByAdmin`, then `cyverse_logic` |
| `acCreateUserZoneCollections` | nothing for `rodsgroup` users |
| `acDataDeletePolicy` | `cyverse_logic` |
| `acDeleteCollByAdminIfPresent` | `cyverse_logic`, then `msiDeleteCollByAdmin` (ignores -808000) |
| `acPreConnect` | `cyverse_logic` (returns `CS_NEG_REFUSE`) |
| `acSetRescSchemeForCreate`, `acSetRescSchemeForRepl` | `cyverse_repl` |
| `acPreProcForModifyAccessControl`, `acPreProcForModifyAVUMetadata` (3 arities), `acPreprocForRmColl` | `cyverse_logic` |
| `acPostProcForCollCreate`, `acPostProcForObjRename` | `cyverse_logic`, `coge` |
| `acPostProcForDataCopyReceived`, `acPostProcForDelete`, `acPostProcForModifyAccessControl`, `acPostProcForModifyAVUMetadata`, `acPostProcForOpen`, `acPostProcForParallelTransferReceived`, `acPostProcForRmColl` | `cyverse_logic` |
| `acPostProcForPut` | `cyverse_logic`, `cyverse_repl`, `cyverse_transfer_tracking`, `cyverse_trash` (see below) |

## Dynamic API PEPs

| PEP | Delegates to |
| --- | --- |
| `pep_api_bulk_data_obj_put_post` | `cyverse_logic`, `cyverse_repl`, `cyverse_transfer_tracking` — only when `cyverse_IS_CATALOG_PROVIDER` |
| `pep_api_bulk_data_obj_reg_post` | logs that it was called (not used by iCommands as of 4.3.1) |
| `pep_api_coll_create_post` | `cyverse_encryption`, `cyverse_trash` |
| `pep_api_data_obj_copy_pre` | `cyverse_encryption` |
| `pep_api_data_obj_copy_post` | `cyverse_logic`, `cyverse_repl`, `cyverse_trash` |
| `pep_api_data_obj_create_pre` | `cyverse_encryption` |
| `pep_api_data_obj_create_post` | `cyverse_logic`, `cyverse_repl`, `cyverse_trash` |
| `pep_api_data_obj_create_and_stat_pre`, `pep_api_data_obj_open_and_stat_pre` | log that they were called |
| `pep_api_data_obj_get_post`, `pep_api_data_obj_read_post` | `cyverse_transfer_tracking` |
| `pep_api_data_obj_open_pre` | `cyverse_encryption` |
| `pep_api_data_obj_open_post`, `pep_api_data_obj_close_post`, `pep_api_replica_open_post`, `pep_api_replica_close_post`, `pep_api_touch_post` | `cyverse_logic`, `cyverse_repl` |
| `pep_api_data_obj_write_post` | `cyverse_logic`, `cyverse_repl`, `cyverse_transfer_tracking` |
| `pep_api_data_obj_rename_pre` | `cyverse_encryption`, `cyverse_trash` |
| `pep_api_data_obj_rename_post` | `cyverse_encryption`, `cyverse_repl`, `cyverse_trash` |
| `pep_api_data_obj_unlink_pre`, `_post`, `_except`; `pep_api_rm_coll_pre`, `_except` | `cyverse_trash` |
| `pep_api_phy_path_reg_post` | `cyverse_logic`, `cyverse_repl` |
| `pep_api_struct_file_ext_and_reg_pre` | nothing; the `cyverse_encryption` call is commented out because the input isn't serialized correctly before iRODS 4.3.2 |

## Database and resource PEPs

Data object creation is detected in the database plugin PEPs rather than the
API PEPs, because of https://github.com/irods/irods/issues/5540:

- `pep_database_reg_data_obj_post` records `CREATE <user> <zone> <DataObjInfo>`
  in `temporaryStorage` under `ipc-data-obj-<path>`, then calls
  `_cyverse_core_dataObjCreated` with step `START` for a zero-byte object or
  `FULL` otherwise.
- `pep_database_mod_data_obj_meta_post` calls `_cyverse_core_dataObjCreated`
  with step `FINISH` when a `START` upload's size is set, and otherwise calls
  `_cyverse_core_dataObjMetadataModified` (which forwards to
  `cyverse_logic_dataObjMetaMod`) for system metadata changes. Per its
  comments, it relies on `*RegParam` serializing to `'0'` to skip calls during
  data modification (issues 5583 and 5584).
- `_cyverse_core_dataObjCreated` calls `cyverse_logic_dataObjCreated` always,
  `coge_dataObjCreated` unless the step is `FINISH`, and
  `cyverse_repl_dataObjCreated` unless the step is `START`.
- `pep_database_close_post` and `pep_database_close_finally` are empty; their
  former bodies are commented out because of issue 5540.

`pep_resource_resolve_hierarchy_pre` is the catch-all for the project rule
files: if an earlier `on` branch stored a message in
`temporaryStorage.resource_resolve_hierarchy_err`, it fails with -32000
(`SYS_INVALID_RESC_INPUT`). The comments explain that errors raised inside an
`on` branch have to be relayed this way because of
https://github.com/irods/irods/issues/6463.

## Issue 8106 workaround

Commit `1631907` works around a memory leak in the `DATA_OBJ_PUT` API PEPs,
https://github.com/irods/irods/issues/8106, which the comments say is fixed in
iRODS 4.3.4 (the collection defaults `irods_version` to 4.3.1):

- `pep_api_data_obj_put_pre` is commented out, so
  `cyverse_encryption_api_data_obj_put_pre` is no longer called for
  `DATA_OBJ_PUT` uploads. The comment says there is no workaround for this PEP.
- `pep_api_data_obj_put_post` is replaced by the static PEP
  `acPostProcForPut`. It rebuilds the inputs the delegates expect from session
  variables: `*Comm.user_user_name`/`user_rods_zone` from `$userNameClient` and
  `$rodsZoneClient`, `*DataObjInp.obj_path` from `$objPath`,
  `*DataObjInp.data_size` from `$dataSize`, and `*DataObjInp.resc_hier` by
  querying `DATA_RESC_HIER` for `$rescName`. `*Instance` and `*DataObjInpBBuf`
  are empty strings. It then calls the same four delegates as before.

`cve.re` disabled its own `pep_api_data_obj_put_pre` in the same commit; see
[cve.re](/irods-rules/cve.md).

## Deployment

`cyverse_core` is the second entry in the rule engine's `re_rulebase_set`,
between `cve` and `cyverse_housekeeping`, followed by `core`. The list is set
through `irods_cfg_re.additional_rulebases` in `irods_catalog_provider.yml`,
`irods_resource_server.yml`, `irods_resource_container.yml`, and `irods_cfg.yml`,
and rendered by `mk_rule_lang_config` in `roles/irods_cfg/templates/macros.j2`,
which appends `core`. The `.re` files themselves are copied to `/etc/irods/` by
the [irods_cfg role](/ansible-roles/irods-cfg.md) from the globs in
`irods_cfg_rulebases_static` and `irods_cfg_rulebases_templated`.
`docs/deployment-artifacts/irods.md` states the three custom rule bases must be
listed in that order and before `core`.

## Tests

`playbooks/tests/rules/cyverse_core.py` (83 test methods, many marked skipped
or not implemented) swaps in stub rule bases from `playbooks/tests/rules/mocks/`
(`cyverse_encryption.re`, `cyverse_logic.re`, `cyverse_repl.re`, and others)
that log when each rule is called, then verifies each PEP calls the expected
delegates. It covers `_cyverse_core_dataObjCreated` for each step, the static
PEPs, and the API PEPs. The `DATA_OBJ_PUT` encryption test is skipped since the
8106 workaround. `mocks/cyverse_core.re` is the stub other test modules (e.g.
`cve.py`, `cyverse_repl.py`) use in place of this file. See
[Testing iRODS Rules](/runbooks/testing-irods-rules.md).

# Citations

[1] `playbooks/files/irods/etc/irods/cyverse_core.re` — the rule base.
[2] `docs/deployment-artifacts/irods.md` — rule base ordering requirement.
[3] `roles/irods_cfg/templates/macros.j2` — `mk_rule_lang_config` builds `re_rulebase_set`.
[4] `playbooks/irods_catalog_provider.yml` — sets `additional_rulebases` and the rule file globs.
[5] `playbooks/irods_resource_server.yml`, `playbooks/irods_resource_container.yml`, `playbooks/irods_cfg.yml` — the same settings for other hosts.
[6] `playbooks/tests/rules/cyverse_core.py` — tests.
[7] `playbooks/tests/rules/mocks/` — stub rule bases.
[8] Commit `1631907` — the issue 8106 hotfix.
[9] https://github.com/irods/irods/issues/8106 — the DATA_OBJ_PUT PEP memory leak.
