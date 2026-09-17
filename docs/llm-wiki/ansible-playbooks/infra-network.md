---
type: Playbook
title: infra_network.yml
description: Tunes networking — MTU and transmit queue length on physical hosts' default interface and net.* sysctl settings on all managed hosts.
resource: /playbooks/infra_network.yml
tags: [infra, network, mtu, txqueuelen, sysctl]
timestamp: 2026-09-17T00:00:00Z
---

`infra_network.yml` applies network tuning to Data Store hosts.

## Plays

1. **Determine the servers that are on physical machines**
   (`all:!unmanaged_systems:!localhost`) — groups hosts into `physical` when
   `ansible_virtualization_type` is `NA` or `kvm`, otherwise `virtual`.
2. **Determine the NIC throughput** (`physical`) — reads the default
   interface's speed with `ethtool` and groups hosts into `network_10G`
   (10000 Mb/s or more) or `network_1G`. Nothing in this playbook targets
   those groups.
3. **Tune physical network** (`physical`):
   1. installs the NetworkManager package `community.general.nmcli` needs
      (`NetworkManager-tui` on CentOS, `network-manager` on Ubuntu,
      `NetworkManager` otherwise);
   2. sets the default interface's MTU to `infra_mtu` (default `1500`);
   3. sets its `txqueuelen` to `infra_txqueuelen` (default `1000`) with `ip link`;
   4. on Ubuntu 20.04 or later, persists the queue length with
      `templates/infra/etc/udev/rules.d/txqueuelen.rules.j2` installed as
      `/etc/udev/rules.d/50-txqueuelen.rules`.
4. **Tune TCP** (`all:!unmanaged_systems:!localhost`) — sets
   `net.<name>` = `<value>` for each entry of `infra_sysctl_net`
   (default `[]`). Tagged `no_testing`.

The play-3 task meant to persist the queue length on older Ubuntu and other
distributions has two `when` conditions that can't both be true
(`ansible_distribution != 'Ubuntu'` and `ansible_distribution == 'Ubuntu' and
… < 20.04`), so as written it never runs.

## Testing

`playbooks/tests/infra_network.yml` exists but contains only `TODO: implement`
debug tasks.

# Citations

[1] `playbooks/infra_network.yml` — the playbook.
[2] `playbooks/templates/infra/etc/udev/rules.d/txqueuelen.rules.j2` — the udev rule.
[3] `playbooks/group_vars/all/infra.yml` — `infra_mtu`, `infra_txqueuelen`,
`infra_sysctl_net` defaults.
[4] `playbooks/tests/infra_network.yml` — its placeholder test playbook.
