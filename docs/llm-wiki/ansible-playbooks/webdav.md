---
type: Playbook
title: webdav.yml
description: Deploys the WebDAV service — Apache with davrods, a Varnish cache in front, purgeman for cache invalidation, static landing pages, and TLS — on the webdav hosts.
resource: /playbooks/webdav.yml
tags: [webdav, apache, davrods, varnish, purgeman, tls]
timestamp: 2026-09-17T00:00:00Z
---

`webdav.yml` builds the Data Store's WebDAV service. See
[WebDAV](/components/webdav.md) for the component.

## Hosts

One play on `webdav` with `become: true`. The package tasks use `yum`,
`rpm_key`, and `yum versionlock`, so the play targets RPM-based hosts.

## Pre-tasks

1. Sets `notifications_enabled` (tagged `no_testing`). All handlers require it,
   and the restart handlers also require `webdav_restart_allowed`.
2. Installs `policycoreutils-python` if SELinux is enabled.
3. Writes the TLS chain, certificate, and key from `webdav_tls_chain`,
   `webdav_tls_cert`, and `webdav_tls_key` to their `*_file` paths when the
   contents are non-empty, creating parent directories.
4. Installs `yum-plugin-versionlock`, the iRODS signing key and yum repository,
   and forces the GPG key import.
5. If the `mod_ssl-rm_ssl_conf` package isn't installed, runs
   `playbooks/tasks/webdav/install_rm_sslconf_rpm.yml`. That builds an empty
   RPM on the control node with `rpmbuild`, whose triggers delete
   `/etc/httpd/conf.d/ssl.conf` whenever `mod_ssl` is installed or updated,
   and installs it on the host.
6. Installs `mod_proxy_html`, `mod_qos`, and `mod_ssl`, and copies the files in
   `files/webdav/etc/httpd/conf.modules.d/`.
7. Removes yum version locks on `irods-*` packages other than
   `irods-runtime-4.3.0`, installs davrods `4.3.0_1.5.0` from its GitHub
   release, and locks `irods-runtime`. A comment explains the `command` module
   is used because `community.general.yum_versionlock` won't lock packages that
   aren't installed.
8. Includes the [irods_cfg](/ansible-roles/irods-cfg.md) role's `client.yml`
   to write `/etc/httpd/irods/irods_environment.json` for user `anonymous`,
   host `webdav_irods_host`, zone `webdav_irods_zone`.
9. Renders davrods directory-listing heads (`home-head.html`,
   `projects-head.html`, `community-head.html`, `curated-head.html`) into
   `/etc/httpd/irods/` via `playbooks/tasks/webdav/mk_dir_head.yml`.
10. Installs templated landing pages for `/dav/` and `/dav-anon/` via
    `playbooks/tasks/webdav/install_html.yml`, plus `index.html`, `robots.txt`,
    and `errors/moved_project.html` under `/var/www/html`.
11. Upgrades Varnish: if a version older than 6.5.1 is installed it stops and
    removes it and deletes its service file, logs, and cache files. It then
    installs Varnish 6.5.1 from packagecloud on every host, sets `varnishd_t`
    permissive under SELinux, mounts a 4 GB tmpfs at `/var/lib/varnish`
    (tagged `no_testing`), creates `webdav_cache_dir` and `/var/log/varnish`,
    and renders `default.vcl` and `varnish.service`.
12. Sets `httpd_t` permissive under SELinux.

## Apache role

The play then applies the Galaxy role `geerlingguy.apache` (tagged
`no_testing`) with `templates/webdav/etc/httpd/conf.d/vhosts.conf.j2` as its
vhost template. It defines:

- an HTTP vhost that permanently redirects to `https://webdav_canonical_hostname/`;
- a vhost on `127.0.0.1` that serves davrods locations for
  `/dav/<zone>/commons/community_released`, `/dav/<zone>/commons/cyverse_curated`,
  `/dav/<zone>/home`, and `/dav/<zone>/projects`, maps `/dav-anon/…` onto
  `/dav/…` with anonymous Basic auth, strips `ticket=` query parameters into
  `DAVRODS_TICKET`, answers `410 Gone` for projects listed in
  `webdav_moved_projects`, and exposes `/server-status` and `/server-qos` to
  localhost;
- a TLS vhost that sends `GET`, `HEAD`, and `PURGE` requests to Varnish on
  `webdav_varnish_service_port` and everything else to Apache on port 80.

