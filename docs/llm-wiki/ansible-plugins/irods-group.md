---
type: Plugin
title: irods_group Module
description: The cyverse.ds.irods_group module, which creates or removes an iRODS group through python-irodsclient.
resource: /plugins/modules/irods_group.py
tags: [plugin, module, irods, group]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_group` ensures an iRODS group exists or doesn't. It imports
python-irodsclient at load time, connects with a TLS context, and supports check
mode, in which it makes no changes.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `group` | yes | | Name of the iRODS group |
| `state` | yes | | `present` or `absent` |
| `host` | yes | | iRODS server hostname |
| `port` | yes | | iRODS server port |
| `admin_user` | yes | | Admin username |
| `admin_password` | yes | | Admin password (`no_log`) |
| `zone` | yes | | Admin user's zone |

## Behavior

The module decides whether the group exists by calling `groups.get` and
catching `GroupDoesNotExist`.

- **present** — creates the group with `groups.create` if it's missing
  (message "Group is created"), otherwise "Group already exists".
- **absent** — removes the group with `groups.remove` if it exists (message
  "Group is removed"), otherwise "Group does not exist".

An `iRODSException` fails the task with "Unable to create/remove irods group".

## Return values

| Key | Description |
| --- | --- |
| `message` | The operation performed |
| `group` | The group named in the task |

## Usage

Used by [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md) and
[pire_usage.yml](/ansible-playbooks/pire-usage.md).

## Tests

`plugins/modules/tests/irods_group.yml` runs once on `irods_catalog`. It creates
a group to remove with `iadmin mkgroup`, then runs the module from `localhost`
to create one group and remove the other, checking each result with
`iadmin lg`. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

Unlike [irods_collection](/ansible-plugins/irods-collection.md) and
[irods_group_member](/ansible-plugins/irods-group-member.md), `admin_user` isn't
marked `no_log` here.

# Citations

[1] `plugins/modules/irods_group.py` — module source and documentation.
[2] `plugins/modules/tests/irods_group.yml` — module test playbook.
