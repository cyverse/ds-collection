---
type: Playbook
title: infra_fail2ban.yml
description: On CentOS hosts running fail2ban, whitelists the vault.centos.org address range in jail.conf.
resource: /playbooks/infra_fail2ban.yml
tags: [infra, fail2ban, centos]
timestamp: 2026-09-17T00:00:00Z
---

`infra_fail2ban.yml` keeps fail2ban from blocking the CentOS 7 vault
repository.

## Hosts

One play on `all:!unmanaged_systems` with `become: true`.

## What it does

On CentOS hosts it gathers service facts, and if `fail2ban.service` exists it
sets `ignoreip = 18.238.85.0/25` in `/etc/fail2ban/jail.conf`. A change
notifies two handlers: reload `fail2ban` and restart `iptables`.

## Testing

There is no `playbooks/tests/infra_fail2ban.yml`.

# Citations

[1] `playbooks/infra_fail2ban.yml` — the playbook.
