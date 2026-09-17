---
type: Role
title: irods_cfg Role
description: The cyverse.ds.irods_cfg role, which generates iRODS 4.3.1 configuration files (irods_environment.json, server_config.json, service_account.config), deploys rule bases and command scripts, and can initialize a new server with setup_irods.py.
resource: /roles/irods_cfg/README.md
tags: [role, irods, configuration, icat, rule-engine]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.irods_cfg` maintains the configuration of an iRODS server or client
once iRODS is installed. Its README says it requires iRODS 4.3.1 and will
eventually configure an iRODS server completely. For now it maintains
`irods_environment.json`, `etc/irods/server_config.json`, and
`etc/irods/service_account.config`, and it also deploys rule bases and command
scripts.

## Task files

| File | Purpose |
| --- | --- |
| `main.yml` | Imports `server.yml`; the default for a server. |
| `server.yml` | Generates `service_account.config`, copies `irods_cfg_cmd_scripts` into `var/lib/irods/msiExecCmd_bin/`, templates `irods_cfg_rulebases_templated` and copies `irods_cfg_rulebases_static` into `etc/irods/` (both notify `Reload rules`), generates `server_config.json`, and generates the server version of `irods_environment.json`. |
| `client.yml` | Generates the client version of `irods_environment.json` (`irods_cfg_for_server: false`). |
| `irods_environment.yml` | Validates the environment variables if `irods_cfg_validate` is true, then renders `irods_cfg_environment_file`. For a server it loads `vars/irods_environment_server.yml` first. |
| `server_config.yml` | Loads `vars/server_config.yml`, validates ICAT, federation, port-range, key-length, and other settings if `irods_cfg_validate` is true, then renders `etc/irods/server_config.json`. |
| `service_account.yml` | Renders `etc/irods/service_account.config`. |
| `setup_irods.yml` | Not part of `main.yml`. If `var/lib/irods/version.json` is missing, renders `/tmp/setup_configuration.json` and runs `python3 /var/lib/irods/scripts/setup_irods.py`, then imports `server.yml`. If setup fails, it removes `version.json` and fails. |
| `_cfg_template.yml` | Internal helper. Creates the parent directory and templates a file with `backup: true`, owned by the service account, and notifies `Restart iRODS`. |
| `_system_account_own.yml` | Internal helper. Gives the service account ownership of a path when `irods_cfg_chown` is true. |

All generated paths are prefixed with `irods_cfg_root_dir` (default `/`). The
JSON files are built from macros in `templates/macros.j2`, and the config files
use schema version `v4`.

### Workaround for irods/irods#8297

`setup_irods.py` is given a stub default resource named
`tmp-<inventory_hostname_short>`. After setup, `setup_irods.yml` replaces that
name with `irods_cfg_default_resource_name` in `/etc/irods/core.re` and deletes
the stub resource with `iadmin rmresc`. Both steps are marked as a workaround
for https://github.com/irods/irods/issues/8297.

## Handlers

- `Reload rules` touches `etc/irods/core.re`.
- `Restart iRODS` runs only when `irods_cfg_restart_allowed` is true, and uses
  the [irods_ctl module](/ansible-plugins/irods-ctl.md) with
  `state: restarted_if_running` and `test_log: irods_cfg_test_log`.

## Variables

None of the role variables are required. The README table documents about 90
of them; this is a summary by group, so consult `roles/irods_cfg/README.md` and
`roles/irods_cfg/defaults/main.yml` for the full list.

- **Role behavior** — `irods_cfg_catalog_service_role` (`provider` or
  `consumer`, default `provider`), `irods_cfg_validate` (default `false`),
  `irods_cfg_restart_allowed` (default `false`), `irods_cfg_test_log`,
  `irods_cfg_chown` (default `true`), `irods_cfg_root_dir`, and
  `irods_cfg_for_server`.
- **Service account** — `irods_cfg_system_account_name` (default `irods`) and
  `irods_cfg_system_group_name`.
- **Zone and catalog** — `irods_cfg_zone_name` (default `tempZone`),
  `irods_cfg_zone_user` (default `rods`), `irods_cfg_zone_password`,
  `irods_cfg_zone_key`, `irods_cfg_zone_port`, `irods_cfg_zone_auth_scheme`,
  `irods_cfg_catalog_provider_hosts`, `irods_cfg_negotiation_key`,
  `irods_cfg_federation`, and `irods_cfg_database` (an object with `db_host`,
  `db_name`, `db_odbc_driver`, `db_password`, `db_port`, and `db_username`,
  used only for a provider).
- **Server behavior** — ports and port ranges, control plane settings,
  transfer buffer and thread settings, hash scheme and policy, delay rule
  executors and sleep times, temporary password lifetimes, log levels,
  `irods_cfg_access_entries`, `irods_cfg_host_entries`,
  `irods_cfg_controlled_user_connection_list`, `irods_cfg_environment_variables`,
  and `irods_cfg_default_resource_name` (default `demoResc`) and its directory.
- **Rule engine** — `irods_cfg_re` (`null` by default; an object with
  `additional_rulebases`, `additional_data_variable_mappings`, and
  `additional_function_name_mappings`), `irods_cfg_rule_engine_namespaces`,
  `irods_cfg_rulebases_static`, `irods_cfg_rulebases_templated`, and
  `irods_cfg_cmd_scripts`.
- **Client environment** — `irods_cfg_environment_file`, `irods_cfg_host`,
  `irods_cfg_home`, `irods_cfg_cwd`, `irods_cfg_authentication_file`, and the
  `irods_cfg_client_*` and `irods_cfg_ssl_*` settings.

When `irods_cfg_re` is null, `mk_rule_engines` renders an empty `rule_engines`
list. When it is set, the list holds the iRODS rule language plugin and the
C++ default policy plugin.

## Playbooks that use the role

| Playbook | How |
| --- | --- |
| [irods_cfg.yml](/ansible-playbooks/irods-cfg.md) | `import_role` for providers (`provider`) and resource servers (`consumer`) |
| [irods_catalog_provider.yml](/ansible-playbooks/irods-catalog-provider.md) | `include_role` with `tasks_from: setup_irods.yml` |
| [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md) | `include_role` with `tasks_from: setup_irods.yml`, role `consumer` |
| [irods_resource_container.yml](/ansible-playbooks/irods-resource-container.md) | `import_role` to generate config files, role `consumer` |
| [webdav.yml](/ansible-playbooks/webdav.md) | `include_role` with `tasks_from: client.yml`, writing `etc/httpd/irods/irods_environment.json` with `irods_cfg_chown: false` |

## Molecule scenarios

The scenarios share files in `molecule/_irods_cfg_shared/`:

- `base.yml` — galaxy dependency, docker driver, and ansible verifier settings;
- `prepare.yml` — groups hosts by OS, updates apt on Ubuntu, installs pip and
  `jsonschema`;
- `prepare_with_431.yml` — preparation with iRODS 4.3.1 installed;
- `centos.dockerfile`;
- `tasks/validate_deposition.yml`.

| Scenario | Platforms | What it exercises and verifies |
| --- | --- | --- |
| `irods_cfg_default` | Ubuntu bionic | Converges only `_system_account_own.yml`. `verify.yml` renders the templates locally and checks the client and server `irods_environment.json`, `server_config.json`, `service_account.config`, and `setup_configuration.json` for default and custom values (options in `vars/`), plus ownership assignment with `irods_cfg_chown` true and false. |
| `irods_cfg_client` | CentOS, Ubuntu bionic | Runs `client.yml` with defaults and with a custom environment file path. Verifies both files were deposited and validate against the iRODS 4.3.1 client environment JSON schema. |
| `irods_cfg_initialize` | A provider image, an Ubuntu consumer, and an unconfigured Ubuntu provider | Runs `setup_irods.yml`. Verifies the ICAT schema version and admin password, deposition of `server_config.json`, `irods_environment.json`, and `service_account.config`, that the old config isn't deposited, and that `core.re` names the default resource `ingestRes`. |
| `irods_cfg_update` | CentOS, Ubuntu bionic | Initializes iRODS, then runs `main.yml` with artifacts from `artifacts/`. Verifies command script and rule base deposition and the contents of static and templated rule bases. |
| `irods_cfg_upgrade` | CentOS, Ubuntu bionic | Installs iRODS 4.2.8, upgrades to 4.3.1, patches config files with the [json_patch module](/ansible-plugins/json-patch.md) (see https://github.com/irods/irods/issues/8052), then runs `main.yml`. Verifies deposition of the three config files and that the old config isn't deposited. |

See [Testing Roles with Molecule](/runbooks/testing-roles-with-molecule.md).

## Notes

The README and the code disagree in a few places:

- The README gives `irods_cfg_re` a default of `core` and describes a `core`
  value; `defaults/main.yml` sets it to `null`.
- The README's client example includes a task file `init_zone_user.yml` that
  doesn't exist in `tasks/`.
- The README calls the ICAT type field `db_type`, but `vars/main.yml` reads
  `irods_cfg_database.catalog_database_type`, defaulting to `postgres`.
- The federation table lists `catalog_provider_hosts`, while the README's
  provider example uses `icat_host`.

# Citations

[1] `roles/irods_cfg/README.md` — role description, variable tables, and example playbooks.
[2] `roles/irods_cfg/tasks/` — all task files.
[3] `roles/irods_cfg/defaults/main.yml` — variable defaults.
[4] `roles/irods_cfg/vars/` — `main.yml`, `server_config.yml`, and `irods_environment_server.yml`.
[5] `roles/irods_cfg/templates/` — `macros.j2` and the config file templates.
[6] `roles/irods_cfg/handlers/main.yml` — handlers.
[7] `molecule/_irods_cfg_shared/`, `molecule/irods_cfg_default/`, `molecule/irods_cfg_client/`, `molecule/irods_cfg_initialize/`, `molecule/irods_cfg_update/`, `molecule/irods_cfg_upgrade/` — molecule scenarios.
[8] `playbooks/irods_cfg.yml`, `playbooks/irods_catalog_provider.yml`, `playbooks/irods_resource_server.yml`, `playbooks/irods_resource_container.yml`, `playbooks/webdav.yml` — playbooks using the role.
