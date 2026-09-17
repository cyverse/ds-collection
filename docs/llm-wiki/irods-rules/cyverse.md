---
type: RuleSet
title: cyverse.re and cyverse-env.re — Shared Library and Environment Constants
description: The shared rule library used by the core and service rule bases, plus the templated environment constants (zone, default resources, AMQP exchange, email addresses) it includes.
resource: /playbooks/files/irods/etc/irods/cyverse.re
tags: [irods, rules, library, constants, templates]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.re` describes itself as "a library of rules to support service
specific policies". It defines no PEPs. It includes `cyverse-env`, the rule base
generated from `playbooks/templates/irods/etc/irods/cyverse-env.re.j2`, so every
file that includes `cyverse` also gets the environment constants.
[cyverse_core.re](/irods-rules/cyverse-core.md) includes it first.

## Environment constants (`cyverse-env.re.j2`)

| Constant | Type | Template value | Default |
| --- | --- | --- | --- |
| `cyverse_AMQP_EXCHANGE` | string | `_irods_amqp_exchange` | `irods` |
| `cyverse_DEFAULT_REPL_RESC` | string | `_irods_default_repl_resource` | `_irods_default_resource` |
| `cyverse_DEFAULT_RESC` | string | `_irods_default_resource` | name of the first `_irods_resource_hierarchies` entry (`demoResc` when none are defined) |
| `cyverse_EMAIL_FROM_ADDR` | string | `<_irods_service_account_name>@<inventory_hostname>` | `irods@<host>` |
| `cyverse_EMAIL_REPORT_ADDR` | string | `_irods_report_email_addr` | `root@localhost` |
| `cyverse_INIT_REPL_DELAY` | integer | `_irods_init_repl_delay` | `0` |
| `cyverse_IS_CATALOG_PROVIDER` | boolean | whether the host is in the `irods_catalog` group | — |
| `cyverse_RE_HOST` | string | `_irods_re_host` | first host in `irods_catalog` |
| `cyverse_ZONE` | string | `_irods_zone_name` | `tempZone` |

The `_irods_*` variables and their defaults are in
`playbooks/group_vars/all/irods.yml`; each is overridable by the same name
without the leading underscore (e.g. `irods_init_repl_delay`).

Constant consumers: `cyverse_AMQP_EXCHANGE` and `cyverse_RE_HOST` in
[cyverse_logic.re](/irods-rules/cyverse-logic.md);
`cyverse_DEFAULT_RESC`, `cyverse_DEFAULT_REPL_RESC`, and
`cyverse_INIT_REPL_DELAY` in [cyverse_repl.re](/irods-rules/cyverse-repl.md)
(`cyverse_DEFAULT_RESC` also in `cyverse_blockRescReq`);
the email constants in
[cyverse_housekeeping.re](/irods-rules/cyverse-housekeeping.md);
`cyverse_IS_CATALOG_PROVIDER` in `cyverse_core.re`; and `cyverse_ZONE` in
several files.

## Library contents

- **List and string helpers:** `cyverse_contains`, `cyverse_endsWith`,
  `cyverse_startsWith`, `cyverse_rmPrefix`.
- **Key-value maps:** `cyverse_hasKey` and `cyverse_getValue` (missing or empty
  keys yield `false`/`''`).
- **File constants:** `cyverse_FILE_CREATE`, `cyverse_FILE_OPEN_WRITE`, the
  `cyverse_OPEN_FLAG_*` values, and `cyverse_replTruncated(*OpenFlags)`.
- **Entity types:** the `-C`, `-d`, `-R`, `-u` constants (`cyverse_COLL`,
  `cyverse_DATA_OBJ`, `cyverse_RESC`, `cyverse_USER`), the `cyverse_is*`
  predicates, and `cyverse_getEntityType`.
- **Data object lookups:** `cyverse_getDataId`, `cyverse_getDataPath`, and
  `cyverse_getDataInfo` (size, type, owner of the replica with
  `DATA_REPL_STATUS` 1).
- **Action tracking:** `cyverse_registerAction`, `cyverse_isCurrentAction`, and
  `cyverse_unregisterAction` store the first action taken on an entity in
  `temporaryStorage` under `<rulebase>-<id>-ROOT_ACTION`, so nested PEP firings
  can tell whether they are the root action.
- **Project resource restriction:** `cyverse_blockRescReq(*Op, *ProjResc,
  *ReqRescHier, *DataPath)` returns true when the operation isn't `OPEN` or
  `UNLINK`, the project resource isn't `cyverse_DEFAULT_RESC`, the requested
  hierarchy's root is the project resource, and the path isn't under any
  `ipc::hosted-collection` AVU value on that resource. The project rule files
  use it.
- **Service collection access:** `cyverse_ensureAccessOnCreateColl`,
  `cyverse_ensureAccessOnCreateDataObj`, and `cyverse_ensureAccessOnMv` grant a
  service user a permission on entities inside
  `/<zone>/home/<user>/<SvcColl>`, excluding the service user's own home and
  `home/shared`. Used by [coge.re](/irods-rules/coge.md).
- **Protected AVUs:** `cyverse_setProtectedAVU` "sets a protected AVU on an
  entity as a rodsadmin user" by running the `imeta-exec` command script.

## Deployment

`cyverse.re` is copied with the other static rule files by the
[irods_cfg role](/ansible-roles/irods-cfg.md). `cyverse-env.re.j2` is rendered
from `irods_cfg_rulebases_templated` with the `.j2` suffix removed. Neither is
listed in `re_rulebase_set`; they load through `@include`.

## Tests

- `playbooks/tests/rules/cyverse.py` — 81 test methods (some skipped) covering
  the constants, list/string helpers, key-value functions, open-flag logic,
  entity type predicates, service access helpers, and
  `cyverse_setProtectedAVU`. The data object lookup tests are skipped as not
  implemented, and the action tracking and resource restriction test classes
  are marked `@test_rules.unimplemented`.
- `playbooks/tests/rules/cyverse-env.py` — checks each constant in the deployed
  `cyverse-env.re`, including `cyverse_IS_CATALOG_PROVIDER` on a provider and a
  consumer.
- `playbooks/tests/irods_rule_templates.yml` — renders the template with the
  group_vars defaults and asserts the expanded constants.

# Citations

[1] `playbooks/files/irods/etc/irods/cyverse.re` — the library.
[2] `playbooks/templates/irods/etc/irods/cyverse-env.re.j2` — environment constants template.
[3] `playbooks/group_vars/all/irods.yml` — defaults for the template variables.
[4] `playbooks/tests/rules/cyverse.py` — library tests.
[5] `playbooks/tests/rules/cyverse-env.py` — deployed constant tests.
[6] `playbooks/tests/irods_rule_templates.yml` — template expansion tests.
