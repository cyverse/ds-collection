---
type: Runbook
title: Control Node Setup
description: One-time preparation of an Ansible control node or development machine for the cyverse.ds collection — Docker, system packages, Python requirements, Galaxy dependencies, and rng-tools.
resource: /README.md
tags: [setup, prerequisites, ansible, docker, pip, galaxy, rng-tools]
timestamp: 2026-09-17T00:00:00Z
---

Before deploying or developing the Data Store with this collection, the admin
host (Ansible control node) and every development machine need Docker, a few
system packages, and the Python and Galaxy dependencies the playbooks and
testing harness use. The repo README states that only Ubuntu 22.04 is
supported for this.

## Once per host

1. Configure Docker's apt repository:

   ```shell
   sudo apt install ca-certificates curl gnupg lsb-release
   sudo mkdir --parents /etc/apt/keyrings
   curl --fail --location --silent --show-error https://download.docker.com/linux/ubuntu/gpg \
      | sudo gpg --dearmor --output /etc/apt/keyrings/docker.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
         https://download.docker.com/linux/ubuntu \
         $(lsb_release --codename --short) stable" \
      | sudo tee /etc/apt/sources.list.d/docker.list
   sudo apt update
   ```

2. Install the system packages:

   ```shell
   sudo apt install \
      dmidecode docker-ce docker-compose-plugin git jq python-is-python3 python3 python3-pip rpm
   ```

3. Enable and start Docker:

   ```shell
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

## Once per person

1. Add the person (here `DEVELOPER`) to the `docker` group:

   ```shell
   sudo usermod --append --groups docker DEVELOPER
   ```

2. Install the Python packages from `requirements.txt`:

   ```shell
   pip install --requirement requirements.txt
   ```

   Two pins in that file carry explanations:

   | Pin | Reason given in `requirements.txt` |
   | --- | --- |
   | `ansible-core<2.17` | 2.17 and later don't work on CentOS 7 and Ubuntu 18.04 managed hosts |
   | `molecule<25` | molecule 25 breaks collection path determination |

   The rest are unpinned: `ansible-lint`, `dnspython`, `docker`, `jsonschema`,
   `molecule-plugins`, `netaddr`, `paramiko`, `python-irodsclient`,
   `requests`, `scp`, and `tox-ansible`.

3. Install the Galaxy collections and roles from `requirements.yml`:

   ```shell
   ansible-galaxy install --role-file requirements.yml
   ```

   This brings in `ansible.netcommon`, `ansible.posix`, `ansible.utils`,
   `community.docker` 4.5.0, `community.general` 10.6.0,
   `community.postgresql` 3.11.0, and `community.rabbitmq`, plus the roles
   `adfinis_sygroup.grub` and `geerlingguy.apache`.

## Entropy on every VM

All VMs, including the control node if it is a VM, must get `rng-tools`
through the [infra_rng_tools](/ansible-playbooks/infra-rng-tools.md)
playbook. The README gives the reason: Ansible tasks need enough entropy to
generate random numbers without pausing mid-deployment. The playbook targets
`all:!unmanaged_systems:!localhost`, so a control node that is `localhost` in
the inventory is not covered by it.

## Discrepancies

- The README's pip package list includes `wheel`, but `requirements.txt` does
  not.

# Citations

[1] `README.md` — prerequisites and setup steps.
[2] `requirements.txt` — Python dependencies and pin reasons.
[3] `requirements.yml` — Galaxy collections and roles.
[4] `playbooks/infra_rng_tools.yml` — installs `rng-tools`.
