---
type: Playbook
title: sftp.yml
description: Installs and configures SFTPGo and the sftpgo-auth-irods plugin on the SFTP hosts, creates SFTPGo's iRODS proxy user, and wires an SFTPGo API key into the auth plugin.
resource: /playbooks/sftp.yml
tags: [sftp, sftpgo, irods, authentication]
timestamp: 2026-09-17T00:00:00Z
---

`sftp.yml` deploys the Data Store's SFTP service, SFTPGo backed by iRODS. See
[SFTP](/components/sftp.md) for the component. HAProxy forwards client SFTP
traffic to it; see [proxy.yml](/ansible-playbooks/proxy.md).

## Hosts

One play on `sftp` with `become: true` and `strategy: linear`.

## What it does

1. Sets `notifications_enabled` (tagged `no_testing`). The `Reload systemd`
   and `Restart sftpgo` handlers only run when this fact is set, so they're
   skipped under the testing harness.
2. Refreshes the apt cache and installs `curl` and `jq`.
3. From the control node, once, ensures the iRODS user
   `sftp_irods_proxy_username` (default `sftp`) exists as a `rodsadmin`, using
   [irods_user](/ansible-plugins/irods-user.md) as
   `sftp_irods_admin_username` (default `rods`) against the first
   `irods_catalog` host.
4. Writes the admin TLS certificate chain and key files from
   `sftp_admin_tls_cert_chain` and `sftp_admin_tls_key`. Both tasks are gated
   on `sftp_admin_tls_cert_chain|bool and sftp_admin_tls_cert_chain_file|bool`;
   the key task checks the chain variables rather than the key variables.
5. Installs SFTPGo when `/usr/bin/sftpgo` is missing, the `sftpgo` account is
   missing, the version isn't `2.7.3`, or the binary's checksum differs. It
   stops a running service, downloads
   `cyverse/sftpgo` release `v2.7.3i` from GitHub, creates the `sftpgo` system
   group and user (home `/var/lib/sftpgo`), and runs
   `playbooks/tasks/sftp/install_sftpgo.yml` as a handler to copy the binary
   and `/usr/share/sftpgo` into place.
6. Installs `sftpgo-auth-irods` `v0.2.0` from GitHub to `/usr/bin` if it's
   missing or a different version.
7. Creates the vault directory `sftp_vault_dir` (default `/sftpgo_vault`) with
   `data` and `backups` subdirectories (mode `0700`), `/var/log/sftpgo`,
   `/var/lib/sftpgo`, and `/etc/sftpgo`. It deletes `/var/lib/sftpgo/sftpgo.db`
   on every run; a comment says the database is recreated dynamically.
8. Renders `templates/sftp/etc/sftpgo/sftpgo.json.j2` and `sftpgo.conf.j2`
   into `/etc/sftpgo`.
9. Copies the host's ECDSA, Ed25519, and RSA SSH host key pairs, where present,
   from `/etc/ssh` to `/var/lib/sftpgo/id_*`, so SFTPGo presents the host's
   own keys.
10. Installs `files/sftp/usr/lib/systemd/system/sftpgo.service` and flushes
    handlers so SFTPGo is running.
11. Waits for SFTPGo's `/healthz` on `sftp_admin_ui_port` (default `18023`),
    gets an admin JWT, enables API-key auth for the admin, issues an API key
    named `sftpgo-auth-irods`, and uses `jq` to append
    `SFTPGO_API_BASE_URL` and `SFTPGO_API_KEY` to the first external command's
    environment in `sftpgo.json`. All of step 11 is tagged `no_testing`; the
    key-issuing tasks report `changed` on every run.
12. Installs `files/sftp/etc/update-motd.d/99-sftpgo`.

## Variables

Defaults from `playbooks/group_vars/all/sftp.yml`:

| Variable | Default |
| --- | --- |
| `sftp_admin_username` | `admin` |
| `sftp_admin_password` | required |
| `sftp_admin_ui_port` | `18023` |
| `sftp_admin_tls_cert_chain` / `sftp_admin_tls_key` | none |
| `sftp_admin_tls_cert_chain_file` / `sftp_admin_tls_key_file` | `''` |
| `sftp_irods_admin_username` | `rods` |
| `sftp_irods_admin_password` | required |
| `sftp_irods_proxy_username` | `sftp` |
| `sftp_irods_proxy_password` | required |
| `sftp_irods_host` | `localhost` |
| `sftp_irods_port` | `1247` |
| `sftp_irods_zone` | `tempZone` |
| `sftp_irods_auth_scheme` | `native` |
| `sftp_irods_ssl_ca_cert_path` / `sftp_irods_ssl_algorithm` | `''` |
| `sftp_irods_ssl_key_size` / `_salt_size` / `_hash_rounds` | `0` |
| `sftp_port` | `2022` |
| `sftp_proxy_allowed` | `[]` |
| `sftp_user_host_allowed` / `sftp_user_host_rejected` | `[]` |
| `sftp_vault_dir` | `/sftpgo_vault` |

## Testing

`playbooks/tests/sftp.yml`:

- renders `sftpgo.conf.j2` and `sftpgo.json.j2` with the defaults and asserts
  the admin username, home path, the iRODS environment passed to the auth
  command (proxy user, host, port, zone, auth scheme, SSL settings,
  `/tempZone/home/shared`), empty defender and proxy lists, backup and user
  directories, admin UI port `18023`, and SFTP port `2022`;
- renders `sftpgo.conf.j2` with `playbooks/tests/group_vars/sftp/cfg.yml` and
  checks the custom admin credentials and vault path;
- on the `sftp` hosts, checks that the `sftp` iRODS user is a `rodsadmin`, that
  the SFTPGo and auth-plugin binaries, configs, and service unit exist, that
  the `sftpgo` group and user exist, and that `/sftp_vault` and
  `/sftp_vault/data` are `0700` directories owned by `sftpgo` (the testing
  inventory sets `sftp_vault_dir: /sftp_vault`).

Several checks (TLS files, log/work/config directories, host keys, MOTD) are
`TODO implement` placeholders.

# Citations

[1] `playbooks/sftp.yml` — the playbook.
[2] `playbooks/tasks/sftp/install_sftpgo.yml` — the install handler's tasks.
[3] `playbooks/templates/sftp/etc/sftpgo/sftpgo.json.j2` and `sftpgo.conf.j2` — SFTPGo configuration.
[4] `playbooks/files/sftp/usr/lib/systemd/system/sftpgo.service` — the systemd unit.
[5] `playbooks/files/sftp/etc/update-motd.d/99-sftpgo` — the MOTD script.
[6] `playbooks/group_vars/all/sftp.yml` — SFTP variable defaults.
[7] `playbooks/tests/sftp.yml` — its test playbook.
[8] `testing/ansible-tester/inventory/group_vars/sftp.yml` — test values.
