---
type: Component
title: HAProxy Proxy
description: The HAProxy hosts in the proxy group that front iRODS, SFTP, and WebDAV, with per-client connection throttling and allow/block/VIP lists.
resource: /playbooks/proxy.yml
tags: [haproxy, proxy, load-balancer, throttling, irods, sftp, webdav]
timestamp: 2026-09-17T00:00:00Z
---

The proxy is HAProxy on the hosts in the `proxy` inventory group. It is the
client entry point for iRODS, SFTP, and WebDAV. The `proxy` group isn't in the
testing inventory, and the start, stop, block, and unblock playbooks are
tagged `no_testing`.

## Playbooks

- `proxy.yml` applies the `cyverse.ds.haproxy` role. It reserves two CPUs for
  the OS (`haproxy_num_threads` is vCPUs minus 2, minimum 1), sets a 10 minute
  queue timeout, forwards iRODS to the first `irods_catalog` host, SFTP to
  the first `sftp` host, and WebDAV to the first `webdav` host, and caps
  throttled iRODS connections at 100.
- `proxy_start.yml` / `proxy_stop.yml` start and enable, or stop and disable,
  the `haproxy` service.
- `proxy_block.yml` drains and disables the `sftp`, `webdavs`, and
  `irods_direct` backends to terminate client connections.
- `proxy_unblock.yml` re-enables those backends.

## Traffic handling

The role's `haproxy.cfg.j2` defines:

- **iRODS** (`irods_main` on port 1247): inspects the iRODS message header,
  accepts `HEARTBEAT` requests and `RODS_CONNECT` requests from VIP sources
  without tracking, rejects anything that isn't `RODS_CONNECT`, tracks
  concurrent connections per source IP, rejects sources with more than 10, and
  sends sources with more than 1 to a throttled backend that loops back
  through a Unix socket. Reconnection
  ports (`irods_reconn`) go straight to `irods_direct`. Health checks on the
  iRODS backend are commented out until iRODS servers are load balanced.
- **SFTP** (`listen sftp`): accepts VIP sources, rejects sources with more
  than 10 concurrent connections, and forwards to the SFTP backend port with
  PROXY protocol v2.
- **WebDAV** (`listen webdav` on 80, `listen webdavs` on 443 when a TLS
  certificate is set): applies the VIP, allow, and block lists and the same
  10-connection limit. With TLS configured, HTTP redirects to HTTPS, and
  blocked HTTPS clients are redirected (307) to
  `https://unblockme.cyverse.org/`.
- A `stats` listener on port 8404.

The source lists live in `/etc/haproxy/vip.lst`, `allow.lst`, and `block.lst`.
The role also configures rsyslog and logrotate for HAProxy, SELinux booleans,
and the `net.ipv4.ip_nonlocal_bind` and `net.ipv4.ip_forward` sysctls.

[Limiting Concurrency](/runbooks/limiting-concurrency.md) explains the
stick-table technique the configuration is built on.

## Key variables

Defaults come from `playbooks/group_vars/all/proxy.yml`; the full table is in
`playbooks/README.md`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `proxy_vip_client_hosts` | `[]` | Sources exempt from throttling |
| `proxy_allow_client_hosts` / `proxy_block_client_hosts` | `[]` / `[]` | WebDAV allow and block lists |
| `proxy_irods_direct_max_conn` | `200` | Max connections to the iRODS backend |
| `proxy_irods_reconn_ports` | `20000-20399` | iRODS reconnection port range |
| `proxy_sftp_port` / `proxy_sftp_backend_port` | `22` / `2022` | SFTP front and back ports |
| `proxy_tls_crt` / `proxy_tls_crt_content` | none | TLS certificate path and content |
| `proxy_stats_auth` | none | Stats page credentials |
| `proxy_restart_allowed` | `false` | Whether handlers may restart HAProxy |

# Citations

[1] `playbooks/proxy.yml` — role invocation and settings.
[2] `playbooks/proxy_start.yml`, `playbooks/proxy_stop.yml`, `playbooks/proxy_block.yml`, `playbooks/proxy_unblock.yml` — operational playbooks.
[3] `roles/haproxy/templates/haproxy.cfg.j2` — frontends, backends, and ACLs.
[4] `roles/haproxy/defaults/main.yml` — role defaults.
[5] `playbooks/group_vars/all/proxy.yml` — variable defaults.
[6] `playbooks/README.md` — variable documentation.
