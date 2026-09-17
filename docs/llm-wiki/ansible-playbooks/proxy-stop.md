---
type: Playbook
title: proxy_stop.yml
description: Stops the haproxy service on the proxy hosts and disables it at boot.
resource: /playbooks/proxy_stop.yml
tags: [proxy, haproxy, service]
timestamp: 2026-09-17T00:00:00Z
---

`proxy_stop.yml` "stops HAProxy" (per `playbooks/README.md`). It has one play
on `proxy` with `become: true`, tagged `no_testing`, that sets the `haproxy`
service to `stopped` and not `enabled`, so it won't start at boot. The
counterpart is [proxy_start.yml](/ansible-playbooks/proxy-start.md). See
[HAProxy Proxy](/components/haproxy-proxy.md).

There is no `playbooks/tests/proxy_stop.yml`.

# Citations

[1] `playbooks/proxy_stop.yml` — the playbook.
[2] `playbooks/README.md` — its description.
