---
type: Plugin
title: irods_unixfilesystem_resource Module
description: The cyverse.ds.irods_unixfilesystem_resource module, which creates an iRODS unixfilesystem storage resource and fails if one with the same name exists with a different type, host, vault, or context.
resource: /plugins/modules/irods_unixfilesystem_resource.py
tags: [plugin, module, irods, resource, storage]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_unixfilesystem_resource` creates an iRODS Unix filesystem
storage resource. The status is set only when the resource is created. It uses
python-irodsclient and supports check mode, in which it makes no changes.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `name` | yes | | Resource name |
| `host` | yes | | Resource server that hosts the resource; also the server the module connects to |
| `vault` | yes | | Absolute path to the vault root |
| `context` | no | `""` | Context to attach |
| `status` | no | `up` | Starting status |
| `port` | no | `1247` | TCP port |
| `zone` | yes | | Local zone |
| `username` | no | `rods` | rodsadmin account |
| `password` | yes | | Password for `username` (`no_log`) |

## Behavior

- **Resource exists.** The module compares it with the request and fails with
  "Resource already exists with different type / on different host / in
  different vault / with different context" on any mismatch. The type may be
  `unixfilesystem` or `unix file system`. If everything matches, it makes no
  change.
- **Resource missing.** It creates the resource with type `unixfilesystem`,
  then sets its status. If either step raises, it tries to remove the partly
  created resource and fails with "unable to create resource", or "unable to
  fully create resource" if the cleanup also failed.
- **Connection failure.** It fails with "unable to connect to iRODS server".

## Return values

| Key | Description |
| --- | --- |
| `response` | Always an empty string |
| `exc` | Type of the underlying exception on failure, or empty |
| `exc_msg` | Message of the underlying exception on failure, or empty |

## Usage

Used by [irods_storage_resources.yml](/ansible-playbooks/irods-storage-resources.md).

## Tests

`plugins/modules/tests/irods_unixfilesystem_resource.yml` runs on the configured
CentOS consumer. It creates two vault directories and two resources, one with
only the required options and one with every option. It then checks each
resource's name, vault path, and host with `iquest`, and the second resource's
context and status. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

# Citations

[1] `plugins/modules/irods_unixfilesystem_resource.py` — module source and documentation.
[2] `plugins/modules/tests/irods_unixfilesystem_resource.yml` — module test playbook.
