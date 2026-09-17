---
type: Component
title: Data Store Overview
description: The Data Store's architecture as expressed by the collection's inventory groups, and which playbooks target each group.
tags: [architecture, inventory, overview, irods, dbms, amqp, proxy, sftp, webdav]
timestamp: 2026-09-17T00:00:00Z
---

The `cyverse.ds` collection deploys the CyVerse Data Store, an iRODS grid with
supporting services. The collection has no site-wide inventory of its own;
its architecture is expressed through the inventory group names the playbooks
target. The testing inventory
`testing/ansible-tester/inventory/hosts-all` shows the expected group layout.

## Inventory groups

| Group | Children | Component |
| --- | --- | --- |
| `amqp` | | [AMQP Broker](/components/amqp-broker.md) (RabbitMQ) |
| `dbms` | `dbms_primary`, `dbms_replicas` | [ICAT DBMS](/components/icat-dbms.md) (PostgreSQL) |
| `irods` | `irods_catalog`, `irods_resource` | iRODS servers |
| `irods_catalog` | | [iRODS Catalog Service Provider](/components/irods-catalog-provider.md) |
| `irods_resource` | `irods_resource_native`, `irods_resource_container` | [iRODS Resource Server](/components/irods-resource-server.md) |
| `proxy` | | [HAProxy Proxy](/components/haproxy-proxy.md) |
| `sftp` | | [SFTP](/components/sftp.md) (SFTPGo) |
| `webdav` | | [WebDAV](/components/webdav.md) (Apache, davrods, Varnish) |
| `unmanaged_systems` | | Hosts the collection must not reconfigure |

`irods_resource_native` hosts run iRODS installed from OS packages;
`irods_resource_container` hosts run it in Docker. The `proxy` group isn't in
the testing inventory, so the proxy playbooks aren't exercised by the harness.
`hosts-all` also defines a `cbuoy` group that no playbook targets.

`unmanaged_systems` is excluded from most host-level playbooks with patterns
such as `all:!unmanaged_systems:!localhost`. In `hosts-all` it holds
`localhost`, the AMQP host, and the containerized resource servers.
`infra_network.yml` also builds a dynamic `physical` group from hosts whose
`ansible_virtualization_type` is `NA` or `kvm`.

## Playbooks by group

| Target | Playbooks |
| --- | --- |
| All managed hosts | `infra_ansible_support.yml`, `infra_connectivity.yml`, `infra_fail2ban.yml`, `infra_mail.yml`, `infra_network.yml`, `infra_ping.yml`, `infra_reboot.yml`, `infra_rng_tools.yml`, `infra_selinux.yml`, `infra_system_packages.yml`, `infra_timezone.yml` |
| `amqp` | `amqp.yml`, `amqp_exchange.yml` |
| `dbms` / `dbms_primary` / `dbms_replicas` | `dbms.yml`, `dbms_icat.yml` |
| `irods` | `irods_provision.yml`, `irods_hosts.yml`, `irods_cfg.yml`, `irods_log.yml`, `irods_s3_cred.yml`, `irods_restart_all.yml`, `irods_stop_all.yml`, `irods_check_routes.yml` |
| `irods_catalog` | `irods_catalog_provider.yml`, `irods_runtime_init.yml`, `irods_resource_hierarchies.yml`, `irods_specific_queries.yml`, `avra_usage.yml`, `esiil_usage.yml`, `ncems_usage.yml`, `pire_usage.yml` |
| `irods_resource` | `irods_resource_server.yml` (native), `irods_resource_container.yml`, `irods_storage_resources.yml` (native), `irods_free_space.yml`, `irods_restart_rs.yml` |
| `proxy` | `proxy.yml`, `proxy_start.yml`, `proxy_stop.yml`, `proxy_block.yml`, `proxy_unblock.yml` |
| `sftp` | `sftp.yml`, `sftp_start.yml`, `sftp_stop.yml` |
| `webdav` | `webdav.yml`, `webdav_start.yml`, `webdav_stop.yml` |

Each playbook has its own page under
[ansible-playbooks/](/ansible-playbooks/index.md).

## How the pieces connect

- The catalog provider stores the ICAT catalog in the `ICAT` database on the
  primary DBMS and publishes change events to an exchange on the AMQP broker.
- Resource servers are catalog service consumers that hold the storage vaults.
- HAProxy fronts iRODS (port 1247 and the reconnection port range), SFTP, and
  WebDAV for clients.
- SFTPGo and WebDAV connect to iRODS as clients. WebDAV's `purgeman` service
  consumes AMQP events to purge its Varnish cache.

Role and configuration-file detail lives on the component pages and in
[iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md).

# Citations

[1] `testing/ansible-tester/inventory/hosts-all` — the full group layout used by the testing harness.
[2] `playbooks/*.yml` — the `hosts:` patterns of each play.
[3] `playbooks/infra_network.yml` — dynamic `physical` group.
[4] `roles/haproxy/templates/haproxy.cfg.j2` — the proxied services.
[5] `playbooks/templates/webdav/etc/purgeman/purgeman.conf.j2` — purgeman's AMQP and Varnish settings.
