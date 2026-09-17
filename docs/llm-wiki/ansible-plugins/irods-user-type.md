---
type: Plugin
title: irods_user_type Module
description: The cyverse.ds.irods_user_type module, which adds or removes an iRODS user type token using iadmin and iquest.
resource: /plugins/modules/irods_user_type.py
tags: [plugin, module, irods, user-type, icommands]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_user_type` adds or removes a user type in an iRODS zone. It
shells out to the iCommands `iquest` and `iadmin`, so it runs on a host where
those are installed and authenticated as a rodsadmin.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `type` | yes | | Label of the user type |
| `description` | no | `""` | Description; only applicable when `state` is `present` |
| `state` | no | `present` | `absent` or `present` |

## Behavior

The module looks up the `user_type` token's ID and description (`TOKEN_ID` and
`TOKEN_VALUE2`) with `iquest`.

- **present** — if the token is missing, runs
  `iadmin at user_type <type> '' '<description>'` and reports a change. If the
  token exists with a different description, it fails with "user type <type>
  already in use for another purpose". Otherwise it makes no change.
- **absent** — if the token exists, runs `iadmin rt user_type <type>` and
  reports a change.

An `iquest` exit code of 1 is treated as "not found"; any other nonzero code
fails the task. `RETURN` is empty; the result echoes `params`.

## Usage

Used by [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md).

## Tests

`plugins/modules/tests/irods_user_type.yml` runs on the configured provider as
`irods`. It creates a user type `unknown` without a description and verifies
with `iquest` that the token exists and has no description. Tests for creating
with a description, updating the description, and removal are TODO
placeholders. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

# Citations

[1] `plugins/modules/irods_user_type.py` — module source and documentation.
[2] `plugins/modules/tests/irods_user_type.yml` — module test playbook.
