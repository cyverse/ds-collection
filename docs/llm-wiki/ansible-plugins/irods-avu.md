---
type: Plugin
title: irods_avu Module
description: The cyverse.ds.irods_avu module, which adds, sets, or removes an AVU on an iRODS data object, collection, or resource through python-irodsclient as a rodsadmin user.
resource: /plugins/modules/irods_avu.py
tags: [plugin, module, irods, metadata, avu]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_avu` manages attribute-value-unit (AVU) metadata in iRODS. It
connects with python-irodsclient (the module's documentation says `>=0.8.2`)
over a TLS context and fails unless the connecting user is a `rodsadmin`.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `attribute` | yes | | Attribute name; must not be empty |
| `value` | yes | | Attribute value; must not be empty |
| `units` | no | `null` | Units of the value |
| `entity_name` | yes | | Entity to modify; absolute path for a data object or collection, name for a resource |
| `entity_type` | no | `data object` | `data object`, `resource`, or `collection` |
| `state` | no | `present` | `absent`, `add`, `present`, or `set` |
| `host` | no | `localhost.localdomain` | iRODS server to connect to; must not be empty |
| `port` | no | `1247` | TCP port; must not be null |
| `zone` | yes | | Local zone |
| `username` | no | `rods` | rodsadmin account |
| `password` | yes | | Password for `username` (`no_log`) |

## State semantics

The code implements the states as follows:

- `present` adds the AVU only if the entity has **no** AVU with that attribute.
- `add` adds the AVU only if there's no AVU with the same attribute, value, and
  units.
- `set` does nothing if exactly one AVU with that attribute exists and it
  matches the value and units. Otherwise it replaces the AVUs for that
  attribute with the single given AVU.
- `absent` removes the AVU whose attribute, value, and units all match.

Each state reports `changed` only when it modifies metadata.

## Return values and errors

`RETURN` is empty; the module returns only `changed`. It fails with a message
when the entity doesn't exist, when authentication fails
(`CAT_INVALID_AUTHENTICATION`, `CAT_INVALID_CLIENT_USER`, `CAT_INVALID_USER`),
on a network error, or when python-irodsclient can't be imported.

## Usage

Used by [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md) and
the project playbooks [avra_usage.yml](/ansible-playbooks/avra-usage.md),
[esiil_usage.yml](/ansible-playbooks/esiil-usage.md),
[ncems_usage.yml](/ansible-playbooks/ncems-usage.md), and
[pire_usage.yml](/ansible-playbooks/pire-usage.md).

## Tests

`plugins/modules/tests/irods_avu.yml` first uploads `add-object` and
`set-object` and seeds AVUs on them and on the `ingestRes` resource. It then
exercises:

- `add` with and without units and on a second attribute;
- `set` on new and existing attributes, verifying only one AVU remains;
- `absent` on resource AVUs;
- failures for an empty host, wrong host, empty port, wrong port, unknown zone,
  unknown user, non-admin user, wrong password, empty attribute, and empty
  value.

See [Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

The module's `DOCUMENTATION` lists only `data object` and `resource` as
`entity_type` choices, but the argument spec also accepts `collection`, and
the code handles it.

# Citations

[1] `plugins/modules/irods_avu.py` — module source, documentation, and examples.
[2] `plugins/modules/tests/irods_avu.yml` — module test playbook.
