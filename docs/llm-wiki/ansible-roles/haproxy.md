---
type: Role
title: haproxy Role
description: The cyverse.ds.haproxy role, which installs HAProxy and renders its configuration for the iRODS, SFTP, WebDAV, and stats front ends, with connection tracking and allow, block, and VIP address lists.
resource: /roles/haproxy/tasks/main.yml
tags: [role, haproxy, proxy, irods, sftp, webdav]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.haproxy` installs and configures the HAProxy load balancer that
fronts the Data Store. The role has no README. `playbooks/proxy.yml` applies it
to the `proxy` inventory group; see [proxy.yml](/ansible-playbooks/proxy.md) and
[HAProxy Proxy](/components/haproxy-proxy.md).

## Task files

`tasks/main.yml` imports `install.yml` and then `configure.yml`.

**`install.yml`** refreshes the apt cache when the package manager is apt,
installs `haproxy` and `socat`, and enables the service. It also sets
`net.ipv4.ip_nonlocal_bind` and `net.ipv4.ip_forward` to `1` in
`/etc/sysctl.d/haproxy.conf`. The service-enable and sysctl tasks are tagged
`no_testing`.

**`configure.yml`**:

- when SELinux is enabled, labels the stats port `tor_port_t` and turns on the
  `haproxy_connect_any` boolean;
- adds a managed block to `/etc/rsyslog.conf` so rsyslog listens on UDP
  127.0.0.1:514, and installs `/etc/rsyslog.d/haproxy.conf` and
  `/etc/logrotate.d/haproxy`, so logs go to `/var/log/haproxy/haproxy.log` and
  `haproxy.err`;
- writes the TLS certificate to `haproxy_tls_crt` when both it and
  `haproxy_tls_crt_content` are set;
- renders `allow.lst.template`, `block.lst.template`, and `vip.lst` in
  `/etc/haproxy/`, then copies the two templates to `allow.lst` and `block.lst`
  only if those files don't exist yet, so edits made on the host survive;
- renders `/etc/haproxy/haproxy.cfg`.

## Generated configuration

`templates/haproxy.cfg.j2` defines these sections:

| Section | Behavior |
| --- | --- |
| `listen stats` | HTTP stats at `/stats` and a Prometheus exporter at `/metrics` on `haproxy_stats_port`, with TLS when `haproxy_tls_crt` is set and basic auth when `haproxy_stats_auth` is set (username defaults to `ds`) |
| `backend concurrency_st` | A stick table tracking current connections per source IP |
| `frontend irods_main` | Listens on `haproxy_irods_port`. It inspects the iRODS message header, accepts `HEARTBEAT` and VIP-source `RODS_CONNECT` messages outright, rejects anything else that isn't `RODS_CONNECT`, rejects sources with more than 10 connections, and routes sources with more than 1 connection to `irods_throttled` |
| `frontend irods_reconn` | Listens on `haproxy_irods_reconn_ports` and forwards straight to `irods_direct` |
| `backend irods_throttled` / `frontend irods_indirect` | Loop through a Unix socket so throttled connections are capped at `haproxy_irods_throttled_max_conn` |
| `backend irods_direct` | The iRODS server `haproxy_irods_host`; health checks are commented out in the template |
| `listen sftp` | Listens on `haproxy_sftp_port`, rejects non-VIP sources with more than 10 connections, and forwards to the first SFTP host on `haproxy_sftp_backend_port` with PROXY protocol v2 |
| `listen webdav` | HTTP on `haproxy_webdav_port`. Denies non-VIP sources that are in `block.lst` but not `allow.lst`, and non-VIP sources with more than 10 connections. With TLS configured it redirects to HTTPS, otherwise it forwards to the first WebDAV host |
| `listen webdavs` | Rendered only with TLS. HTTPS on `haproxy_webdav_tls_port`; denied requests get a 307 redirect to `https://unblockme.cyverse.org/` |

Host names in the address lists and server lines are resolved with a `dig`
lookup at render time.

## Variables

| Variable | Default |
| --- | --- |
| `haproxy_allow_client_hosts`, `haproxy_block_client_hosts`, `haproxy_vip_client_hosts` | `[]` |
| `haproxy_default_check_period` | `10s` |
| `haproxy_default_max_conn` | `500` |
| `haproxy_irods_host` / `haproxy_irods_port` | `localhost` / `1247` |
| `haproxy_irods_reconn_ports` | `20000-20199` |
| `haproxy_irods_direct_max_conn`, `haproxy_irods_throttled_max_conn` | `haproxy_default_max_conn` |
| `haproxy_num_threads` | `1` |
| `haproxy_queue_timeout` | `null` (no `timeout queue` line) |
| `haproxy_restart_allowed` | `false` |
| `haproxy_sftp_hosts` / `haproxy_sftp_port` / `haproxy_sftp_backend_port` | `[localhost]` / `22` / `2022` |
| `haproxy_stats_auth` / `haproxy_stats_port` | `null` / `8404` |
| `haproxy_tls_crt` / `haproxy_tls_crt_content` | `null` / `null` |
| `haproxy_webdav_hosts` / `haproxy_webdav_port` / `haproxy_webdav_tls_port` | `[localhost]` / `80` / `443` |

`haproxy_default_client_hosts`, `haproxy_rsyslog_conf`, and the `*_check_period`
variables are also defined in `defaults/main.yml`.

## Handlers

`Reload haproxy` reloads the service. `Restart haproxy` restarts it only when
`haproxy_restart_allowed` is true; otherwise the
[warn_if_false](/ansible-plugins/warn-if-false.md) test prints a "RESTART
REQUIRED" warning. `Restart rsyslog` restarts rsyslog and then triggers a
reload.

## Molecule scenario

`molecule/haproxy` converges the role on an Ubuntu 22.04 container with
`haproxy_restart_allowed: true`. `verify.yml` checks the rendered address list
and `haproxy.cfg` against the defaults (threads, `maxconn`, stats port, iRODS,
SFTP, and WebDAV sections) and against custom values in
`vars/custom_haproxy_vars.yml` (threads, queue timeout, TLS stats bind, stats
auth). On the instance it checks that haproxy is installed, the rsyslog block
and config and the logrotate file are in place, and `vip.lst` exists. Many
other checks are `debug` placeholders marked TODO. See
[Testing Roles with Molecule](/runbooks/testing-roles-with-molecule.md).

# Citations

[1] `roles/haproxy/tasks/` — `main.yml`, `install.yml`, and `configure.yml`.
[2] `roles/haproxy/templates/haproxy.cfg.j2` — the HAProxy configuration template.
[3] `roles/haproxy/templates/address.lst.j2` — the address list template.
[4] `roles/haproxy/defaults/main.yml` and `roles/haproxy/vars/main.yml` — defaults.
[5] `roles/haproxy/handlers/main.yml` — handlers.
[6] `roles/haproxy/files/` — rsyslog and logrotate configuration.
[7] `molecule/haproxy/` — the molecule scenario.
[8] `playbooks/proxy.yml` — the playbook that applies the role.
