---
type: Playbook
title: webdav_start.yml
description: Starts and enables varnish, varnishncsa, httpd, and purgeman on the WebDAV hosts.
resource: /playbooks/webdav_start.yml
tags: [webdav, apache, varnish, purgeman, service]
timestamp: 2026-09-17T00:00:00Z
---

`webdav_start.yml` has one play on `webdav` with `become: true`, tagged
`no_testing`. It sets each service to `started` and `enabled`, in this order:
`varnish`, `varnishncsa`, `httpd`, `purgeman`. The counterpart is
[webdav_stop.yml](/ansible-playbooks/webdav-stop.md). See
[WebDAV](/components/webdav.md).

There is no `playbooks/tests/webdav_start.yml`.

# Citations

[1] `playbooks/webdav_start.yml` — the playbook.