Worker limits come from `webdav_server_limit`, `webdav_threads_per_child`, and
`webdav_max_request_workers`; optional `mod_qos` request limits come from
`webdav_access_limit` and `webdav_irods_access_limit`.

## Post-tasks

1. Installs `files/webdav/etc/logrotate.d/httpd`.
2. Adds systemd `requires` links so httpd pulls in Varnish, and Varnish pulls
   in `varnishncsa` and purgeman.
3. Installs purgeman `v0.3.0` from GitHub (via `make install_centos`) if it's
   missing, a different version, or lacks its `purgeman` account, renders
   `/etc/purgeman/purgeman.conf`, and installs `purgeman.service`.

## Variables

Defaults are in `playbooks/group_vars/all/webdav.yml`. Notable ones:

| Variable | Default |
| --- | --- |
| `webdav_canonical_hostname` | `localhost` |
| `webdav_irods_host` / `webdav_irods_port` / `webdav_irods_zone` | `localhost` / `1247` / `tempZone` |
| `webdav_irods_username` / `webdav_irods_password` | `rods` / required |
| `webdav_amqp_host` / `_port` / `_vhost` / `_exchange` | `localhost` / `5672` / `/` / `irods` |
| `webdav_amqp_username` / `webdav_amqp_password` | `guest` / `guest` |
| `webdav_cache_dir` | `/var/cache/varnish` |
| `webdav_cache_size` (MB) / `webdav_cache_max_file_size` (MB) | `1000` / `10` |
| `webdav_cache_max_ttl` (s) / `webdav_cache_ttl_fraction` | `86400` / `0.1` |
| `webdav_varnish_service_port` | `6081` |
| `webdav_server_limit` / `webdav_threads_per_child` / `webdav_max_request_workers` | `48` / `4` / `192` |
| `webdav_access_limit` / `webdav_irods_access_limit` | none |
| `webdav_moved_projects` | `[]` |
| `webdav_restart_allowed` | `false` |
| `webdav_tls_cert_file` / `_key_file` / `_chain_file` | `/etc/ssl/certs/dummy.crt` / `dummy.key` / `dummy-chain.crt` |

`webdav_auth_name` is consumed by the davrods template, and the `webdav_amqp_*`
and `webdav_irods_username`/`_password` variables by the purgeman template.
`webdav_allowed_src` (default `['0.0.0.0/0']`) is defined but not referenced by
the playbook, its task files, or its templates. The landing-page task
file uses `_irods_zone_name` for paths, while the rest of the playbook uses
`webdav_irods_zone`.

## Testing

`playbooks/tests/webdav.yml`:

- renders `head.html.j2`, `default.vcl.j2`, `purgeman.conf.j2`, and
  `varnish.service.j2` and checks the cache TTL and size rules, purgeman's AMQP
  and iRODS settings, and Varnish's listen port and cache file;
- renders the landing pages for both `dav` and `dav-anon` and checks their
  titles, links, and base URLs;
- on the `webdav` hosts, checks the TLS files' contents and permissions, the
  installed packages (`davrods`, `mod_proxy_html`, `mod_qos`, `mod_ssl`,
  `yum-plugin-versionlock`, `varnish`), the iRODS signing key and repo,
  that `ssl.conf` is gone, that `irods-runtime` is locked, the davrods head
  files and `irods_environment.json` contents, the Apache module files, the web
  pages, Varnish's directories and config, the log rotation config, the
  systemd dependency links, and the purgeman binary, config, and unit.

The Varnish package check passes `version: "6.5.1"`, but
`playbooks/tests/tasks/test_pkg_installed.yml` reads `ver`, so the installed
version isn't actually checked.

The testing inventory's `webdav` group vars set the cache directory to
`/cache_vol`, the zone to `testing`, the certificate and key paths under
`/tmp`, and the chain path to `/etc/httpd/testing.crt`.

# Citations

[1] `playbooks/webdav.yml` — the playbook.
[2] `playbooks/tasks/webdav/install_rm_sslconf_rpm.yml`, `mk_dir_head.yml`, `install_html.yml` — included task files.
[3] `playbooks/templates/webdav/` — vhost, davrods, Varnish, purgeman, and landing-page templates.
[4] `playbooks/files/webdav/` — Apache module config, log rotation, purgeman unit, static pages.
[5] `playbooks/group_vars/all/webdav.yml` — WebDAV variable defaults.
[6] `playbooks/tests/webdav.yml` — its test playbook.
[7] `testing/ansible-tester/inventory/group_vars/webdav.yml` — test values.
