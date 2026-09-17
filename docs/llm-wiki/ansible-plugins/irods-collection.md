---
type: Plugin
title: irods_collection Module
description: The cyverse.ds.irods_collection module, which creates or force-removes an iRODS collection, optionally creating parent collections, through python-irodsclient.
resource: /plugins/modules/irods_collection.py
tags: [plugin, module, irods, collection]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_collection` ensures an iRODS collection is present or absent.
It requires python-irodsclient (the module's documentation says `>=0.8.2`) and
fails with "python-irodsclient not installed" if it can't import it. It
connects with a TLS context and supports check mode, in which it makes no
changes.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `path` | yes | | Path of the collection |
| `state` | no | `present` | `present` or `absent` |
| `parents` | no | `false` | Create parent collections; only meaningful when `state` is `present` |
| `host` | yes | | iRODS server hostname |
| `port` | yes | | iRODS server port |
| `admin_user` | yes | | Admin username (`no_log`) |
| `admin_password` | yes | | Admin password (`no_log`) |
| `zone` | yes | | Admin user's zone |

## Behavior

Existence is checked with a catalog query on `Collection.name`.

- **present** — if the collection exists, returns without change. Otherwise it
  calls `collections.create(path, recurse=parents)` and checks again, failing
  with "Collection disappear after creation" if it's still missing.
- **absent** — if the collection is missing, returns without change. Otherwise
  it calls `collections.remove(path, force=True)` and checks again, failing if
  the collection remains.

## Return values

| Key | Description |
| --- | --- |
| `collection` | The collection that was changed |
| `exc` | Type of the last iRODS exception, or empty |
| `exc_msg` | Message of the last iRODS exception, or empty |

## Usage

Used by [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md),
[avra_usage.yml](/ansible-playbooks/avra-usage.md),
[esiil_usage.yml](/ansible-playbooks/esiil-usage.md),
[ncems_usage.yml](/ansible-playbooks/ncems-usage.md), and
[pire_usage.yml](/ansible-playbooks/pire-usage.md).

## Tests

`plugins/modules/tests/irods_collection.yml` covers:

- creating a collection;
- removing a collection;
- creating a nested collection with `parents: false`, expecting the task to
  fail and the collection not to exist;
- creating a nested collection with `parents: true`, verifying it exists.

See [Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

# Citations

[1] `plugins/modules/irods_collection.py` — module source and documentation.
[2] `plugins/modules/tests/irods_collection.yml` — module test playbook.
