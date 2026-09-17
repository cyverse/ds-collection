---
type: Plugin
title: warn_if_false Test
description: The cyverse.ds.warn_if_false Jinja2 test, which returns a Boolean unchanged and prints a warning when it is false; used to gate restart and reboot handlers.
resource: /plugins/test/warn_if_false.py
tags: [plugin, test, jinja2, handlers]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.warn_if_false` is a Jinja2 test plugin. It returns the tested value
unchanged. When the value is false, it also writes the given message to the
Ansible display as a warning.

## Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| `_value` | yes | The Boolean being tested |
| `_warning` | yes | Warning text to display when `_value` is false |

```yaml
when: >-
  haproxy_restart_allowed
  is cyverse.ds.warn_if_false(
    inventory_hostname + ' skipped, RESTART REQUIRED FOR SETTINGS TO TAKE' )
```

## Usage

The collection uses it to skip disruptive handlers unless they are explicitly
allowed, while leaving a visible warning that action is still needed:

- the `Restart haproxy` handler of the [haproxy role](/ansible-roles/haproxy.md),
  gated on `haproxy_restart_allowed`;
- the `Restart postgres` and `Reboot` handlers of the
  [postgresql role](/ansible-roles/postgresql.md), gated on
  `postgresql_restart_allowed` and `postgresql_reboot_allowed`.

## Tests

There is no test playbook for this plugin under `plugins/test/`.

# Citations

[1] `plugins/test/warn_if_false.py` — test plugin source and documentation.
[2] `roles/haproxy/handlers/main.yml` — use in the haproxy role.
[3] `roles/postgresql/handlers/main.yml` — use in the postgresql role.
