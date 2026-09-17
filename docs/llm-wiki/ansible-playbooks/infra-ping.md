---
type: Playbook
title: infra_ping.yml
description: Checks Ansible connectivity to every managed host by gathering facts.
resource: /playbooks/infra_ping.yml
tags: [infra, connectivity, facts]
timestamp: 2026-09-17T00:00:00Z
---

`infra_ping.yml` is a connectivity check. It has one play on
`all:!unmanaged_systems` with fact gathering disabled, and a single task that
runs `ansible.builtin.setup`. A host that can't be reached or can't run the
setup module fails the play.

There is no `playbooks/tests/infra_ping.yml`.

# Citations

[1] `playbooks/infra_ping.yml` — the playbook.
