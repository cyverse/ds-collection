---
type: Playbook
title: proxy_unblock.yml
description: Re-enables the iRODS, WebDAV, and SFTP backend servers in HAProxy, restoring client access after proxy_block.yml.
resource: /playbooks/proxy_unblock.yml
tags: [proxy, haproxy, maintenance]
timestamp: 2026-09-17T00:00:00Z
---

`proxy_unblock.yml` "allows client connections to be made" (per
`playbooks/README.md`), undoing [proxy_block.yml](/ansible-playbooks/proxy-block.md).
See [HAProxy Proxy](/components/haproxy-proxy.md).

One play on `proxy` with `become: true`, tagged `no_testing`. Using
`community.general.haproxy` with `state: enabled` and
`fail_on_not_found: true`, it enables, in order:

1. server `irods` in backend `irods_direct`;
2. server `dav` in backend `webdavs`;
3. server `sftp` in backend `sftp`.

There is no `playbooks/tests/proxy_unblock.yml`.

# Citations

[1] `playbooks/proxy_unblock.yml` — the playbook.
[2] `playbooks/README.md` — its description.
