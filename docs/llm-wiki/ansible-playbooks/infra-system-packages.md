---
type: Playbook
title: infra_system_packages.yml
description: Upgrades all system packages on managed hosts and optionally reboots hosts whose packages changed.
resource: /playbooks/infra_system_packages.yml
tags: [infra, packages, upgrade, reboot]
timestamp: 2026-09-17T00:00:00Z
---

`infra_system_packages.yml` brings managed hosts' packages up to date.

## Plays

1. **Upgrade system packages** (`all:!unmanaged_systems:!localhost`,
   `become: true`) — refreshes the apt cache on Ubuntu, then upgrades every
   package (`name: '*'`, `state: latest`) and registers the result.
2. **Reboot changed nodes** — imports
   [infra_reboot.yml](/ansible-playbooks/infra-reboot.md) with the condition
   that the upgrade changed something and `infra_reboot_on_pkg_change` is true
   (default `false`).

Both plays are tagged `non_idempotent`.

## Testing

There is no `playbooks/tests/infra_system_packages.yml`.

# Citations

[1] `playbooks/infra_system_packages.yml` — the playbook.
[2] `playbooks/group_vars/all/infra.yml` — `infra_reboot_on_pkg_change` and
`infra_rebootable` defaults.
