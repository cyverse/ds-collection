---
type: Playbook
title: infra_mail.yml
description: Installs sendmail on managed hosts for alert mail and, for hosts inventoried by IP address, configures sendmail masquerading as the infra domain.
resource: /playbooks/infra_mail.yml
tags: [infra, mail, sendmail, alerts]
timestamp: 2026-09-17T00:00:00Z
---

`infra_mail.yml` sets up outgoing mail so hosts can send alerts.

## Hosts

One play on `all:!unmanaged_systems:!localhost` with `become: true`.

## What it does

1. On Ubuntu, refreshes the apt cache (tagged `non_idempotent`).
2. Installs `sendmail`.
3. Only when the inventory hostname is an IP address (checked with the
   `ansible.utils.ipaddr` filter):
   1. installs `m4` and `sendmail-cf`;
   2. adds a managed block to `/etc/mail/sendmail.mc` enabling
      `masquerade_envelope`, masquerading as `infra_domain_name` and
      masquerading the host's FQDN;
   3. rebuilds `/etc/mail/sendmail.cf` with `m4` when the `.mc` file is newer
      and the output differs, then restarts sendmail.

## Variables

`infra_domain_name` is mandatory (it has no default in
`playbooks/group_vars/all/infra.yml`).

## Testing

`playbooks/tests/infra_mail.yml` only checks that `sendmail` is installed. A
comment explains that the masquerading configuration can't be tested because
no hostname in the testing environment is an IP address.

# Citations

[1] `playbooks/infra_mail.yml` — the playbook.
[2] `playbooks/group_vars/all/infra.yml` — `infra_domain_name`.
[3] `playbooks/tests/infra_mail.yml` — its test playbook.
