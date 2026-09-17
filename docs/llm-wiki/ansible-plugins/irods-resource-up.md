---
type: Plugin
title: irods_resource_up Module
description: The cyverse.ds.irods_resource_up module, which sets an iRODS resource's status to up along with the status of every ancestor resource.
resource: /plugins/modules/irods_resource_up.py
tags: [plugin, module, irods, resource, status]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_resource_up` changes the status of a resource and all of its
parents to `up`. It uses python-irodsclient (the module's documentation says
`>=0.8.2`) and supports check mode, in which it makes no changes.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `resource` | yes | | Name of the resource to bring up |
| `host` | yes | | iRODS server |
| `port` | yes | | TCP port |
| `admin_user` | yes | | rodsadmin user (`no_log`) |
| `admin_password` | yes | | Password for `admin_user` (`no_log`) |
| `zone` | yes | | Zone for authentication |

## Behavior

The module gets the resource. If its status isn't `up`, it sets it. It then
does the same for the resource named by `parent_name`, and so on up the
hierarchy. `changed` is true if any status was modified.

It fails with "The provided admin credentials are invalid." on
`CAT_INVALID_AUTHENTICATION`, and with "The resource <name> doesn't exist."
when the resource is missing.

## Return values

| Key | Description |
| --- | --- |
| `resource` | The resource name passed in |

## Usage

Used by [pire_usage.yml](/ansible-playbooks/pire-usage.md).

## Tests

`plugins/modules/tests/irods_resource_up.yml` creates a `passthru` parent and
child, both with status `down`. It brings up the child and checks with
`iquest` that both the child and the parent are `up`, then checks that a
nonexistent resource fails with the expected message. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

`DOCUMENTATION` lists only `resource`, with type `object`. The argument spec
declares `resource` as a string and also requires `host`, `port`,
`admin_user`, `admin_password`, and `zone`. The example block is named
`EXAMPLE` rather than `EXAMPLES`.

# Citations

[1] `plugins/modules/irods_resource_up.py` — module source and documentation.
[2] `plugins/modules/tests/irods_resource_up.yml` — module test playbook.
