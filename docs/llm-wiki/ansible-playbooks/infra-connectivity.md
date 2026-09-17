---
type: Playbook
title: infra_connectivity.yml
description: Installs or removes maintainer SSH public keys in the connecting user's authorized_keys on managed hosts.
resource: /playbooks/infra_connectivity.yml
tags: [infra, ssh, authorized-keys]
timestamp: 2026-09-17T00:00:00Z
---

`infra_connectivity.yml` manages the SSH keys maintainers use to reach the
hosts.

## Hosts

One play on `all:!unmanaged_systems`, without `become`, so keys go into the
`authorized_keys` of the user Ansible connects as (`ansible_user_id`).

## What it does

For each entry in `infra_maintainer_keys` (default `[]`) it applies
`ansible.posix.authorized_key`. An entry is either a key string, which is
installed, or a mapping with `key` and an optional `state` (`present` by
default, or `absent` to remove the key).

The task is skipped entirely when `infra_personal_ssh` or `infra_proxied_ssh`
is true (both default to `false`).

## Testing

`playbooks/tests/infra_connectivity.yml` relies on the four keys in
`testing/ansible-tester/inventory/group_vars/all/vars.yml`. It checks that the
three keys commented `allowed 1`–`allowed 3` are in `~/.ssh/authorized_keys`
and that the key commented `disallowed` (state `absent`) is not.

# Citations

[1] `playbooks/infra_connectivity.yml` — the playbook.
[2] `playbooks/group_vars/all/infra.yml` — `infra_maintainer_keys`,
`infra_personal_ssh`, and `infra_proxied_ssh` defaults.
[3] `playbooks/tests/infra_connectivity.yml` — its test playbook.
