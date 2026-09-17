---
type: Plugin
title: uuid Lookup
description: The cyverse.ds.uuid lookup plugin, which returns a version 1, 3, 4, or 5 UUID using Python's uuid module.
resource: /plugins/lookup/uuid.py
tags: [plugin, lookup, uuid]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.uuid` is a lookup plugin that generates a UUID of the requested
version with Python's standard `uuid` module. It uses a `match` statement, so
it needs Python 3.10 or later on the controller.

## Terms

The first term is the UUID version:

| Version | Result | Extra terms |
| --- | --- | --- |
| `1` | Time-based UUID | none |
| `4` | Random UUID | none |
| `3` | Name-based UUID (MD5) | namespace UUID, name |
| `5` | Name-based UUID (SHA-1) | namespace UUID, name |

```yaml
msg: "{{ lookup('cyverse.ds.uuid', 5, '6ba7b810-9dad-11d1-80b4-00c04fd430c8', 'example') }}"
```

The lookup returns a one-element list holding the UUID string. It raises an
`AnsibleError` when no terms are given, when a type 3 or 5 request is missing
its namespace or name, or when the version isn't 1, 3, 4, or 5.

## Usage

Used by [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md).

## Tests

`plugins/lookup/tests/uuid.yml` prints a UUID of each version with
`ansible.builtin.debug`: 1, 4, 3 with the DNS namespace, and 5. It doesn't
assert on the values. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

The plugin's `EXAMPLES` call `lookup('uuid', …)` without the `cyverse.ds.`
prefix.

# Citations

[1] `plugins/lookup/uuid.py` — lookup plugin source and documentation.
[2] `plugins/lookup/tests/uuid.yml` — lookup test playbook.
