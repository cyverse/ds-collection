---
type: Playbook
title: irods_resource_container.yml
description: Deploys containerized iRODS resource servers on AlmaLinux and Ubuntu hosts — installs Docker, generates the iRODS configuration with irods_cfg, and builds and runs an iRODS 4.3.1 resource server image with docker compose.
resource: /playbooks/irods_resource_container.yml
tags: [irods, resource-server, docker, container, almalinux, ubuntu]
timestamp: 2026-09-17T00:00:00Z
---

`irods_resource_container.yml` targets the `irods_resource_container` group
with `become: true`. These hosts run the iRODS resource server inside a
Docker container instead of from host packages, so
[irods_provision.yml](/ansible-playbooks/irods-provision.md) skips them.

## What it does

**Pre-tasks** set `_enable_notifications: true` (tagged `no_testing`, so
handlers don't fire in the test harness) and add the Docker package
repository: `dnf config-manager --add-repo` on AlmaLinux, or a keyring plus
`docker.list` apt source on Ubuntu.

**Tasks** refresh the package cache, install `docker-ce`, `docker-ce-cli`,
`containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`,
`logrotate`, and `rsyslog`, and start `rsyslog` and `docker` (both tagged
`no_testing`). They also write `/etc/docker/daemon.json` so containers log to
syslog with the tag `docker-<container name>`.

**Post-tasks**:

1. Create the system user `irods` (home `/var/lib/irods`, in the `docker`
   group) and the directories `/irods_vault`, `/etc/irods`,
   `/var/lib/irods/.irods`, and `/var/lib/irods/msiExecCmd_bin`.
2. Install `files/irods/docker-rs/irodsctl` as `/var/lib/irods/irodsctl`, a
   wrapper that maps `start`, `stop`, `restart`, and `status` onto
   `docker compose` commands for the compose project in `/var/lib/irods`.
3. Copy `core.dvm` and `core.fnm` from `files/irods/docker-rs/run/etc/irods/`
   and render `templates/irods/docker-rs/run/etc/irods/core.re.j2` into
   `/etc/irods/`.
4. Import the [irods_cfg role](/ansible-roles/irods-cfg.md) as a consumer
   with `irods_cfg_chown: false`, `irods_cfg_validate: false`,
   `irods_cfg_schema_validation_base_uri: 'off'`, `irods_cfg_host` set to the
   inventory hostname, no database settings, rule bases from
   `files/irods/etc/irods/*` and `templates/irods/etc/irods/*`, and command
   scripts from `files/irods/var/lib/irods/msiExecCmd_bin/*`. A change
   notifies `Restart irods`.
5. Copy `Dockerfile` and `entrypoint.sh` into `/var/lib/irods/build`, render
   `templates/irods/docker-rs/env.j2` to `/var/lib/irods/.env`, and copy
   `docker-compose.yml` to `/var/lib/irods/`.
6. Configure rsyslog to send `docker-cyverse-irods*` messages to
   `/var/log/irods/irods.log`, and install the same logrotate template as
   [irods_log.yml](/ansible-playbooks/irods-log.md).
7. Start the compose project with `community.docker.docker_compose_v2`
   (`pull: never`, tagged `no_testing`).

Handlers rebuild the compose project, restart Docker, run
`irodsctl restart`, or restart rsyslog. All except `Update apt cache` are
gated on `_enable_notifications`.

## The container

`files/irods/docker-rs/docker-compose.yml` defines project `cyverse` with one
service, `irods-rs`. It builds from `build/`, uses host networking, restarts
on failure, and bind-mounts the vault, `/etc/irods`,
`/var/lib/irods/.irods`, `msiExecCmd_bin` (read-only), and the
America/Phoenix zoneinfo file. The Dockerfile starts from `ubuntu:22.04` and
installs `irods-icommands`, `irods-runtime`, and `irods-server` pinned to
4.3.1. The `.env` file supplies the first catalog provider, the host
`irods` UID, the port range, the clerver password, `_irods_default_vault` as
the vault path, the zone name, and the zone port.

## Notes

- The account name `irods` is hardcoded in this playbook rather than taken
  from `_irods_service_account_name`, although the `irods_cfg` role is passed
  that variable.
- `irods_rs_image`, `irods_publish_rs_image`, and `irods_build_dir` have
  defaults in `playbooks/group_vars/all/irods.yml`, but no playbook or role
  references them.

## Tests

`playbooks/tests/irods_resource_container.yml` has real checks for the Docker
repository setup and packages, `daemon.json` contents, the `irods` user and
its `docker` membership, the directories, the `irodsctl` adapter, the runtime
config files (`core.dvm`, `core.fnm`, `core.re`), command scripts, the
service account name in `service_account.config`, and some
`server_config.json` fields. The template expansion plays on localhost and
the checks for rule base staging, the remaining `server_config.json` fields,
`irods_environment.json`, the build directory, image source, `.env`,
`docker-compose.yml`, rsyslog config, and logrotate config are placeholder
`debug` tasks reading `TODO: implement`.

## Related

- [iRODS Resource Server](/components/irods-resource-server.md)
- [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md)

# Citations

[1] `playbooks/irods_resource_container.yml` — the playbook.
[2] `playbooks/files/irods/docker-rs/` — compose file, image build files, `irodsctl` adapter, and runtime config.
[3] `playbooks/templates/irods/docker-rs/` — `.env` and `core.re` templates.
[4] `playbooks/group_vars/all/irods.yml` — variable defaults.
[5] `playbooks/tests/irods_resource_container.yml` — the test playbook.
