---
type: Playbook
title: infra_timezone.yml
description: Sets managed hosts' timezone to America/Phoenix and restarts cron.
resource: /playbooks/infra_timezone.yml
tags: [infra, timezone, cron]
timestamp: 2026-09-17T00:00:00Z
---

`infra_timezone.yml` has one play on `all:!unmanaged_systems:!localhost` with
`become: true`, tagged `no_testing`. It sets the timezone to `America/Phoenix`
(the task is named "Make Mountain Standard Time") and, on change, restarts
`cron` on Ubuntu or `crond` elsewhere. The timezone isn't configurable.

There is no `playbooks/tests/infra_timezone.yml`.

# Citations

[1] `playbooks/infra_timezone.yml` — the playbook.
