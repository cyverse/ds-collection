---
type: Plugin
title: irods_permission Module
description: The cyverse.ds.irods_permission module, which sets or removes a user's null, read, write, or own permission on an iRODS collection or data object, optionally recursing into a collection's members.
resource: /plugins/modules/irods_permission.py
tags: [plugin, module, irods, acl, permission]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_permission` modifies iRODS ACLs. It can add or remove a
permission on a collection or data object, and for a collection it can apply
the change recursively to the collection's members. Its documentation says it
requires python-irodsclient `<2.0.0`. It connects with a TLS context and sets
ACLs with `admin=True`.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `zone` | yes | | Zone where the change is made |
| `subject` | yes | | Username receiving the permission |
| `subject_zone` | no | value of `zone` | Zone the subject belongs to |
| `permission` | yes | | `null`, `read`, `write`, or `own` |
| `object` | yes | | Collection or data object path |
| `recursion` | no | `none` | `none`, `inclusive` (collection and contents), or `exclusive` (contents only); ignored for data objects |
| `admin_user` | no | `rods` | rodsadmin user authorizing the change |
| `admin_password` | yes | | Password for `admin_user` (`no_log`) |
| `host` | no | `localhost` | iRODS server |
| `port` | no | `1247` | TCP port |

## Behavior

`permission: null` selects removal; anything else selects granting. The module
fails if the subject user or the object doesn't exist.

- **Current permission.** For a collection, the module registers a temporary
  specific query against `r_objt_access` and `r_coll_main`. For a data object,
  it uses a general query conditioned on the user's name and zone. Comments in
  the code explain that conditioning on `User.id` didn't work in iRODS 4.2.8.
- **Whether to change.** With `none`, it compares the object's permission to
  the target. With `inclusive`, it also counts the permissions on
  subcollections and data objects under the path. With `exclusive`, it looks
  only at those member counts.
- **Applying the change.** It sets the ACL, recursively unless recursion is
  `none`. For `exclusive`, it then restores the collection's own previous
  permission.

## Return values

| Key | Returned | Description |
| --- | --- | --- |
| `perm_before` | success | Subject's permission on `object` before any change (`null`, `read`, `write`, `own`) |
| `perm_after` | success | Subject's permission on `object` after any change |

Both values describe only `object` itself, regardless of `recursion`.

## Usage

Used by [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md),
[avra_usage.yml](/ansible-playbooks/avra-usage.md),
[esiil_usage.yml](/ansible-playbooks/esiil-usage.md),
[ncems_usage.yml](/ansible-playbooks/ncems-usage.md), and
[pire_usage.yml](/ansible-playbooks/pire-usage.md).

## Tests

`plugins/modules/tests/irods_permission.yml` creates a remote zone, test users,
collections, and data objects on `irods_catalog`. It then covers:

- removing and granting read, write, and own permissions on a data object,
  including for a remote-zone user;
- non-recursive grant and removal on a collection, checking that members are
  unaffected;
- inclusive recursive grant and removal;
- granting own on an empty collection;
- exclusive recursion, checking that the collection keeps its own permission
  while its members change.

A large nested-collection case is commented out because it takes a long time.
See [Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

In check mode, `run()` calls `self.exit_json(**self._result)`, but the class
never defines `_result`.

# Citations

[1] `plugins/modules/irods_permission.py` — module source and documentation.
[2] `plugins/modules/tests/irods_permission.yml` — module test playbook.
