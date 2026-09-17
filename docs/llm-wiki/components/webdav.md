---
type: Component
title: WebDAV
description: The webdav group's Apache httpd with davrods, fronted by a Varnish cache that purgeman invalidates from iRODS AMQP events.
resource: /playbooks/webdav.yml
tags: [webdav, apache, davrods, varnish, purgeman, cache]
timestamp: 2026-09-17T00:00:00Z
---

WebDAV access runs on the hosts in the `webdav` inventory group. The stack is
Apache httpd with the davrods module for iRODS access, Varnish for caching
reads, and purgeman for cache invalidation. The playbook uses `yum` and an
EL7 Varnish RPM, so it targets CentOS 7 hosts.

## Services

| Service | Role |
| --- | --- |
| `httpd` | TLS termination, request routing, and davrods |
| `varnish` / `varnishncsa` | Cache for `GET`/`HEAD` requests, and its access log |
| `purgeman` | Consumes iRODS events from AMQP and purges changed paths from Varnish |

`webdav_start.yml` starts varnish, varnishncsa, httpd, then purgeman;
`webdav_stop.yml` stops them in reverse order. Both are tagged `no_testing`.
Symlinks in systemd `.requires` directories make Varnish run with Apache,
and varnishncsa and purgeman run with Varnish.

## Deployment

`webdav.yml` installs `mod_proxy_html`, `mod_qos`, and `mod_ssl`, removes the
stock `ssl.conf` by building and installing a small RPM, installs davrods
`4.3.0_1.5.0` and locks `irods-runtime`, and writes the davrods client
environment to `etc/httpd/irods/irods_environment.json` with the `irods_cfg`
role's `client.yml` as the `anonymous` user. It installs static HTML
directory headers and pages, Varnish `6.5.1` with its VCL and a shared-memory
mount, purgeman `v0.3.0` from `github.com/cyverse/purgeman`, and log rotation.
Apache itself is configured by the `geerlingguy.apache` role (tagged
`no_testing`).

## Request flow

- Port 80 permanently redirects to HTTPS on `webdav_canonical_hostname`.
- The 443 virtual host terminates TLS and proxies `GET`, `HEAD`, and `PURGE`
  to Varnish on `webdav_varnish_service_port`; other methods go to Apache on
  `127.0.0.1:80`.
- The `127.0.0.1` virtual host serves davrods locations under
  `/dav/<zone>/`: anonymous read-only `commons/community_released` and
  `commons/cyverse_curated`, and authenticated `home` and `projects`.
  `/dav-anon/<zone>/...` is proxied to `/dav/` with an `anonymous`
  Authorization header. `ticket=` query parameters are passed to davrods,
  and projects listed in `webdav_moved_projects` return `410 Gone`.
- `mod_qos` returns 429 when `webdav_access_limit` or
  `webdav_irods_access_limit` is exceeded.

The VCL computes an object's TTL as `webdav_cache_ttl_fraction` of the time
since its `Last-Modified`, capped at `webdav_cache_max_ttl`. purgeman is
configured to purge `/dav` and `/dav-anon` on Varnish.

## Key variables

Defaults come from `playbooks/group_vars/all/webdav.yml`; the full table is
in `playbooks/README.md`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `webdav_canonical_hostname` | `localhost` | Public host name |
| `webdav_irods_host` / `_port` / `_zone` | `localhost` / `1247` / `tempZone` | iRODS connection |
| `webdav_irods_username` / `webdav_irods_password` | `rods` / required | purgeman's iRODS account |
| `webdav_amqp_host`, `_port`, `_vhost`, `_exchange` | `localhost`, `5672`, `/`, `irods` | purgeman's AMQP source |
| `webdav_cache_max_ttl` / `webdav_cache_ttl_fraction` | `86400` / `0.1` | Cache TTL policy |
| `webdav_cache_size` / `webdav_cache_dir` | `1000` / `/var/cache/varnish` | Cache storage |
| `webdav_varnish_service_port` | `6081` | Varnish port |
| `webdav_server_limit`, `webdav_threads_per_child`, `webdav_max_request_workers` | `48`, `4`, `192` | Apache worker MPM limits |
| `webdav_access_limit` / `webdav_irods_access_limit` | none / none | `mod_qos` request limits |
| `webdav_moved_projects` | `[]` | Projects answered with 410 |
| `webdav_tls_cert_file`, `_key_file`, `_chain_file` | `/etc/ssl/certs/dummy.*` | TLS file paths |
| `webdav_restart_allowed` | `false` | Whether handlers may restart services |

# Citations

[1] `playbooks/webdav.yml` — installation and Apache virtual hosts.
[2] `playbooks/webdav_start.yml`, `playbooks/webdav_stop.yml` — service control.
[3] `playbooks/tasks/webdav/` — static page and RPM tasks.
[4] `playbooks/templates/webdav/etc/varnish/default.vcl.j2` — Varnish cache policy.
[5] `playbooks/templates/webdav/etc/purgeman/purgeman.conf.j2`, `playbooks/files/webdav/usr/lib/systemd/system/purgeman.service` — purgeman settings and unit ("an iRODS web-cache invalidator").
[6] `playbooks/templates/webdav/etc/httpd/conf.d/` — davrods and vhost templates.
[7] `playbooks/group_vars/all/webdav.yml` — variable defaults.
[8] `playbooks/README.md` — variable documentation.
