---
type: RuleSet
title: cyverse_json.re — JSON Support
description: An iRODS rule language implementation of JSON values, serialization, and deserialization used for AMQP messages and API PEP inputs.
resource: /playbooks/files/irods/etc/irods/cyverse_json.re
tags: [irods, rules, json, library]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse_json.re` provides "iRODS rule language logic for working with JSON
documents". It defines no PEPs. Its header lists three limitations:

1. Only tab, carriage return, and line feed control characters are supported in
   strings.
2. Exponential notation isn't supported.
3. Numbers may not begin with `.` or `+`.

## Public interface

- `data cyverse_json_val` — constructors `cyverse_json_empty` (a placeholder,
  not part of JSON), `cyverse_json_null`, `cyverse_json_bool`,
  `cyverse_json_num`, `cyverse_json_str`, `cyverse_json_array`, and
  `cyverse_json_obj` (a list of name/value pairs).
- `cyverse_json_serialize(*Val)` — returns the serialized string.
- `cyverse_json_getValue(*Doc, *FieldName)` — returns a field of an object, or
  `cyverse_json_empty`.
- `cyverse_json_deserialize(*Serial)` — returns
  `cyverse_json_deserialize_val(value, remainder)` or
  `cyverse_json_deserialize_err(message, partial, remainder)`.

Everything else is prefixed `_cyverse_json_` and private (list reversal, string
helpers, escaping, per-type deserializers).

## Consumers

- [cyverse_logic.re](/irods-rules/cyverse-logic.md) builds AMQP message bodies
  with `cyverse_json_obj` and `cyverse_json_serialize`, and parses touch input.
- [cyverse_repl.re](/irods-rules/cyverse-repl.md) parses the `TOUCH` API's JSON
  input.

Included by [cyverse_core.re](/irods-rules/cyverse-core.md).

## Tests

`playbooks/tests/rules/cyverse_json.py` has 29 test methods for the list, string,
encoding, value, and deserialization logic; most are marked skipped or not
implemented.

# Citations

[1] `playbooks/files/irods/etc/irods/cyverse_json.re` — the library.
[2] `playbooks/tests/rules/cyverse_json.py` — tests.
