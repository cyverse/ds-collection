---
type: Playbook
title: webdav_stop.yml
description: Stops and disables purgeman, httpd, varnishncsa, and varnish on the WebDAV hosts.
resource: /playbooks/webdav_stop.yml
tags: [webdav, apache, varnish, purgeman, service]
timestamp: 2026-09-17T00:00:00Z
---

`webdav_stop.yml` has one play on `webdav` with `become: true`, tagged
`no_testing`. It sets each service to `stopped` and not `enabled`, in the
reverse of the start order: `purgeman`, `httpd`, `varnishncsa`, `varnish`. The
counterpart is [webdav_start.yml](/ansible-playbooks/webdav-start.md). See
[WebDAV](/components/webdav.md).

There is no `playbooks/tests/webdav_stop.yml`.

# Citations

[1] `playbooks/webdav_stop.yml` — the playbook.
