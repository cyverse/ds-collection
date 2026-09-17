---
type: Component
title: AMQP Broker
description: The RabbitMQ broker in the amqp group that hosts the topic exchange iRODS publishes Data Store events to.
resource: /playbooks/amqp.yml
tags: [amqp, rabbitmq, events, exchange]
timestamp: 2026-09-17T00:00:00Z
---

The AMQP broker is RabbitMQ on the hosts in the `amqp` inventory group. The
catalog service provider publishes iRODS change events to an exchange on it
(via `IRODS_AMQP_URI`), and the WebDAV hosts' `purgeman` service consumes
those events.

## Deployment

`amqp.yml` applies the `cyverse.ds.rabbitmq` role, which on Ubuntu 22.04
(jammy) installs Erlang `1:25.1.2-1` and `rabbitmq-server` `3.11.23-1` from
Team RabbitMQ's apt repositories and pins both versions. It enables the
management plugin, creates the admin user, and removes the `guest` user when
the admin user isn't `guest`. A `firewalld` role invocation is present but
commented out, noting it is disabled until DS-821 is started.

`amqp_exchange.yml` runs once, tagged `no_testing`, and applies the
`cyverse.ds.rabbitmq_vhost` role through the management API. It ensures the
vhost `amqp_irods_vhost`, grants `amqp_irods_username` full configure, read,
and write permissions on it, and creates the topic exchange
`amqp_irods_exchange`.

In the testing inventory the `amqp` host is also in `unmanaged_systems`.

## Key variables

Defaults come from `playbooks/group_vars/all/amqp.yml`; the full table is in
`playbooks/README.md`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `amqp_admin_username` / `amqp_admin_password` | `guest` / `guest` | Broker admin |
| `amqp_broker_port` | `5672` | AMQP port |
| `amqp_management_port` | `15672` | Management API port |
| `amqp_irods_vhost` | `/` | Vhost for iRODS events |
| `amqp_irods_exchange` | `irods` | Topic exchange for iRODS events |
| `amqp_irods_username` / `amqp_irods_password` | the admin credentials | iRODS publisher account |
| `amqp_external_clients` | `[]` | External client hosts (used only by the disabled firewall role) |

The iRODS side is configured separately by `irods_amqp_host`,
`irods_amqp_port`, `irods_amqp_vhost`, `irods_amqp_exchange`,
`irods_amqp_username`, and `irods_amqp_password`; see
[iRODS Catalog Service Provider](/components/irods-catalog-provider.md). The
WebDAV side uses the `webdav_amqp_*` variables; see
[WebDAV](/components/webdav.md).

# Citations

[1] `playbooks/amqp.yml` — broker deployment.
[2] `playbooks/amqp_exchange.yml` — vhost, user permissions, and exchange.
[3] `playbooks/group_vars/all/amqp.yml` — variable defaults.
[4] `roles/rabbitmq/` — installation and version pins.
[5] `roles/rabbitmq_vhost/README.md` — vhost management role.
[6] `playbooks/README.md` — variable documentation.
