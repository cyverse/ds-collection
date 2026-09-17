---
type: RuleSet
title: cve.re — iRODS CVE Workarounds
description: Rules that block or neuter iRODS APIs and microservices with known security holes until the Data Store upgrades past the iRODS versions that fix them.
resource: /playbooks/files/irods/etc/irods/cve.re
tags: [irods, rules, security, cve]
timestamp: 2026-09-17T00:00:00Z
---

`cve.re` "contains workarounds [for] CVEs". Each rule overrides a microservice
or attaches to an API pre-processing PEP to block an exploitable operation, and
its comment names the iRODS version after which it can be removed. The
collection's default iRODS version is 4.3.1 (`_irods_version` in
`playbooks/group_vars/all/irods.yml`). It doesn't include or call any other
CyVerse rule file.

## Workarounds

| Rule | What it does | Removable after |
| --- | --- | --- |
| `msiSendMail` | Replaces the microservice with a log line (CVE-2024-38462, issues 7651 and 7562). | 4.3.2 |
| `msiServerMonPerf` | Replaces the microservice with a log line (CVE-2024-38461, issue 7652). | 4.3.3 |
| `msiTarFileExtract` | Logs and fails with -169000 (`SYS_NOT_ALLOWED`) to prevent tar slip. | 5.1.0 |
| `pep_api_bulk_data_obj_reg_pre` | Blocks `rcBulkDataObjReg` for everyone, failing with -169000 (its header comment lists -31000). | 5.1.0 |
| `pep_api_data_obj_copy_pre` | Fails with -31000 when the copy request carries a destination physical path (`icp -p`). | 4.3.5 |
| `pep_api_data_obj_put_pre` | **Disabled** — see below. | 4.3.5 |
| `pep_api_data_obj_unlink_pre` | Fails with -818000 unless one of the client's groups has at least `delete_object` (`_cve_DEL_VAL` = 1130) on the data object. Prevents `irm -f` by a reader deleting physical files (issue 8441). | 4.3.5 |
| `pep_api_exec_rule_expression_pre` | Fails with -169000 unless the proxy user is a `rodsadmin`. | 5.1.0 |
| `pep_api_reg_data_obj_pre` | Fails with -169000 unless the proxy user is a `rodsadmin`. | 5.1.0 |
| `pep_api_sub_struct_file_get_pre` | Blocks getting subfiles, failing with -169000. | 5.1.0 |
| `pep_api_sub_struct_file_put_pre` | Blocks putting subfiles, failing with -169000. | 5.1.0 |

The copy and unlink rules use `on (...)` conditions with `cut`, so when they
don't match, the same-named PEP in
[cyverse_core.re](/irods-rules/cyverse-core.md) (loaded after `cve`) still runs.

## Issue 8106 workaround

Commit `1631907` commented out `pep_api_data_obj_put_pre`, which blocked
`iput -p` from writing to a client-supplied physical path. The comment says the
PEP has "a huge memory leak" (https://github.com/irods/irods/issues/8106),
fixed in iRODS 4.3.4, and that there is no workaround. The rule is commented
out unconditionally, so the `iput -p` protection is not in effect on any iRODS
version until it is restored. In the same commit `cyverse_core.re` commented out
its `pep_api_data_obj_put_pre` and replaced its `pep_api_data_obj_put_post`
with `acPostProcForPut`.

## Deployment

`cve` is the first entry in `re_rulebase_set`, ahead of `cyverse_core`,
`cyverse_housekeeping`, and `core`. The list comes from
`irods_cfg_re.additional_rulebases` in the iRODS playbooks and is rendered by
`roles/irods_cfg/templates/macros.j2`; see
[cyverse_core.re](/irods-rules/cyverse-core.md#deployment).

## Tests

`playbooks/tests/rules/cve.py` (36 test methods) replaces `cyverse_core.re` with
`mocks/cyverse_core.re`, whose PEPs log when called, and verifies each
workaround: the intercepted microservices, tar extraction, bulk registration,
copy and put with and without `-p`, `_cve_delete_allowed` and the unlink rule for
readers versus deleters, rule expression execution, direct `rcRegDataObj` calls
(crafting raw packing instructions), and subfile get/put. It also checks that
the `cyverse_core.re` version of a PEP isn't reached when a workaround fires.
The three `pep_api_data_obj_put_pre` `-p` tests are skipped with the reason
"pep_api_data_obj_put_pre has memory leak. Fixed in 4.3.4".

# Citations

[1] `playbooks/files/irods/etc/irods/cve.re` — the workarounds.
[2] `playbooks/tests/rules/cve.py` — tests.
[3] `playbooks/tests/rules/mocks/cyverse_core.re` — stub used by the tests.
[4] `playbooks/group_vars/all/irods.yml` — `_irods_version` default.
[5] `docs/deployment-artifacts/irods.md` — describes `cve.re` and the rule base order.
[6] Commit `1631907` — disabled `pep_api_data_obj_put_pre`.
[7] https://github.com/irods/irods/issues/8106 — the memory leak.
