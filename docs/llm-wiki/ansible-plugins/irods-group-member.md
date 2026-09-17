---
type: Plugin
title: irods_group_member Module
description: The cyverse.ds.irods_group_member module, which adds users to or removes users from an existing iRODS group through python-irodsclient.
resource: /plugins/modules/irods_group_member.py
tags: [plugin, module, irods, group, user]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_group_member` ensures a list of users is present in, or absent
from, an iRODS group. The group must already exist, or the module fails with
"Group must already exist". It requires python-irodsclient, connects with a TLS
context, and supports check mode, in which it makes no changes.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `group` | yes | | Name of an existing iRODS group |
| `users` | yes | | List of usernames |
| `state` | yes | | `present` or `absent` |
| `host` | yes | | iRODS server hostname |
| `port` | yes | | iRODS server port |
| `admin_user` | yes | | Admin username (`no_log`) |
| `admin_password` | yes | | Admin password (`no_log`) |
| `zone` | yes | | Admin user's zone |

## Behavior

- **present** — filters `users` to those not already in the group and adds each
  with `groups.addmember`. It then re-checks membership and fails with
  "Specified user(s) not in group after adding" if any are still missing.
- **absent** — filters to users currently in the group and removes each with
  `groups.removemember`. It then fails if any remain.

Membership is checked by iterating a `User.name, Group.name` query.

## Return values

| Key | Description |
| --- | --- |
| `message` | The operation performed |
| `users` | Users changed by the task, or on failure the users left in the wrong state |

## Usage

Used by [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md),
[irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md), and
[pire_usage.yml](/ansible-playbooks/pire-usage.md). The test playbook
`playbooks/tests/irods_resource_server.yml` also uses it.

## Tests

`plugins/modules/tests/irods_group_member.yml` creates two groups and three
users, all members of the removal group. It adds users to one group and checks
they're present, removes users from the other and checks they're absent, and
checks that the users not removed are still members. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

The module's `DOCUMENTATION` describes `users` as "Username of user" without a
type, but the argument spec requires a list of strings.

# Citations

[1] `plugins/modules/irods_group_member.py` — module source and documentation.
[2] `plugins/modules/tests/irods_group_member.yml` — module test playbook.
