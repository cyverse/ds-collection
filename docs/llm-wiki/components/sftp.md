---
type: Component
title: SFTP
description: The SFTPGo service in the sftp group that serves SFTP access to the Data Store, authenticating users against iRODS with the sftpgo-auth-irods hook.
resource: /playbooks/sftp.yml
tags: [sftp, sftpgo, irods, authentication]
timestamp: 2026-09-17T00:00:00Z
---

SFTP access runs on the hosts in the `sftp` inventory group using CyVerse's
fork of SFTPGo. HAProxy forwards client connections to it with the PROXY
protocol; see [HAProxy Proxy](/components/haproxy-proxy.md).

## Deployment

`sftp.yml` (apt-based hosts):

- Installs `curl` and `jq`, and from the control node ensures a `rodsadmin`
  iRODS user named `sftp_irods_proxy_username` exists on the first catalog
  provider.
- Installs SFTPGo `v2.7.3i` from `github.com/cyverse/sftpgo` when the binary,
  service account, version, or checksum differs, with an `sftpgo` system user
  and group.
- Installs `sftpgo-auth-irods` `v0.2.0` from
  `github.com/cyverse/sftpgo-auth-irods`.
- Creates the vault (`sftp_vault_dir`, with `data` and `backups`),
  `/var/log/sftpgo`, `/var/lib/sftpgo`, and `/etc/sftpgo`, and removes
  `/var/lib/sftpgo/sftpgo.db`, which SFTPGo recreates.
- Templates `/etc/sftpgo/sftpgo.json` and `/etc/sftpgo/sftpgo.conf`, copies the
  host's SSH host keys for SFTPGo's use, and installs the systemd unit and a
  message-of-the-day script.
- Outside testing, waits for the REST API, enables API-key auth for the admin,
  issues an API key for `sftpgo-auth-irods`, and patches it into the
  `sftpgo-auth-irods` command's environment in `sftpgo.json` as
  `SFTPGO_API_BASE_URL` and `SFTPGO_API_KEY`.

`sftp_start.yml` and `sftp_stop.yml` start/enable or stop/disable the
`sftpgo` service; both are tagged `no_testing`.

## Configuration

In `sftpgo.json`, the `common` section enables `proxy_protocol` with
`proxy_allowed` set from `sftp_proxy_allowed`, and the SFTP binding listens on
`sftp_port` and applies that proxy configuration. User homes live under
`<sftp_vault_dir>/data`, and `external_auth_hook` is
`/usr/bin/sftpgo-auth-irods`. The `command` section passes that program the
iRODS host, port, zone, proxy credentials, auth scheme, and SSL settings as
environment variables. The admin web UI listens on `sftp_admin_ui_port`, with
optional TLS files. `sftpgo.conf` sets the default admin credentials, home
path, log file, and `TZ="America/Phoenix"`.

## Key variables

Defaults come from `playbooks/group_vars/all/sftp.yml`; the full table is in
`playbooks/README.md`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `sftp_port` | `2022` | SFTP listen port |
| `sftp_admin_username` / `sftp_admin_password` | `admin` / required | SFTPGo admin |
| `sftp_admin_ui_port` | `18023` | Admin UI and REST API port |
| `sftp_irods_host` / `sftp_irods_port` / `sftp_irods_zone` | `localhost` / `1247` / `tempZone` | iRODS connection |
| `sftp_irods_proxy_username` / `sftp_irods_proxy_password` | `sftp` / required | iRODS proxy account |
| `sftp_irods_admin_username` / `sftp_irods_admin_password` | `rods` / required | Account used to create the proxy user |
| `sftp_irods_auth_scheme` | `native` | iRODS auth scheme |
| `sftp_proxy_allowed` | `[]` | Hosts allowed to send PROXY headers |
| `sftp_user_host_allowed` / `sftp_user_host_rejected` | `[]` / `[]` | Client source filters |
| `sftp_vault_dir` | `/sftpgo_vault` | Data and backup root |

# Citations

[1] `playbooks/sftp.yml` — installation and configuration.
[2] `playbooks/sftp_start.yml`, `playbooks/sftp_stop.yml` — service control.
[3] `playbooks/tasks/sftp/install_sftpgo.yml` — binary installation handler.
[4] `playbooks/templates/sftp/etc/sftpgo/sftpgo.json.j2`, `playbooks/templates/sftp/etc/sftpgo/sftpgo.conf.j2` — SFTPGo configuration.
[5] `playbooks/files/sftp/` — systemd unit and MOTD script.
[6] `playbooks/group_vars/all/sftp.yml` — variable defaults.
[7] `playbooks/README.md` — variable documentation.
