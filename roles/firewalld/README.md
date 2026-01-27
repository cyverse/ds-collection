# cyverse.ds.firewalld

This role configures firewalld.

## Configuration

This role configures firewalld in an opinionated way for a single service. It provides three configurations.

1. *maintenance* allows only the admin hosts to connect, but these hosts can connect on every TCP and UDP port. It is intended maintenance.
1. *testing* extends *maintenance* allows the hosts composing the system, e.g., Data Store, to connected to the hosted services, but other hosts are blocked. It is assumed that the hosted services belongs to the system. This level is intended for integration testing.
1. *operation* extends *testing* by allowing hosts external to the system, i.e., clients of the system, to connect to the hosted services. This level is intended for production operation of the system.

## Task Sets

* `main.yml`: The default set ensures that installs and configures firewalld, removing ufw. It leaves firewalld enabled and running in *maintenance* mode for the given service.
* `mode_maintenance.yml`: This set puts firewalld into maintenance mode for the given service.
* `mode_operation.yml`: This set puts firewalld into operation mode for the given service.
* `mode_testing.yml`: This set puts firewalld into testing mode for the given service.

## Role Variables

Here are the role variables.

Variable                      | Required | Default       | Comment
------------------------------|----------|---------------|--------
`firewalld_admin_hosts`       | yes      |               | One or more hosts that can access every network port. They are never blocked. This could be a single entry, a list of entries, or a nested list of entries, where each entry is an IP address, a FQDN, or a CIDR range.
`firewalld_external_hosts`    | no       | []            | The set of hosts external to the system that need access to this service when the firewall is configured for *operation*. This could be a single entry, a list of entries, or a nested list of entries, where each entry is an IP address, a FQDN, or a CIDR range.
`firewalld_network_interface` | no       | *see comment* | The name of the network interface used by the service being configured. By default, the interface ansible determines to be the default is used.
`firewalld_service_name`      | yes      |               | The name of the service being configured. It needs to follow firewalld's requirements for a service name.
`firewalld_service_ports`     | yes      |               | The IP port(s) the service listens on. This could be a single entry, a list of entries, or a nested list of entries, where each entry has the form `port(/protocol)?`, where `port` is a port number or port range. If no protocol is provided, it is assumed to be `tcp`.
`firewalld_system_hosts`      | no       | []            | The set of other hosts composing the system that provides the service being configured. These hosts have access to the service when the firewall is configured for *testing* and *operation*. This could be a single entry, a list of entries, or a nested list of entries, where each entry is an IP address, a FQDN, or a CIDR range.

## Example Playbook

```yaml
---
- name: Deploy firewall on AMQP host
  hosts: amqp
  roles:
    - role: cyverse.ds.firewalld
      vars:
        firewalld_service_name: amqp
        firewalld_service_ports: 5672
        firewalld_admin_hosts: ds-adm.cyverse.org
        firewalld_system_hosts: "{{ groups['irods_catalog'] }}"
        firewalld_external_hosts:
          - de.cyverse.org
          - datawatch.cyverse.org
```

## License

BSD
