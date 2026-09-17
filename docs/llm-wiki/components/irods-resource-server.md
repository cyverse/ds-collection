---
type: Component
title: iRODS Resource Server
description: Catalog service consumers that host storage vaults, deployed either natively from OS packages or as a Docker Compose container.
resource: /playbooks/irods_resource_server.yml
tags: [irods, resource-server, consumer, docker, storage, vault]
timestamp: 2026-09-17T00:00:00Z
---

Resource servers are the hosts in the `irods_resource` inventory group. They
run iRODS with the `consumer` catalog service role, pointing at the hosts in
`irods_catalog`, and host unixfilesystem storage resources. The group has two
children with different deployment methods.

## Native resource servers (`irods_resource_native`)

`irods_resource_server.yml`:

1. Imports `irods_provision.yml` to install iRODS packages, the service
   account, and `/etc/hosts` entries.
2. Ensures the catalog providers are started.
3. From the control node, creates the clerver user as a `rodsadmin` and adds
   it to the `rodsadmin` group, using the first catalog provider's admin
   credentials (`irods_user` and `irods_group_member` modules).
4. Runs the `irods_cfg` role's `setup_irods.yml` with
   `irods_cfg_catalog_service_role: consumer` and no database settings, then
   starts iRODS.
5. Imports `irods_storage_resources.yml`, which creates each vault directory
   from `irods_storage_resources`, defines each storage resource with the
   `irods_unixfilesystem_resource` module, and imports
   `irods_free_space.yml` to initialize free space.

## Containerized resource servers (`irods_resource_container`)

`irods_resource_container.yml` supports AlmaLinux and Ubuntu hosts:

- Adds the Docker CE repository and installs Docker, the compose and buildx
  plugins, logrotate, and rsyslog. The Docker daemon logs to syslog with the
  tag `docker-<container name>`.
- Creates an `irods` system user in the `docker` group and the directories
  `/irods_vault`, `/etc/irods`, `/var/lib/irods/.irods`, and
  `/var/lib/irods/msiExecCmd_bin`.
- Installs `/var/lib/irods/irodsctl`, a wrapper that maps
  `start`/`stop`/`restart`/`status` onto `docker compose` commands.
- Copies `core.dvm` and `core.fnm`, templates `core.re`, and generates the
  iRODS config files with the `irods_cfg` role (schema validation off).
- Places the image source (`Dockerfile`, `entrypoint.sh`), a `.env` file, and
  `docker-compose.yml` under `/var/lib/irods`, then starts the compose
  project `cyverse`.
- Routes `docker-cyverse-irods*` syslog messages to
  `/var/log/irods/irods.log` and installs a logrotate config.

The image is built from `ubuntu:22.04` with `irods-server`, `irods-runtime`,
and `irods-icommands` pinned to `4.3.1`, and an `irods` user whose UID matches
the host's `irods` user. The container uses host networking, restarts on
failure, and bind-mounts the vault, `/etc/irods`, `/var/lib/irods/.irods`, and
(read-only) `msiExecCmd_bin`. Its entrypoint runs `iinit` against
`IRODS_CATALOG_PROVIDER` and then `irodsServer -u`.

Handlers rebuild the container, restart Docker, or run `irodsctl restart` only
outside the testing harness.

## Operations

- [irods_restart_rs](/ansible-playbooks/irods-restart-rs.md) restarts
  resource servers that aren't also catalog providers.
- [irods_stop_all](/ansible-playbooks/irods-stop-all.md) stops consumers
  before providers.
- [irods_free_space](/ansible-playbooks/irods-free-space.md) updates resource
  free space.
- [irods_check_routes](/ansible-playbooks/irods-check-routes.md) verifies
  port access between servers.

## Key variables

Defaults come from `playbooks/group_vars/all/irods.yml`; the full table,
including the `irods_storage_resources` entry fields (`name`, `vault`,
`context`), is in `playbooks/README.md`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `irods_storage_resources` | `[]` | Storage resources hosted on the server |
| `irods_default_vault` | none | Vault path; also `IRODS_VAULT_PATH` for containers |
| `irods_default_resource` | first `irods_resource_hierarchies` name | Default resource |
| `irods_server_port_range_start` / `_end` | `20000` / `20199` | Server port range |
| `irods_clerver_user` / `irods_clerver_password` | `rods` / `rods` | Clerver account |
| `irods_restart_allowed` | `false` | Whether handlers may restart native iRODS |

# Citations

[1] `playbooks/irods_resource_server.yml` — native resource server deployment.
[2] `playbooks/irods_storage_resources.yml` — vaults and storage resource definitions.
[3] `playbooks/irods_resource_container.yml` — containerized resource server deployment.
[4] `playbooks/files/irods/docker-rs/` — image source, compose file, and `irodsctl` wrapper.
[5] `playbooks/templates/irods/docker-rs/` — `.env` and `core.re` templates.
[6] `playbooks/group_vars/all/irods.yml` — variable defaults.
[7] `playbooks/README.md` — variable documentation.
