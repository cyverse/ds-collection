---
type: Role
title: rabbitmq_vhost Role
description: The cyverse.ds.rabbitmq_vhost role, which creates or removes a RabbitMQ vhost and manages its parameters, policies, user permissions, exchanges, queues, and bindings.
resource: /roles/rabbitmq_vhost/README.md
tags: [role, rabbitmq, amqp, vhost, messaging]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.rabbitmq_vhost` configures a vhost on a RabbitMQ broker. The broker
must already have RabbitMQ server (at least 3.2) with the management plugin
installed. `playbooks/amqp_exchange.yml` applies it once, passing the
`_amqp_management_port`, `_amqp_admin_username`, and `_amqp_admin_password`
values; see [amqp_exchange.yml](/ansible-playbooks/amqp-exchange.md) and
[AMQP Broker](/components/amqp-broker.md).

## Task flow

`tasks/main.yml` ensures the vhost exists or is absent with
`community.rabbitmq.rabbitmq_vhost`. When `rabbitmq_vhost_state` is `present`,
it then:

1. sets each entry of `rabbitmq_vhost_parameters`;
2. sets each entry of `rabbitmq_vhost_policies` (default pattern `^$`, tags
   `{}`);
3. runs `permission.yml` for each user in `rabbitmq_vhost_users`. This reads
   the user's existing tags with `rabbitmqctl list_users` and passes them back
   unchanged while setting the configure, read, and write permissions;
4. runs `exchange.yml` for each exchange, which configures it through the
   management API and, if it's present, calls `bind.yml` for its bindings;
5. runs `queue.yml` for each queue, which configures it through the management
   API and, if it's present, calls `bind.yml` for its bindings.

Exchange, queue, and binding tasks authenticate to the management API with
`rabbitmq_vhost_admin_username`, `rabbitmq_vhost_admin_password`, and
`rabbitmq_vhost_mgmt_port`. The vhost, parameter, policy, and permission tasks
use `rabbitmq_vhost_node` instead. The handlers file is empty.

## Variables

| Variable | Required | Default | Comment |
| --- | --- | --- | --- |
| `rabbitmq_vhost_admin_password` | yes | | Password for the admin user |
| `rabbitmq_vhost_admin_username` | no | `guest` | User able to administer the vhost |
| `rabbitmq_vhost_mgmt_port` | no | `15672` | Management plugin port (README: untested) |
| `rabbitmq_vhost_name` | yes | | The vhost to manage |
| `rabbitmq_vhost_node` | no | `rabbit` | Erlang node of the RabbitMQ server |
| `rabbitmq_vhost_state` | no | `present` | `absent` or `present` |
| `rabbitmq_vhost_tracing` | no | `false` | Enable tracing (README: untested) |
| `rabbitmq_vhost_exchanges` | no | `[]` | Exchanges to add, modify, or remove |
| `rabbitmq_vhost_parameters` | no | `[]` | Parameters (README: untested) |
| `rabbitmq_vhost_policies` | no | `[]` | Policies (README: untested) |
| `rabbitmq_vhost_queues` | no | `[]` | Queues (README: untested) |
| `rabbitmq_vhost_users` | no | `[]` | Per-user permissions on the vhost |

The README documents the fields of each item type: parameters (`component`,
`name`, `state`, `value`); policies (`apply_to`, `name`, `pattern`,
`priority`, `state`, `tags`); users (`name`, `configure_priv`, `read_priv`,
`write_priv`); exchanges (`name`, `type`, `durable`, `auto_delete`,
`internal`, `arguments`, `bindings`, `state`); queues (`name`, `durable`,
`auto_delete`, `auto_expires`, `dead_letter_exchange`,
`dead_letter_routing_key`, `max_length`, `message_ttl`, `arguments`,
`bindings`, `state`); and bindings (`source`, `routing_key`, `arguments`,
`state`). The role's `meta/main.yml` declares the `community.rabbitmq`
collection, and the README lists `requests >= 1.0.0` as a dependency.

## Molecule scenario

`molecule/rabbitmq_vhost` runs against the `rabbitmq:management` image.
`prepare.yml` creates `admin` (tags `administrator,monitoring`) and `user`.
`converge.yml` creates `/vhost1` with a minimal entry for `user`, and `/vhost2`
with full permissions for `admin` and a `topic-exchange` exchange of type
`topic`. `verify.yml` checks that:

- `user` has `^$` permissions on `/vhost1`;
- `/vhost2` exists and `admin` has `.*` permissions on it;
- `admin`'s tags are unchanged;
- `topic-exchange` exists with type `topic`.

See [Testing Roles with Molecule](/runbooks/testing-roles-with-molecule.md).

## Notes

The README's item tables are headed with `irods_vhost_parameters`,
`irods_vhost_policies`, `irods_vhost_users`, `irods_vhost_exchanges`, and
`irods_vhost_queues`, which don't match the role's variable names. The README
also gives exchange defaults of `durable: true` and `type: direct`, and user
permission defaults of `^$`. The task files don't set those defaults
themselves; they omit unset fields, so the `community.rabbitmq` module defaults
apply. The molecule scenario confirms that a user given no privileges ends up
with `^$`.

# Citations

[1] `roles/rabbitmq_vhost/README.md` — role description, variable tables, and example playbook.
[2] `roles/rabbitmq_vhost/tasks/` — `main.yml`, `permission.yml`, `exchange.yml`, `queue.yml`, and `bind.yml`.
[3] `roles/rabbitmq_vhost/defaults/main.yml` and `roles/rabbitmq_vhost/vars/main.yml` — defaults.
[4] `roles/rabbitmq_vhost/meta/main.yml` — role metadata and collection dependency.
[5] `molecule/rabbitmq_vhost/` — the molecule scenario.
[6] `playbooks/amqp_exchange.yml` — the playbook that applies the role.
