---
type: Playbook
title: infra_rng_tools.yml
description: Installs rng-tools on managed hosts so Ansible tasks have enough entropy for random number generation.
resource: /playbooks/infra_rng_tools.yml
tags: [infra, entropy, rng-tools]
timestamp: 2026-09-17T00:00:00Z
---

`infra_rng_tools.yml` installs `rng-tools`. The repository `README.md` says
all VMs, including a VM used as the Ansible control node, should run this
playbook so that Ansible tasks have efficient entropy and deployments don't
pause unexpectedly. See [Control Node Setup](/runbooks/control-node-setup.md).

## What it does

One play on `all:!unmanaged_systems:!localhost` with `become: true`:

1. on Ubuntu, refreshes the apt cache (tagged `non_idempotent`);
2. installs the `rng-tools` package.

## Testing

`playbooks/tests/infra_rng_tools.yml` checks that `rng-tools` is installed, or
`rng-tools-debian` when no `rng-tools` package is reported.

# Citations

[1] `playbooks/infra_rng_tools.yml` — the playbook.
[2] `README.md` — the requirement that all VMs run it.
[3] `playbooks/tests/infra_rng_tools.yml` — its test playbook.
