---
type: Playbook
title: amqp_exchange.yml
description: Creates the iRODS vhost, user permissions, and topic exchange on the RabbitMQ broker using the rabbitmq_vhost role.
resource: /playbooks/amqp_exchange.yml
tags: [amqp, rabbitmq, exchange, vhost]
timestamp: 2026-09-17T00:00:00Z
---

`amqp_exchange.yml` prepares the broker for the messages iRODS publishes. See
[AMQP Broker](/components/amqp-broker.md).

## Hosts

One play on the `amqp` group with `become: true`, `run_once: true`, and
`gather_facts: false`. The whole play is tagged `no_testing`, so the testing
harness skips it.

## What it does

It applies the [rabbitmq_vhost](/ansible-roles/rabbitmq-vhost.md) role with:

- vhost `amqp_irods_vhost` (default `/`), managed through the management port
  `amqp_management_port` (default `15672`) as `amqp_admin_username` /
  `amqp_admin_password` (default `guest` / `guest`);
- user `amqp_irods_username` (defaults to `amqp_admin_username`) with `.*`
  configure, read, and write permissions;
- a `topic` exchange named `amqp_irods_exchange` (default `irods`).

## Testing

There is no `playbooks/tests/amqp_exchange.yml`, and the play is tagged
`no_testing`.

# Citations

[1] `playbooks/amqp_exchange.yml` — the playbook.
[2] `playbooks/group_vars/all/amqp.yml` — AMQP variable defaults.
[3] `roles/rabbitmq_vhost/README.md` — the role it applies.
