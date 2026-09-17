---
type: Playbook
title: amqp.yml
description: Installs and configures the RabbitMQ broker on the amqp hosts using the rabbitmq role.
resource: /playbooks/amqp.yml
tags: [amqp, rabbitmq, broker]
timestamp: 2026-09-17T00:00:00Z
---

`amqp.yml` sets up the RabbitMQ broker that the Data Store publishes events to.
See [AMQP Broker](/components/amqp-broker.md) for how the broker fits into the
Data Store.

## Hosts

A single play targets the `amqp` inventory group with `become: true`.

## What it does

It applies the [rabbitmq](/ansible-roles/rabbitmq.md) role, mapping collection
variables onto the role's variables:

| Role variable | Collection variable | Default |
| --- | --- | --- |
| `rabbitmq_admin_username` | `amqp_admin_username` | `guest` |
| `rabbitmq_admin_password` | `amqp_admin_password` | `guest` |
| `rabbitmq_broker_port` | `amqp_broker_port` | `5672` |
| `rabbitmq_mgmt_port` | `amqp_management_port` | `15672` |

A [firewalld](/ansible-roles/firewalld.md) role invocation is present but
commented out, with the note "This is disabled until DS-821 is started". It
would have admitted `admin_hosts`, the `irods_catalog` and `webdav` groups, and
`amqp_external_clients` to the broker port.

The vhost, users, and exchange are created separately by
[amqp_exchange.yml](/ansible-playbooks/amqp-exchange.md).

## Testing

There is no `playbooks/tests/amqp.yml`. In the testing environment the `amqp`
host is also listed in `unmanaged_systems`.

# Citations

[1] `playbooks/amqp.yml` — the playbook.
[2] `playbooks/group_vars/all/amqp.yml` — AMQP variable defaults.
[3] `roles/rabbitmq/` — the role it applies.
