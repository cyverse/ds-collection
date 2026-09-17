---
type: Playbook
title: irods_hosts.yml
description: Maintains a managed block in /etc/hosts on iRODS hosts that resolves the DBMS, catalog providers, resource servers, federated providers, AMQP broker, and other listed names.
resource: /playbooks/irods_hosts.yml
tags: [irods, networking, hosts-file]
timestamp: 2026-09-17T00:00:00Z
---

`irods_hosts.yml` targets `irods:!unmanaged_systems` with `become: true`.
The whole play is tagged `no_testing`, because `/etc/hosts` can't be
modified inside the test containers.

## What it does

A single `blockinfile` task writes a block between
`# BEGIN DS MANAGED BLOCK` and `# END DS MANAGED BLOCK` markers. Each entry
is resolved on the control node with `lookup('dig', ...)`, and names that
are already IP addresses are skipped. The block contains:

- the ICAT DBMS host (`_irods_dbms_host`), only on catalog providers that
  aren't themselves the DBMS host, and only if it isn't `localhost`;
- every other host in `irods_catalog`;
- every other host in `irods_resource` that isn't also a catalog provider;
- the `catalog_provider_hosts` of each zone in `_irods_federation`;
- the AMQP host (`_irods_amqp_host`), only on catalog providers that aren't
  the AMQP host;
- each name in `_irods_other_host_entries`.

## Variables

| Variable | Default |
| --- | --- |
| `irods_dbms_host` | first host in `irods_catalog` |
| `irods_amqp_host` | `localhost` |
| `irods_federation` | `[]` |
| `irods_other_host_entries` | `[]` |

## Used by

Imported at the end of
[irods_provision.yml](/ansible-playbooks/irods-provision.md).

## Tests

There is no `playbooks/tests/irods_hosts.yml`.

# Citations

[1] `playbooks/irods_hosts.yml` — the playbook.
[2] `playbooks/group_vars/all/irods.yml` — variable defaults.
