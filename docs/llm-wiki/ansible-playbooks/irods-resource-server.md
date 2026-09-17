---
type: Playbook
title: irods_resource_server.yml
description: Deploys native (non-containerized) iRODS resource servers — provisioning, clerver user creation on the catalog, initial iRODS setup as a catalog consumer, start, and storage resource creation.
resource: /playbooks/irods_resource_server.yml
tags: [irods, resource-server, catalog-consumer, deployment]
timestamp: 2026-09-17T00:00:00Z
---

`irods_resource_server.yml` stands up hosts in `irods_resource_native` that
aren't also catalog providers. Containerized resource servers use
[irods_resource_container.yml](/ansible-playbooks/irods-resource-container.md)
instead.

## Play order

1. Imports [irods_provision.yml](/ansible-playbooks/irods-provision.md).
2. **Ensure catalog service providers are started** (`irods_catalog`, as the
   service account): runs [irods_ctl](/ansible-plugins/irods-ctl.md) with its
   default state.
3. **Create clerver user** (`irods_resource_native:!irods_catalog`, delegated
   to the control node): ensures `_irods_clerver_user` exists as a
   `rodsadmin` with [irods_user](/ansible-plugins/irods-user.md) and belongs
   to the `rodsadmin` group with
   [irods_group_member](/ansible-plugins/irods-group-member.md). It connects
   to the first catalog provider with that provider's clerver credentials.
4. **Configure iRODS** (`irods_resource_native:!irods_catalog`, as the service
   account): includes the [irods_cfg role](/ansible-roles/irods-cfg.md) with
   `tasks_from: setup_irods.yml` and
   `irods_cfg_catalog_service_role: consumer`, with all `irods_catalog` hosts
   as providers and no database. Then it starts iRODS with `irods_ctl`.
5. Imports
   [irods_storage_resources.yml](/ansible-playbooks/irods-storage-resources.md).

The consumer play passes the same rule bases (`cve`, `cyverse_core`,
`cyverse_housekeeping` plus the static and templated rule files), command
scripts, ports, keys, and zone settings as the catalog provider play. Unlike
the consumer play in [irods_cfg.yml](/ansible-playbooks/irods-cfg.md), it
doesn't set `irods_cfg_database_user_password_salt`,
`irods_cfg_number_of_concurrent_delay_rule_executors`,
`irods_cfg_environment_variables`, or `irods_cfg_test_log`.

## Variables

Beyond those used by `irods_provision.yml`, the main inputs from
`playbooks/group_vars/all/irods.yml` are `irods_clerver_user` and
`irods_clerver_password` (both default `rods`), `irods_default_vault` (no
default), `irods_default_resource` (the first resource hierarchy's name),
`irods_storage_resources` (default `[]`), and `irods_zone_name` (default
`tempZone`).

## Tests

`playbooks/tests/irods_resource_server.yml` imports the provision test, checks
ownership of `/etc/irods` and `/var/lib/irods`, imports
`irods_rule_templates.yml`, and checks the deployed configuration files,
command scripts, `irods_environment.json`, and `server_config.json`. On the
`consumer_unconfigured` test host it verifies that the clerver user exists
and is in `rodsadmin`, and that iRODS is running. It ends by importing the
storage resources test.

## Related

- [iRODS Resource Server](/components/irods-resource-server.md)
- [irods_catalog_provider.yml](/ansible-playbooks/irods-catalog-provider.md)

# Citations

[1] `playbooks/irods_resource_server.yml` — the playbook.
[2] `roles/irods_cfg/tasks/setup_irods.yml` — setup tasks.
[3] `playbooks/group_vars/all/irods.yml` — variable defaults.
[4] `playbooks/tests/irods_resource_server.yml` — the test playbook.
