---
type: Plugin
title: port_check_sender Module
description: The cyverse.ds.port_check_sender module, which sends a message to each listed TCP and UDP port on a destination host and fails listing every port that didn't reply.
resource: /plugins/modules/port_check_sender.py
tags: [plugin, module, network, firewall, connectivity]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.port_check_sender` works with
[port_check_receiver](/ansible-plugins/port-check-receiver.md) to check whether
TCP and UDP ports on a destination host running the receiver can be reached. It
uses only the Python standard library, and its documentation lives in a comment
header rather than a `DOCUMENTATION` block.

## Options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `destination` | no | `localhost` | Host to send the message to |
| `tcp_ports` | no | `[]` | TCP ports to check |
| `udp_ports` | no | `[]` | UDP ports to check |
| `timeout` | no | `4` | Seconds to wait for a response |
| `msg` | no | `ping` | Message to send |

## Behavior

For each TCP port, the module connects, sends `msg`, and waits to receive a
reply. For each UDP port, it sends a datagram and waits for a reply. Any
exception, including a timeout, marks the port as blocked, recorded as
`port/protocol (error)`. If any port is blocked, the module fails with
"blocked ports [...]"; otherwise it exits successfully without reporting a
change.

## Usage

Used by [irods_check_routes.yml](/ansible-playbooks/irods-check-routes.md),
together with `port_check_receiver`.

## Tests

There is no `plugins/modules/tests/port_check_sender.yml`.

# Citations

[1] `plugins/modules/port_check_sender.py` — module source and header documentation.
