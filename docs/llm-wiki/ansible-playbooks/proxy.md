---
type: Playbook
title: proxy.yml
description: Deploys HAProxy on the proxy hosts, fronting iRODS, SFTP, and WebDAV, using the haproxy role.
resource: /playbooks/proxy.yml
tags: [proxy, haproxy, irods, sftp, webdav]
timestamp: 2026-09-17T00:00:00Z
---

`proxy.yml` "completely deploys the proxies" (per `playbooks/README.md`). See
[HAProxy Proxy](/components/haproxy-proxy.md) for the component and
[Limiting Concurrency](/runbooks/limiting-concurrency.md) for how per-client
connection limits work.

## Hosts

One play on the `proxy` inventory group with `become: true`.

## What it does

It applies the [haproxy](/ansible-roles/haproxy.md) role. Backends come from
the inventory: iRODS is the first `irods_catalog` host, and the SFTP and WebDAV
backends are the `sftp` and `webdav` groups. Fixed values set by the playbook:

- `haproxy_num_threads` is the host's vCPU count minus two (reserving two CPUs
  for the OS), with a minimum of one;
- `haproxy_queue_timeout` is `10m`;
- `haproxy_irods_throttled_max_conn` is `100`;
- SFTP and WebDAV health-check periods are `6s`.

## Variables

Defaults from `playbooks/group_vars/all/proxy.yml`; descriptions are from
`playbooks/README.md`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `proxy_allow_client_hosts` | `[]` | Clients allowed limited concurrent iRODS connections |
| `proxy_block_client_hosts` | `[]` | Clients not allowed to use the Data Store |
| `proxy_vip_client_hosts` | `[]` | Clients allowed unlimited concurrent iRODS connections |
| `proxy_irods_direct_max_conn` | `200` | Maximum number of connections to iRODS |
| `proxy_irods_reconn_ports` | `20000-20399` | Ports forwarded to iRODS for reconnections |
| `proxy_sftp_port` | `22` | Port HAProxy serves SFTP on |
| `proxy_sftp_backend_port` | `2022` | Port SFTPGo listens on |
| `proxy_restart_allowed` | `false` | Whether HAProxy may be restarted |
| `proxy_rsyslog_conf` | `/etc/rsyslog.d/haproxy.conf` | rsyslog config path for HAProxy |
| `proxy_stats_auth` | none | Credentials for the stats web interface |
| `proxy_tls_crt` / `proxy_tls_crt_content` | none | TLS certificate chain path / contents |

## Related playbooks

[proxy_start.yml](/ansible-playbooks/proxy-start.md),
[proxy_stop.yml](/ansible-playbooks/proxy-stop.md),
[proxy_block.yml](/ansible-playbooks/proxy-block.md), and
[proxy_unblock.yml](/ansible-playbooks/proxy-unblock.md) operate the deployed
proxy.

## Testing

There is no `playbooks/tests/proxy.yml`, and none of the testing inventories
under `testing/ansible-tester/inventory/` define a `proxy` group. The haproxy
role has its own molecule scenario in `molecule/haproxy/`.

# Citations

[1] `playbooks/proxy.yml` — the playbook.
[2] `playbooks/group_vars/all/proxy.yml` — proxy variable defaults.
[3] `playbooks/README.md` — playbook and variable descriptions.
[4] `roles/haproxy/` — the role it applies.
