---
type: Plugin
title: port_check_receiver Module
description: The cyverse.ds.port_check_receiver module, which listens on a set of TCP and UDP ports, answers every message with pong, and exits on a stop message, for verifying network routes with port_check_sender.
resource: /plugins/modules/port_check_receiver.py
tags: [plugin, module, network, firewall, connectivity]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.port_check_receiver` works with
[port_check_sender](/ansible-plugins/port-check-sender.md) to check whether TCP
and UDP ports on the receiver's host can be reached from the sender's host. It
uses only the Python standard library, and its documentation lives in a comment
header rather than a `DOCUMENTATION` block.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `tcp_ports` | no | `[]` | TCP ports to listen on |
| `udp_ports` | no | `[]` | UDP ports to listen on |
| `stop_command` | no | `finished` | Message that tells the receiver to stop |
| `timeout` | no | `300` | Seconds to wait for activity before giving up |

## Behavior

The module binds each port on `0.0.0.0` and runs a `select` loop.

- It answers any message with `pong`, reading at most 128 bytes.
- TCP connections are accepted without blocking and dropped after the reply.
- When it receives `stop_command`, it stops listening and exits successfully.
- It fails if any port can't be bound ("port N/tcp already in use"), if no
  activity happens within `timeout` seconds ("receiver: timed out"), or on an
  unexpected exception, reported with its traceback.

Because it blocks until stopped, callers run it asynchronously.

## Usage

Used by [irods_check_routes.yml](/ansible-playbooks/irods-check-routes.md),
together with `port_check_sender`.

## Tests

`plugins/modules/tests/port_check_receiver.yml` starts the receiver on TCP port
1100 with `async`, sends `finished` through `/dev/tcp`, waits for the job to
finish, and fails if the job reported an error. The play is tagged
`non_idempotent`. See
[Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).

## Notes

When a UDP port can't be bound, the failure message still says `/tcp`.

# Citations

[1] `plugins/modules/port_check_receiver.py` — module source and header documentation.
[2] `plugins/modules/tests/port_check_receiver.yml` — module test playbook.
