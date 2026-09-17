---
type: Playbook
title: irods_catalog_provider.yml
description: Fully deploys iRODS catalog service providers — provisioning, PostgreSQL client and ODBC setup, initial iRODS setup through the irods_cfg role, start, clerver authentication, and run-time initialization.
resource: /playbooks/irods_catalog_provider.yml
tags: [irods, catalog-provider, icat, postgresql, odbc, deployment]
timestamp: 2026-09-17T00:00:00Z
---

`irods_catalog_provider.yml` stands up the hosts in the `irods_catalog`
group, from bare OS to a running, initialized catalog service provider.

## Play order

1. **Enable test effects** (`hosts: all`): sets `_test_log: true`, then
   `false` in a task tagged `no_testing`. The value is passed to the
   `irods_cfg` role and `irods_ctl` module as `test_log`.
2. Imports [irods_provision.yml](/ansible-playbooks/irods-provision.md).
3. **Provision additional for catalog service providers** (`irods_catalog`,
   `become: true`):
   - sets `kernel.<name>` sysctls from `_irods_sysctl_kernel` (tagged
     `no_testing`);
   - writes `/etc/security/limits.d/irods.conf` with a soft `nofile` limit of
     2000 for the service account;
   - pip-installs `pika>=1.2`;
   - **CentOS**: builds and pip-installs `pyodbc` (no system package exists on
     CentOS 7), installs `mailx`, adds the PostgreSQL 12 archive yum repo,
     installs `postgresql12` and `postgresql12-odbc`, copies
     `files/irods/etc/profile.d/*` to put the PostgreSQL 12 clients on the
     path, registers the PostgreSQL 12 ODBC driver with `odbcinst` from
     `files/irods/postgresql-odbc-tmpl.ini`, and version-locks
     `irods-database-plugin-postgres` (tagged `non_idempotent` because of
     community.general issue 4470);
   - **Ubuntu**: installs `bsd-mailx`, the PostgreSQL apt archive key and
     source, `odbc-postgresql`, and `postgresql-client-12`;
   - installs `irods-database-plugin-postgres` and runs
     `tasks/irods/ensure_irods_ownership.yml`.
4. **Configure iRODS on catalog service providers** (`irods_catalog`, as the
   service account with `become_flags: -i`):
   - includes the [irods_cfg role](/ansible-roles/irods-cfg.md) with
     `tasks_from: setup_irods.yml`, which initializes the ICAT DB and deploys
     the server configuration;
   - starts iRODS with [irods_ctl](/ansible-plugins/irods-ctl.md);
   - authenticates the clerver with
     [irods_clerver_auth](/ansible-plugins/irods-clerver-auth.md).
5. Imports [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md).

## irods_cfg settings

The role variables match those in
[irods_cfg.yml](/ansible-playbooks/irods-cfg.md)'s catalog provider play:

- `irods_cfg_catalog_provider_hosts` is the host itself.
- `irods_cfg_database` points at `_irods_dbms_host`/`_irods_dbms_port` using
  the `_irods_odbc_driver` ODBC driver.
- `irods_cfg_environment_variables` sets `IRODS_AMQP_URI` (built from the
  `irods_amqp_*` variables, with `/` in the vhost encoded as `%2F`) and the
  `IRODS_DB_*` connection values.
- `irods_cfg_re.additional_rulebases` is `cve`, `cyverse_core`, and
  `cyverse_housekeeping`.
- Static rule bases come from `files/irods/etc/irods/*.re`, templated ones
  from `templates/irods/etc/irods/*.re.j2`, and command scripts from
  `files/irods/var/lib/irods/msiExecCmd_bin/*`.
- `irods_cfg_zone_user` and `irods_cfg_zone_password` are the clerver
  credentials.

See [iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md)
for what those files are.

## Variables

From `playbooks/group_vars/all/irods.yml` (not exhaustive):

| Variable | Default |
| --- | --- |
| `irods_version` | `4.3.1` |
| `irods_dbms_host` | first host in `irods_catalog` |
| `irods_dbms_port` | `5432` |
| `irods_db_username` / `irods_db_password` | `irods` / `testpassword` |
| `irods_odbc_driver` | `PostgreSQL` |
| `irods_amqp_host` / `irods_amqp_port` / `irods_amqp_vhost` | `localhost` / `5672` / `/` |
| `irods_clerver_user` / `irods_clerver_password` | `rods` / `rods` |
| `irods_zone_name` | `tempZone` |
| `irods_resource_hierarchies` | `[ { "name": "demoResc" } ]` |
| `irods_max_num_re_procs` | `4` |
| `irods_sysctl_kernel` | `[]` |
| `irods_become_svc_acnt` | `true` |

The zone port (1247), control plane port (1248), client-server policy
(`CS_NEG_REFUSE`), and hash scheme (`MD5`) are internal constants in the
same file.

## Tests

`playbooks/tests/irods_catalog_provider.yml` imports the provision test,
then checks the limits file, `pika`, the distribution-specific PostgreSQL
client and ODBC setup, the `irods-database-plugin-postgres` install and lock,
and ownership. It imports `irods_rule_templates.yml`, checks the deployed
configuration files, command scripts, `irods_environment.json`, and
`server_config.json` contents, confirms iRODS is running and the clerver
auth file exists, and finally imports the run-time initialization test.

## Related

- [iRODS Catalog Provider](/components/irods-catalog-provider.md)
- [ICAT DBMS](/components/icat-dbms.md)
- [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md)

# Citations

[1] `playbooks/irods_catalog_provider.yml` — the playbook.
[2] `playbooks/files/irods/postgresql-odbc-tmpl.ini` — ODBC driver definition for CentOS.
[3] `playbooks/files/irods/etc/profile.d/` — PostgreSQL 12 client path scripts.
[4] `roles/irods_cfg/tasks/setup_irods.yml` — ICAT setup tasks.
[5] `playbooks/group_vars/all/irods.yml` — variable defaults.
[6] `playbooks/tests/irods_catalog_provider.yml` — the test playbook.
