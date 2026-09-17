---
type: Runbook
title: Testing Roles with Molecule
description: The molecule scenarios under molecule/ that test the collection's roles — which role each exercises, its Docker platforms, shared irods_cfg fixtures, and version constraints.
resource: /molecule
tags: [testing, molecule, docker, roles, irods-cfg]
timestamp: 2026-09-17T00:00:00Z
---

The collection's roles are tested with [molecule](https://ansible.readthedocs.io/projects/molecule/)
using its Docker driver. Scenarios live at the repo root in `molecule/`, one
directory per scenario, rather than inside each role. Playbooks and plugins
use a different harness; see
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Running a scenario

Molecule finds scenarios in `molecule/<name>/`, so from the repo root:

```bash
molecule test -s <scenario>
```

Molecule and `molecule-plugins` come from `requirements.txt` (see
[Control Node Setup](/runbooks/control-node-setup.md)). Molecule is pinned
below 25 because, per `requirements.txt`, molecule 25 breaks collection path
determination. Most converge playbooks include roles by their fully qualified
names (`cyverse.ds.<role>`), so Ansible must be able to resolve this checkout
as the `cyverse.ds` collection. How that is arranged locally is not documented
in the repo.

## Scenarios

| Scenario | Role / tasks exercised | Platforms |
| --- | --- | --- |
| `firewalld` | [firewalld](/ansible-roles/firewalld.md) `main.yml`, then `mode_<service>.yml` | Built from `Dockerfile` (`ubuntu:24.04`), privileged, systemd |
| `haproxy` | [haproxy](/ansible-roles/haproxy.md) (referenced as `haproxy`, not FQCN) | Built from `Dockerfile` (`ubuntu:22.04`), privileged, systemd; sets `haproxy_vip_client_hosts` |
| `postgresql` | [postgresql](/ansible-roles/postgresql.md) | Built from `Dockerfile` (`ubuntu:20.04`), privileged, systemd |
| `postgresql_db` | [postgresql_db](/ansible-roles/postgresql-db.md) | Built from `Dockerfile` (`ubuntu:20.04`); runs PostgreSQL 12 directly as the container command |
| `rabbitmq` | [rabbitmq](/ansible-roles/rabbitmq.md) | Built from `Dockerfile` (`ubuntu:22.04`), privileged, systemd |
| `rabbitmq_vhost` | [rabbitmq_vhost](/ansible-roles/rabbitmq-vhost.md) | Built from `Dockerfile` (`rabbitmq:management`) |
| `irods_cfg_client` | [irods_cfg](/ansible-roles/irods-cfg.md) `client.yml` | CentOS 7 (`centos-archive`) and `ubuntu:bionic` |
| `irods_cfg_default` | `irods_cfg` internal `_system_account_own.yml`, with and without giving files irods ownership | `ubuntu:bionic` |
| `irods_cfg_initialize` | `irods_cfg` `setup_irods.yml` | A provider image built from `provider/Dockerfile` and an `ubuntu:bionic` consumer, both on a `molecule` network, plus an unconfigured `ubuntu:bionic` provider |
| `irods_cfg_update` | `irods_cfg` `main.yml` against existing configuration | CentOS 7 and `ubuntu:bionic` |
| `irods_cfg_upgrade` | `irods_cfg` `main.yml` after an upgrade setup | CentOS 7 and `ubuntu:bionic` |

`haproxy`, `postgresql_db`, `rabbitmq`, and `rabbitmq_vhost` declare a galaxy
dependency step using `requirements.yml`. All `irods_cfg_*` scenarios except
`irods_cfg_default` set `irods_cfg_validate: true` for their hosts.

## Shared irods_cfg fixtures

`molecule/_irods_cfg_shared/` is not a scenario; the `irods_cfg_*` scenarios
import from it:

- `centos.dockerfile` builds CentOS 7 with its yum repositories pointed at
  `vault.centos.org`.
- `prepare.yml` is imported by the `client`, `default`, and `upgrade`
  scenarios; `prepare_with_431.yml` imports `prepare.yml` and additionally
  installs and version-locks iRODS 4.3.1 packages on the CentOS and Ubuntu
  hosts, and installs PostgreSQL and creates the ICAT DB on the
  `irods_catalog` hosts; it is used by `initialize` and `update`.
- `tasks/validate_deposition.yml` is included from the `initialize` and
  `upgrade` verify playbooks.
- `base.yml` holds a galaxy dependency, Docker driver, and Ansible verifier
  config, but nothing in the repo references it.

## Idempotence exceptions

Molecule's idempotence stage skips tasks tagged
`molecule-idempotence-notest`. The tag is used in `roles/firewalld/tasks/main.yml`
and `molecule/irods_cfg_upgrade/converge.yml`. The playbook harness uses
`non_idempotent` instead; the two tags are not interchangeable.

# Citations

[1] `molecule/*/molecule.yml` — scenario drivers, platforms, and inventories.
[2] `molecule/*/converge.yml`, `prepare.yml`, `verify.yml` — scenario playbooks.
[3] `molecule/_irods_cfg_shared/` — shared irods_cfg fixtures.
[4] `requirements.txt` — molecule version pin and reason.
[5] `roles/firewalld/tasks/main.yml` — use of `molecule-idempotence-notest`.
