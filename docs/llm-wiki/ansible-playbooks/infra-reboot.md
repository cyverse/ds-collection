---
type: Playbook
title: infra_reboot.yml
description: Reboots managed hosts whose infra_rebootable setting allows it.
resource: /playbooks/infra_reboot.yml
tags: [infra, reboot]
timestamp: 2026-09-17T00:00:00Z
---

`infra_reboot.yml` reboots hosts. It has one play on
`all:!unmanaged_systems:!localhost` with `become: true` and one task that runs
`ansible.builtin.reboot` when `infra_rebootable` is true (default `true`). The
task is tagged `no_testing`.

[infra_system_packages.yml](/ansible-playbooks/infra-system-packages.md)
imports this playbook to reboot hosts after package upgrades.

There is no `playbooks/tests/infra_reboot.yml`.

# Citations

[1] `playbooks/infra_reboot.yml` — the playbook.
[2] `playbooks/group_vars/all/infra.yml` — `infra_rebootable` default.
