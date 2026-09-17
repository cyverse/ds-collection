---
type: Role
title: firewalld Role
description: The cyverse.ds.firewalld role, which installs firewalld in place of ufw and manages a per-service maintenance, testing, or operation firewall configuration.
resource: /roles/firewalld/README.md
tags: [role, firewall, firewalld, security]
timestamp: 2026-09-17T00:00:00Z
---

`cyverse.ds.firewalld` configures firewalld in an opinionated way for a single
service. No playbook currently applies it: the only reference is a commented-out
block in `playbooks/amqp.yml`, marked as disabled until DS-821 is started.

## Configurations

The README describes three configurations, each extending the previous one.

1. **maintenance** — only the admin hosts may connect, and they may connect on
   every TCP and UDP port.
2. **testing** — adds access to the hosted service for the hosts composing the
   system (e.g. the Data Store).
3. **operation** — adds access to the hosted service for hosts external to the
   system, i.e. its clients.

## Task files

| File | What it does |
| --- | --- |
| `tasks/main.yml` | Installs `iproute2` and `python3-firewall`, removes `ufw`, installs, enables, and starts `firewalld`, then templates the service definition, the `admin`, `system`, and `external` ipsets, the `<service>_maintenance` zone, a `block` zone bound to the network interface, and the `<service>_operation` zone. The operation zone is written with `force: false`, so an existing one is left alone. |
| `tasks/mode_maintenance.yml` | Re-templates `<service>_operation.xml`, which removes any source ipsets from it. |
| `tasks/mode_testing.yml` | Adds the `<service>_system` ipset as a source of the operation zone and removes any `_external` source. |
| `tasks/mode_operation.yml` | Adds both the `<service>_system` and `<service>_external` ipsets as sources of the operation zone. |

Every template change notifies the `Reload firewalld` handler. Host entries in
the ipset templates that aren't IP addresses or CIDR ranges are resolved with a
`dig` lookup when the template is rendered.

## Variables

| Variable | Required | Default | Comment |
| --- | --- | --- | --- |
| `firewalld_admin_hosts` | yes | | Hosts that can access every port; never blocked |
| `firewalld_external_hosts` | no | `[]` | Hosts outside the system allowed in *operation* mode |
| `firewalld_network_interface` | no | `ansible_default_ipv4.alias` | Interface bound to the `block` zone |
| `firewalld_service_name` | yes | | Service name; also prefixes the ipset and zone names |
| `firewalld_service_ports` | yes | | Ports as `port(/protocol)?`; protocol defaults to `tcp` |
| `firewalld_system_hosts` | no | `[]` | Other system hosts allowed in *testing* and *operation* |

Host and port variables accept a single entry, a list, or a nested list.

## Molecule scenario

`molecule/firewalld` runs against an Ubuntu 24.04 container with systemd. Its
`prepare.yml` installs `ufw` and seeds three operation zone files. `converge.yml`
applies `main.yml` and then the `testing`, `operation`, and `maintenance` mode
task files. `verify.yml` checks that:

- each template renders the expected XML, including a `dig`-resolved host name;
- `firewalld`, `iproute2`, and `python3-firewall` are installed, `ufw` is not,
  and `firewalld` is enabled;
- the service, ipset, and zone files exist and are owned by root;
- each mode left the expected source ipsets in its operation zone.

See [Testing Roles with Molecule](/runbooks/testing-roles-with-molecule.md).

## Notes

In `tasks/mode_operation.yml`, the second task is named "Ensure no external
access", but it adds the external ipset, which is what *operation* mode calls
for.

# Citations

[1] `roles/firewalld/README.md` — role description, variables, and example.
[2] `roles/firewalld/tasks/` — `main.yml` and the three `mode_*.yml` task files.
[3] `roles/firewalld/templates/` — service, ipset, and zone templates.
[4] `roles/firewalld/defaults/main.yml` — variable defaults.
[5] `molecule/firewalld/` — the molecule scenario.
[6] `playbooks/amqp.yml` — the commented-out use of the role.
