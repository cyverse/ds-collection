---
type: Role
title: rabbitmq Role
description: The cyverse.ds.rabbitmq role, which installs pinned Erlang and RabbitMQ packages from Team RabbitMQ's apt repositories, enables the management plugin, and manages the broker admin user.
resource: /roles/rabbitmq/tasks/main.yml
tags: [role, rabbitmq, amqp, messaging]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.rabbitmq` installs and configures the RabbitMQ broker the Data
Store publishes events to. The role has no README. `playbooks/amqp.yml` applies
it with the `_amqp_admin_username`, `_amqp_admin_password`, and
`_amqp_broker_port` values; see [amqp.yml](/ansible-playbooks/amqp.md) and
[AMQP Broker](/components/amqp-broker.md).

## Task files

`tasks/main.yml` imports `install.yml` and then `configure.yml`.

**`install.yml`** is apt-only and hard-codes the `jammy` (Ubuntu 22.04)
repositories:

1. If `/etc/apt/sources.list.d/rabbitmq.list` exists but doesn't reference
   `com.rabbitmq.team.gpg`, removes that list and the old keyrings.
2. Installs `apt-transport-https`, `ca-certificates`, `curl`, and `gnupg`.
3. Fetches the Team RabbitMQ signing key into
   `/usr/share/keyrings/com.rabbitmq.team.gpg` if it's absent.
4. Writes the Erlang and RabbitMQ repositories from `deb1`/`deb2.rabbitmq.com`.
5. Installs Erlang packages at `1:25.1.2-1` and `rabbitmq-server` at
   `3.11.23-1`.
6. Pins those versions in `/etc/apt/preferences.d/erlang` and
   `/etc/apt/preferences.d/rabbitmq`.

**`configure.yml`**:

1. Templates `/etc/rabbitmq/rabbitmq.conf`, setting
   `listeners.tcp.1 = :::<broker port>` and `management.tcp.port`.
2. Enables and starts `rabbitmq-server`.
3. Enables the `rabbitmq_management` plugin.
4. Creates the admin user with full permissions on `/` and the `administrator`
   tag (`no_log`).
5. Deletes the `guest` user when the admin username isn't `guest`.

The config template and plugin tasks notify the `Restart RabbitMQ` handler.

## Variables

| Variable | Default |
| --- | --- |
| `rabbitmq_admin_username` | `guest` |
| `rabbitmq_admin_password` | `guest` |
| `rabbitmq_broker_port` | `5672` |
| `rabbitmq_mgmt_port` | `15672` |

Vhosts, exchanges, and queues are managed separately by the
[rabbitmq_vhost role](/ansible-roles/rabbitmq-vhost.md).

## Molecule scenario

`molecule/rabbitmq` converges the role on an Ubuntu 22.04 container with admin
user `admin` and management port 2000. `verify.yml` checks that:

- `rabbitmq.conf` renders the expected listener and management port;
- the prerequisite packages, apt preferences, repository list, and keyring
  exist;
- the installed Erlang packages are older than `1:25.2` and RabbitMQ is older
  than `3.12`;
- the config file is owned by `rabbitmq`, and the service is running and
  enabled;
- only the management plugin is explicitly enabled;
- the admin user has the `administrator` tag, the management API accepts its
  password, and it has `.*` permissions on `/`.

See [Testing Roles with Molecule](/runbooks/testing-roles-with-molecule.md).

# Citations

[1] `roles/rabbitmq/tasks/` — `main.yml`, `install.yml`, and `configure.yml`.
[2] `roles/rabbitmq/templates/rabbitmq.conf.j2` — the broker configuration template.
[3] `roles/rabbitmq/defaults/main.yml` and `roles/rabbitmq/handlers/main.yml` — defaults and the restart handler.
[4] `molecule/rabbitmq/` — the molecule scenario.
[5] `playbooks/amqp.yml` — the playbook that applies the role.
