---
type: Plugin
title: json_patch Module
description: The cyverse.ds.json_patch module, which adds or updates top-level string and number fields in a JSON file on a managed host.
resource: /plugins/modules/json_patch.py
tags: [plugin, module, json, configuration]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.json_patch` updates entries in a JSON file on a managed host,
adding any that are missing. It works only with top-level fields and supports
only numbers and strings. It uses only the Python standard library.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `path` | yes | | Absolute path to the JSON file |
| `updates` | yes | | List of update dictionaries |

Each `updates` item has these fields:

| Field | Required | Default | Description |
| --- | --- | --- | --- |
| `field` | yes | | Name of the top-level field |
| `force` | no | `false` | Overwrite the field if it already exists |
| `type` | no | `string` | `number` or `string` |
| `value` | no | `null` | New value |

## Behavior

- If the file doesn't exist, the module creates it, and any missing parent
  directories, containing `{}`.
- For each update, a value with `type: number` is converted with `float()`, and
  otherwise with `str()`.
- A field that's missing is set. A field that exists is overwritten only when
  `force` is true and its current value differs.
- When anything changed, the file is rewritten with 4-space indentation and
  sorted keys.

The module returns only `changed`.

## Usage

No playbook in `playbooks/` uses it. The `irods_cfg_upgrade` molecule scenario
of the [irods_cfg role](/ansible-roles/irods-cfg.md) uses it to patch
`schema_validation_base_uri` in `server_config.json`, and three transfer
settings in `irods_environment.json`, while upgrading iRODS from 4.2.8 to
4.3.1.

## Tests

There is no `plugins/modules/tests/json_patch.yml`.

## Notes

Because numbers go through `float()`, a numeric value such as `4` is written
as `4.0`.

# Citations

[1] `plugins/modules/json_patch.py` — module source and documentation.
[2] `molecule/irods_cfg_upgrade/converge.yml` — the only use of the module.
