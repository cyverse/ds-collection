---
type: Playbook
title: proxy_block.yml
description: Drains and disables the SFTP, WebDAV, and iRODS backend servers in HAProxy, cutting off client access to the Data Store.
resource: /playbooks/proxy_block.yml
tags: [proxy, haproxy, maintenance]
timestamp: 2026-09-17T00:00:00Z
---

`proxy_block.yml` "terminates all client connections to HAProxy and blocks new
connections" (per `playbooks/README.md`). It reverses with
[proxy_unblock.yml](/ansible-playbooks/proxy-unblock.md). See
[HAProxy Proxy](/components/haproxy-proxy.md).

One play on `proxy` with `become: true`, tagged `no_testing`. Using
`community.general.haproxy` with `state: disabled` and `drain: true`, it
disables, in order:

1. server `sftp` in backend `sftp`;
2. server `dav` in backend `webdavs`;
3. server `irods` in backend `irods_direct`.

Those backend and server names match the ones defined in the haproxy role's
`haproxy.cfg.j2` template.

There is no `playbooks/tests/proxy_block.yml`.

# Citations

[1] `playbooks/proxy_block.yml` — the playbook.
[2] `playbooks/README.md` — its description.
[3] `roles/haproxy/templates/haproxy.cfg.j2` — where the backends are defined.
