---
type: Plugin
title: irods_move Module
description: The cyverse.ds.irods_move module, which renames an iRODS collection through python-irodsclient and treats an already-completed move as success.
resource: /plugins/modules/irods_move.py
tags: [plugin, module, irods, collection, rename]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_move` renames an iRODS collection. Its documentation says it
can rename a data object or a collection, and that for idempotency it assumes
the move already happened when the source is missing but the destination
exists. It connects with python-irodsclient and a TLS context, and supports
check mode, in which it makes no changes.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `source` | yes | | Current absolute path |
| `destination` | yes | | New absolute path |
| `host` | yes | | iRODS server hostname |
| `port` | yes | | iRODS server port |
| `admin_user` | yes | | Admin username (`no_log`) |
| `admin_password` | yes | | Admin password (`no_log`) |
| `zone` | yes | | Admin user's zone |

## Behavior

The module checks `collections.exists` for both paths. If the source exists, or
the destination doesn't, it calls `collections.move(source, destination)` and
reports a change. Only when the source is missing and the destination exists
does it skip the move. Any exception fails the task with "Unable to move irods
object/collection <source>".

## Return values

| Key | Description |
| --- | --- |
| `exc` | Type of the last iRODS exception, or empty |
| `exc_msg` | Message of the last iRODS exception, or empty |

## Usage

Used by [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md).

## Tests

`plugins/modules/tests/irods_move.yml` creates `/testing/home/rods/test_src`,
then checks that:

- a move where neither path exists fails;
- moving the collection succeeds and `ils` shows only the destination;
- a move with identical source and destination fails.

See [Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

- The module's `DOCUMENTATION` lists only `source` and `destination`. The
  argument spec also requires `host`, `port`, `admin_user`, `admin_password`,
  and `zone`, which `EXAMPLES` shows.
- The existence checks and the move use the collections API only, so the code
  doesn't show how a data object source is handled, despite what the
  documentation says.

# Citations

[1] `plugins/modules/irods_move.py` — module source and documentation.
[2] `plugins/modules/tests/irods_move.yml` — module test playbook.
