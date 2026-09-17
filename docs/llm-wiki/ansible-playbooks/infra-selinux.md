---
type: Playbook
title: infra_selinux.yml
description: Disables SELinux on managed hosts where it is enabled.
resource: /playbooks/infra_selinux.yml
tags: [infra, selinux]
timestamp: 2026-09-17T00:00:00Z
---

`infra_selinux.yml` has one play on `all:!unmanaged_systems:!localhost` with
`become: true`. When `ansible_selinux.status` is `enabled`, it sets SELinux to
`disabled` with `ansible.posix.selinux`. The play is tagged `no_testing`.

There is no `playbooks/tests/infra_selinux.yml`.

# Citations

[1] `playbooks/infra_selinux.yml` — the playbook.
