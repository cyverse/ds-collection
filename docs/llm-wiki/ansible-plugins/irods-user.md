---
type: Plugin
title: irods_user Module
description: The cyverse.ds.irods_user module, which creates, updates (type, info, password), or removes an iRODS user, optionally emptying the user's home and trash before removal.
resource: /plugins/modules/irods_user.py
tags: [plugin, module, irods, user]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_user` creates or removes an iRODS user and can modify certain
properties of an existing user. It uses python-irodsclient (the module's
documentation says `>=0.8.2`) with a TLS context, and supports check mode, in
which it makes no changes.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `zone` | yes | | Zone where the change is made; also the managed user's zone |
| `name` | yes | | Username being managed |
| `state` | no | `present` | `present` or `absent` |
| `force` | no | `false` | Remove a user even if their home or trash has data |
| `info` | no | | User info; only used when `present` |
| `password` | no | | User password; only used when `present` (`no_log`) |
| `type` | no | | User type; `rodsuser` when creating, otherwise unchanged if unset |
| `admin_user` | no | `rods` | rodsadmin user authorizing the change |
| `admin_password` | yes | | Password for `admin_user` (`no_log`) |
| `host` | no | `localhost` | iRODS server |
| `port` | no | `1247` | TCP port |

## Behavior

- **absent** — if the user exists, the module removes it. With `force`, it
  first gives the admin session `own` on `/<zone>/home/<user>` and
  `/<zone>/trash/home/<user>` recursively, then force-removes their
  subcollections and unlinks their data objects.
- **present, user missing** — creates the user with the given type (default
  `rodsuser`), then sets the password and info if provided.
- **present, user exists** — updates the type or info if they differ. For the
  password, it opens a second session as the user and changes the password only
  if that login fails with `CAT_INVALID_USER`.

An `iRODSException` fails the task with "unhandled exception: <type>".

## Return values

| Key | Description |
| --- | --- |
| `user` | The username that was managed |

## Usage

Used by [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md),
[irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md), and
[sftp.yml](/ansible-playbooks/sftp.md).

## Tests

`plugins/modules/tests/irods_user.yml` covers:

- creating a user, checking with `iadmin lu` for type `rodsuser`, zone
  `testing`, and info `foo_bar`, and checking the password;
- updating the password, type (to `rodsadmin`), and info of an existing user;
- removing a user without data, and with `force`, a user with data.

See [Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

`DOCUMENTATION` shows a default of `rodsuser*` for `type`, with a footnote that
it applies only when creating. The argument spec has no default; the code
substitutes `rodsuser` at creation time.

In iRODS 4.3.1, the catalog's password check (`db_check_auth_op` in the
PostgreSQL database plugin) returns `CAT_INVALID_USER` only when the user has no
stored password; a password that doesn't match returns
`CAT_INVALID_AUTHENTICATION`. `check_password` catches only
`CAT_INVALID_USER`, so it sets a password only for a user that has none. For a
user whose existing password differs, the login error isn't caught and the task
is expected to fail with "unhandled exception". The test's "Update password"
step doesn't exercise that case: `existing` is created by `iadmin mkuser` with
no password.

# Citations

[1] `plugins/modules/irods_user.py` — module source and documentation.
[2] `plugins/modules/tests/irods_user.yml` — module test playbook.
[3] https://raw.githubusercontent.com/irods/irods/4.3.1/plugins/database/src/db_plugin.cpp — `db_check_auth_op` error codes in iRODS 4.3.1.
