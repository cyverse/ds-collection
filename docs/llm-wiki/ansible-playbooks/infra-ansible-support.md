---
type: Playbook
title: infra_ansible_support.yml
description: Installs the packages Ansible needs on managed hosts, points CentOS 7 at the vault repositories, and removes unattended-upgrades from Ubuntu.
resource: /playbooks/infra_ansible_support.yml
tags: [infra, packages, centos, ubuntu, bootstrap]
timestamp: 2026-09-17T00:00:00Z
---

`infra_ansible_support.yml` prepares hosts so the rest of the collection's
playbooks can run on them.

## Hosts

All plays target `all:!unmanaged_systems:!localhost` with `become: true`.

## Plays

1. **Install ansible core facts requirement** (no fact gathering) — if
   `/etc/centos-release` exists, rewrites `/etc/yum.repos.d/CentOS-Base.repo`
   so the base, updates, and extras repositories point at
   `vault.centos.org/7.9.2009`; then installs `dmidecode` using the package
   manager named by `infra_package_manager` (default `auto`).
2. **Install required packages for ansible** —
   - on Ubuntu, refreshes the apt cache (tagged `non_idempotent`);
   - on CentOS, installs `epel-release`, `python2-pip`, and
     `yum-plugin-versionlock`, and upgrades pip2 via `get-pip.py` when
     `pip --version` doesn't report pip 20;
   - on every host, installs `acl`, `jq`, `python3`, `python3-pip`, and the
     distribution's equivalents of `iproute`, `python-dns`, `python-requests`,
     SELinux Python bindings, and `virtualenv`;
   - on Ubuntu 22.04 or later, installs `python-is-python3`.
3. **Remove packages on ubuntu** — removes `unattended-upgrades` from Ubuntu
   hosts. The task carries a tag named `idempotent`, which the testing harness
   doesn't use.

## Testing

`playbooks/tests/infra_ansible_support.yml` checks that the CentOS base repo
mentions `7.9.2009`, that the common, CentOS-specific, and Ubuntu-specific
packages are installed (using `playbooks/tests/tasks/test_pkg_installed.yml`),
that pip 20 is present on CentOS, that `python-is-python3` is installed on
Ubuntu 22.04+, and that `unattended-upgrades` is absent on Ubuntu. The CentOS
list checks `libselinux-python`, while the playbook installs
`libselinux-python3`.

# Citations

[1] `playbooks/infra_ansible_support.yml` — the playbook.
[2] `playbooks/group_vars/all/infra.yml` — `infra_package_manager` default.
[3] `playbooks/tests/infra_ansible_support.yml` — its test playbook.
