---
type: Playbook
title: proxy_start.yml
description: Starts the haproxy service on the proxy hosts and enables it at boot.
resource: /playbooks/proxy_start.yml
tags: [proxy, haproxy, service]
timestamp: 2026-09-17T00:00:00Z
---

`proxy_start.yml` "starts HAProxy" (per `playbooks/README.md`). It has one play
on `proxy` with `become: true`, tagged `no_testing`, that sets the `haproxy`
service to `started` and `enabled`. The counterpart is
[proxy_stop.yml](/ansible-playbooks/proxy-stop.md). See
[HAProxy Proxy](/components/haproxy-proxy.md).

There is no `playbooks/tests/proxy_start.yml`.

# Citations

[1] `playbooks/proxy_start.yml` — the playbook.
[2] `playbooks/README.md` — its description.
