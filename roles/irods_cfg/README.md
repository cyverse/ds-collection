# cyverse.ds.irods_cfg

This role will eventually be able to be used to completely configure an iRODS server once iRODS is installed. At the moment, it can maintain the following configuration files.

* irods_environment.json
* etc/irods/server_config.json
* etc/irods/service_account.config

## Requirements

iRODS 4.3.1 is installed.

## Tasks Files

The `main.yml` tasks file that is called by default performs the same tasks as `server.yml`, i.e., it deploys the set of files required by an iRODS server.

There are two tier-specific tasks files. `client.yml` deploys the configuration files required by a client, e.g., the iCommands. Currently, it deploys the irods_environment.json file. `server.yml` deploys the configuration files required by an iRODS server.

For each iRODS configuration file there is a corresponding tasks file that deploys only that configuration file. `irods_environment.yml` deploys the client or clerver configuration file, _irods_environment.json_ by default. In the `etc/irods/` directory, `server_config.yml` deploys server_config.json and `service_account.yml` deploys service_account.config.

The `setup_irods.yml` task file is not part of `main.yml` or either of the tier-specific tasks files. `setup_irods.yml` initializes the ICAT DB before calling `server.yml`.

## Role Variables

Here are the role variables. None of them are required.

Variable                                                     | Default                                                                              | Choices                                          | Comment
------------------------------------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------ | -------
`irods_cfg_access_entries`                                   | []                                                                                   |                                                  | A list of access entry objects defining who can access iRODS and from where, see below
`irods_cfg_agent_factory_watcher_sleep_time`                 | 5                                                                                    |                                                  | the number of seconds between runs of the CRON task which ensures that the agent factory is running
`irods_cfg_authentication_file`                              | /var/lib/irods/.irods/.irodsA                                                        |                                                  | the authentication file for the client or clerver
`irods_cfg_catalog_provider_hosts`                           | \[ `inventory_hostname` \]                                                           |                                                  | a list of FQDNs or IP addresses of the catalog service providers
`irods_cfg_catalog_service_role`                             | provider                                                                             | consumer, provider                               | the role of the iRODS server, a provider directly accesses the catalog database, a consumer does not
`irods_cfg_chown`                                            | true                                                                                 |                                                  | whether or not to make the service account the owner of the generate files
`irods_cfg_client_api_allowlist_policy`                      | enforce                                                                              | disabled, enforce                                | controls which API operations are accessible to non-rodsadmin users
`irods_cfg_client_authentication_scheme`                     | native                                                                               | gsi, krb, native, pam                            | the authentication scheme used by a client
`irods_cfg_client_default_hash_scheme`                       | `irods_cfg_default_hash_scheme`                                                      | MD5, SHA256                                      | checksum scheme for the client or clerver
`irods_cfg_client_default_resource`                          | `irods_cfg_default_resource_name` _but see comment_                                  |                                                  | the name of the resource used for client or clerver operations if one is not specified, on the clerver, if `irods_cfg_default_resource_name`
`irods_cfg_client_encryption_algorithm`                      | `irods_cfg_server_control_plane_encryption_algorithm`                                |                                                  | EVP-supplied encryption algorithm for parallel transfer
`irods_cfg_client_encryption_key_size`                       | 32                                                                                   |                                                  | key size for parallel transport encryption
`irods_cfg_client_encryption_num_hash_rounds`                | `irods_cfg_server_control_plane_encryption_num_hash_rounds`                          |                                                  | number of hash rounds for parallel transfer encryption
`irods_cfg_client_encryption_salt_size`                      | 8                                                                                    |                                                  | salt size for parallel transfer encryption
`irods_cfg_client_log_level`                                 | 5                                                                                    | 1 - 10                                           | desired verbosity of logging by the client or clerver
`irods_cfg_client_server_negotiation`                        | request_server_negotiation                                                           | none, request_server_negotiation                 | whether or not advanced negotiation is desired for the client or clerver
`irods_cfg_client_server_policy`                             | CS_NEG_REFUSE                                                                        | CS_NEG_DONT_CARE, CS_NEG_REFUSE, CS_NEG_REQUIRE  | which SSL policy for the client or clerver to use
`irods_cfg_connection_pool_refresh_time`                     | 300                                                                                  |                                                  | the number of seconds after which an existing connection in a connection pool is refreshed
`irods_cfg_controlled_user_connection_list`                  | _see below_                                                                          |                                                  | defines the list of users that can connect to this server, _see below_
`irods_cfg_cmd_scripts`                                      | []                                                                                   |                                                  | a list of command scripts specified by relative file path globs
`irods_cfg_cwd`                                              | `irods_cfg_home`                                                                     |                                                  | the initial working collection for the admin user
`irods_cfg_database`                                         | _see comment_                                                                        |                                                  | The ICAT DB configuration object. _See below_. If the server being configured isn't a catalog provider, this will be ignored.
`irods_cfg_database_user_password_salt`                      |                                                                                      |                                                  | the salt used when obfuscating user passwords stored in the catalog database
`irods_cfg_debug`                                            | ''                                                                                   | '' or any combination of 'CAT', 'RDA', and 'SQL' | desired verbosity of the debug logging level for client or  clerver. e.g., 'CATRDA' means include CAT and RDA debugging in debug log messages
`irods_cfg_default_dir_mode`                                 | 0750                                                                                 |                                                  | the Unix file system octal permission mode for a newly created directory
`irods_cfg_default_file_mode`                                | 0600                                                                                 |                                                  | the Unix file system octal permission mode for a newly created file
`irods_cfg_default_hash_scheme`                              | SHA256                                                                               | MD5, SHA256                                      | the hash scheme used for file integrity checking
`irods_cfg_default_number_of_transfer_threads`               | 4                                                                                    |                                                  | the default maximum number of threads allowed for parallel transfer
`irods_cfg_default_resource_directory`                       |                                                                                      |                                                  | the default Vault directory for the initial resource on server installation
`irods_cfg_default_resource_name`                            | demoResc                                                                             |                                                  | the name of the initial resource on server installation
`irods_cfg_default_temporary_password_lifetime`              | 120                                                                                  |                                                  | the default number of seconds a server-side temporary password is valid
`irods_cfg_delay_rule_executors`                             | []                                                                                   |                                                  | a list of iRODS server host names the delay server dispatches rules to for execution
`irods_cfg_delay_server_sleep_time                           | 30                                                                                   |                                                  | The number of seconds the delay server sleeps before checking the catalog for rules ready for execution.
`irods_cfg_environment_file`                                 | home/`irods_cfg_system_account_name`/.irods/irods_environment.json _but see comment_ |                                                  | the location where the iRODS environment file should be placed relative to `irods_cfg_root_dir`. For server configuration, the default is `'var/lib/irods/.irods/irods_environment.json'`.
`irods_cfg_environment_variables`                            | {}                                                                                   |                                                  | a set of environment variables to add to the server process environment
`irods_cfg_federation`                                       | []                                                                                   |                                                  | an array of federation objects identifying the zones this zone federates with, see below
`irods_cfg_for_server`                                       | false _but see comment_                                                              |                                                  | whether or not a server is being configured. If the `main` or `server` tasks are run, this is forced to `true`. If the `client` tasks are run, this is forced to be `false`.
`irods_cfg_gsi_server_dn`                                    | null                                                                                 |                                                  | the distinguished name of the GSI server
`irods_cfg_home`                                             | /`irods_cfg_zone_name`/home/`irods_cfg_zone_user`                                    |                                                  | the home collection of the admin user
`irods_cfg_host`                                             | `inventory_name`                                                                     |                                                  | the fully qualified domain name of the server the client or clerver connects to
`irods_cfg_host_entries`                                     | []                                                                                   |                                                  | an array of host entry objects grouping host names and addresses referring to the same host, see below
`irods_cfg_log_level`                                        | _see below_                                                                          |                                                  | holds the log level for various log message categories used throughout the server, _see below_
`irods_cfg_match_hash_policy`                                | compatible                                                                           | compatible, strict                               | indicates to iRODS whether to use the hash used by the client or the data at rest, or to force the use of the default hash scheme
`irods_cfg_maximum_connections`                              |                                                                                      |                                                  | if set, this limits the maximum number of connections to a server to this number
`irods_cfg_maximum_size_for_single_buffer`                   | 32                                                                                   |                                                  | the maximum size in mebibytes for a single buffer
`irods_cfg_maximum_size_of_delay_queue`                      | 0                                                                                    |                                                  | the maximum number of bytes available to the delay queue, zero means unlimited
`irods_cfg_maximum_temporary_password_lifetime`              | 1000                                                                                 |                                                  | the maximum number of seconds a server-side temporary password can be valid
`irods_cfg_migrate_delay_server_sleep_time`                  | 5                                                                                    |                                                  | The number of seconds between runs of the CRON task which executes the delay server migration algorithm
`irods_cfg_negotiation_key`                                  | 32_byte_server_negotiation_key__                                                     |                                                  | a 32-byte encryption key shared by the zone for use in the advanced negotiation handshake at the beginning of an iRODS client connection
`irods_cfg_number_of_concurrent_delay_rule_executors`        | 4                                                                                    |                                                  | the maximum number of rule engine processes to run
`irods_cfg_plugins_home`                                     |                                                                                      |                                                  | directory to use for the client side plugins
`irods_cfg_re                                                | core                                                                                 | _see below_                                      | The configuration of the iRODS rule language rule engine plugin.
`irods_cfg_restart_allowed`                                  | false                                                                                |                                                  | indicates if the role is allowed to restart an iRODS service
`irods_cfg_root_dir`                                         | /                                                                                    |                                                  | The root directory where all depositions are relative to
`irods_cfg_rule_engine_namespaces`                           | `[ "" ]`                                                                             |                                                  | defines the list of namespaces used during PEP processing
`irods_cfg_rule_engine_server_sleep_time`                    | 30                                                                                   |                                                  | how frequently the rule engine polls for scheduled rules when idle in seconds
`irods_cfg_rulebases_static`                                 | []                                                                                   |                                                  | a list of rulebases specified by relative file path globs
`irods_cfg_rulebases_templated`                              | []                                                                                   |                                                  | a list of Jinja2 templates that expand to iRODS rulebases. The templates should be specified by relative file path globs. The `.j2` file extension will be removed when deployed.
`irods_cfg_schema_validation_base_uri`                       | `file:///var/lib/irods/configuration_schemas`                                        | a URI or 'off'                                   | the URI against which the iRODS server configuration is validated. 'off' means to skip validation
`irods_cfg_server_control_plane_encryption_algorithm`        | AES-256-CBC                                                                          |                                                  | the algorithm used to encrypt control plane communications
`irods_cfg_server_control_plane_encryption_num_hash_rounds`  | 16                                                                                   |                                                  | the number of hash rounds used in the control plane communications
`irods_cfg_server_control_plane_key`                         | 32_byte_server_control_plane_key                                                     |                                                  | the the encryption key required for communicating with the iRODS grid control plane, must be 32 bytes
`irods_cfg_server_control_plane_port`                        | 1248                                                                                 |                                                  | the port on which the control plane operates
`irods_cfg_server_control_plane_timeout`                     | 10000                                                                                |                                                  | the number of milliseconds before control plane times out
`irods_cfg_server_port_range_end`                            | 20199                                                                                |                                                  | the ending of the port range available for re-connections, parallel transfer and RBUDP transfer
`irods_cfg_server_port_range_start`                          | 20000                                                                                |                                                  | the beginning of the port range available for re-connections, parallel transfer and RBUDP transfer
`irods_cfg_ssl_ca_certificate_file`                          |                                                                                      |                                                  | location of a file of trusted CA certificates in PEM format
`irods_cfg_ssl_ca_certificate_path`                          |                                                                                      |                                                  | location of a directory containing CA certificates in PEM format
`irods_cfg_ssl_certificate_chain_file`                       |                                                                                      |                                                  | the file containing the server's certificate chain
`irods_cfg_ssl_certificate_key_file`                         |                                                                                      |                                                  | private key corresponding to the server's certificate in the certificate chain file
`irods_cfg_ssl_dh_params_file`                               |                                                                                      |                                                  | the Diffie-Hellman parameter file location
`irods_cfg_ssl_verify_server`                                | hostname                                                                             | cert, hostname, none                             | level of server certificate based authentication to perform
`irods_cfg_stacktrace_file_processor_sleep_time`             | 10                                                                                   |                                                  | the amount of time the stacktrace file processing thread sleeps before files are processed and written to the log file.
`irods_cfg_system_account_name`                              | irods                                                                                |                                                  | the account used to run iRODS
`irods_cfg_system_group_name`                                | `irods_cfg_system_account_name`                                                      |                                                  | the group used to run iRODS
`irods_cfg_tcp_keepalive_intvl`                              | -1                                                                                   |                                                  | the number of seconds between TCP keep-alive probes, if non-positive, leave socket opt unset
`irods_cfg_tcp_keepalive_probe`                              | -1                                                                                   |                                                  | the maximum number of TCP keep-alive probes to send before giving up and killing the connection if no response is obtained from the other end, if non-positive, leave socket opt unset
`irods_cfg_tcp_keepalive_time`                               | -1                                                                                   |                                                  | the number of seconds a connection needs to be idle before TCP begins sending out keep-alive probes, if non-positive, leave socket opt unset
`irods_cfg_test_log`                                         | false                                                                                |                                                  | if the iRODS server process gets restarted, should log messages be written to /var/lib/irods/log/test_mode_output.log
`irods_cfg_transfer_buffer_size_for_parallel_transfer`       | 4                                                                                    |                                                  | the buffer size in mebibytes for parallel transfer
`irods_cfg_transfer_chunk_size_for_parallel_transfer`        | 40                                                                                   |                                                  | the chunk size in mebibytes for parallel transfer
`irods_cfg_validate`                                         | true                                                                                 |                                                  | whether or not the configuration values should be validated when the configuration files are generated
`irods_cfg_zone_auth_scheme`                                 | native                                                                               | native, pam_password                             | the authentication scheme used by `irods_cfg_zone_user` on the clerver.
`irods_cfg_zone_key`                                         | TEMPORARY_ZONE_KEY                                                                   |                                                  | the shared secret used for authentication and identification on server-to-server communication, it cannot contain hyphens (`-`)
`irods_cfg_zone_name`                                        | tempZone                                                                             |                                                  | the name of the in which the server participates
`irods_cfg_zone_password`                                    | rods                                                                                 |                                                  | the password used to authenticate `irods_cfg_zone_user`.
`irods_cfg_zone_port`                                        | 1247                                                                                 |                                                  | the main port used by the zone for communication
`irods_cfg_zone_user`                                        | rods                                                                                 |                                                  | the name of the rodsadmin user running this iRODS instance

The `irods_cfg_access_entries` variables is an array of `access_entry` objects. An `access_entry` object has the following fields, all of them required.

Field     | Comments
--------- | --------
`address` | the IPv4 address of a host or network that is able to access
`group`   | the iRODS group able to access
`mask`    | the network mask when `address` is a network address
`user`    | the iRODS user able to access

The `irods_cfg_controlled_user_connection_list` variable holds and object with the following fields, both of which are optional.

Field          | Default  | Choices             | Comments
---------------|----------|---------------------|---------
`control_type` | denylist | allowlist, denylist | defines the type of list
`users`        | []       |                     | a list of fully qualified user names in the form of "username#zone"

The `irods_cfg_database` variable is an `icat` object. An `icat` object has the following fields, none of them are required.

Field            | Default         | Choices                 | Comments
-----------------| ----------------|-------------------------|---------
`db_host`        | localhost       |                         | the hostname of the DBMS
`db_name`        | ICAT            |                         | the name of the database used as the iCAT
`db_odbc_driver` | PostgreSQL ANSI |                         | The ODBC driver to use, by default
`db_password`    | testpassword    |                         | the password used by `db_username` to connect to `db_name`
`db_port`        | 5432            |                         | the port on which the database server is listening
`db_type`        | postgres        | mysql, oracle, postgres | the type of database iRODS is using for the iCAT. _see below_
`db_username`    | irods           |                         | the database user name

For `db_type`, only `postgres` has been fully tested.

The `irods_cfg_environment_variables` variable is a dictionary where the key is the name of a server process environment variable, and the value is the value of the environment variable.

The `irods_cfg_federation` variable is an array of `federation` objects. A `federation` object has the following fields, all of them required.

Field                    | Choices | Comments
------------------------ | --------| --------
`catalog_provider_hosts` |         | a list of FQDNs or IP addresses of the catalog service providers in the federated zone
`negotiation_key`        |         | the 32-byte encryption key of the federated zone
`zone_key`               |         | the shared authentication secret with the federated zone
`zone_name`              |         | the name of the federated zone

The `irods_cfg_host_entries` variable is an array of `host_entry` objects. A `host_entry` object has the following fields, all of them required.

Field          | Choices       | Comments
-------------- | ------------- | --------
`address_type` | local, remote | indicates if this host is localhost.
`addresses`    |               | an array of names and addresses referring to this host

The `irods_cfg_log_level` variable holds an object with the following fields, none of them are required.

Field            | Default | Choices
-----------------|---------|--------
`agent`          | info    | trace, debug, info, warn, error, critical
`agent_factory`  | ⋮       | ⋮
`api`            | ⋮       | ⋮
`authentication` | ⋮       | ⋮
`database`       | ⋮       | ⋮
`delay_server`   | ⋮       | ⋮
`legacy`         | ⋮       | ⋮
`microservice`   | ⋮       | ⋮
`network`        | ⋮       | ⋮
`resource`       | ⋮       | ⋮
`rule_engine`    | ⋮       | ⋮
`server`         | ⋮       | ⋮
`sql`            | ⋮       | ⋮

The `irods_cfg_re` variable holds `null`, `core`, or an `re` object. `null` means that no rule engine will be used. `core` means the iRODS rule language rule engine will be used with its default configuration. An `re` object customizes an rule language rule engine. Here are the fields in an `re` object. None of them are required.

Field                               | Default | Comments
------------------------------------|---------|---------
`additional_data_variable_mappings` | []      | an array of file names (without the .dvm extension) that will be loaded in order before core.dvm is loaded
`additional_function_name_mappings` | []      | an array of file names (without the .fnm extension) that will be loaded in order before core.fnm is loaded
`additional_rulebases`              | []      | an array of file names (without the .re extension) that will be loaded in order before core.re is loaded

## Dependencies

None

## Example Playbooks

```yaml
# Client
- hosts: webdav
  vars:
    irods_cfg_environment_file: etc/httpd/irods/irods_environment.json
    irods_cfg_authentication_file: /etc/httpd/irods/.irodsA
    irods_cfg_chown: false
    irods_cfg_host: ares.iplantcollaborative.org
    irods_cfg_zone_name: iplant
    irods_cfg_zone_user: davrods_svc
    irods_cfg_home: /iplant
  tasks:
    - include_role:
        name: cyverse.ds.irods_cfg
        tasks_from: "{{ item }}"
      with_items:
        - client.yml
        - init_zone_user.yml

# Catalog Service Provider
- hosts: irods_catalog_provider
  roles:
    - role: cyverse.ds.irods_cfg
      vars:
        irods_cfg_default_hash_scheme: MD5
        irods_cfg_default_number_of_transfer_threads: 16
        irods_cfg_default_resource_name: CyVerseRes
        irods_cfg_environment_variables:
          amqp_host: amqp.cyverse.org
        irods_cfg_federation:
          - icat_host: irods.tacc.utexas.edu
            negotiation_key: "Don't you wish!                !"
            zone_key: crack me
            zone_name: tacc
        irods_cfg_host_entries:
          - address_type: local
            addresses:
              - ares.iplantcollaborative.org
              - data.cyverse.org
              - data.iplantcollaborative.org
        irods_cfg_database:
          db_host: irods-db.cyverse.org
          db_password: secret
          db_username: icatuser
        irods_cfg_negotiation_key: Just guess it                  .
        irods_cfg_re:
          additional_rulebases:
            - ipc_custom
        irods_cfg_server_control_plane_key: "I'm not telling                ."
        irods_cfg_server_port_range_end: 20399
        irods_cfg_transfer_buffer_size_for_parallel_transfer: 32
        irods_cfg_zone_key: secret
        irods_cfg_zone_name: iplant
        irods_cfg_zone_user: cyverse_admin

# Catalog Service Consumer Acting as a Resource Server
- hosts: irods_resource_server
  roles:
    - role: cyverse.ds.irods_cfg
      vars:
        irods_cfg_default_hash_scheme: MD5
        irods_cfg_default_number_of_transfer_threads: 16
        irods_cfg_default_resource_directory: /f2/haboob
        irods_cfg_default_resource_name: haboobRes
        irods_cfg_negotiation_key: Just guess it                  .
        irods_cfg_re:
          additional_rulebases:
            - ipc_custom
        irods_cfg_server_control_plane_key: "I'm not telling                ."
        irods_cfg_server_port_range_end: 20399
        irods_cfg_transfer_buffer_size_for_parallel_transfer: 32
        irods_cfg_zone_key: secret
        irods_cfg_zone_name: iplant
        irods_cfg_zone_user: has_admin
```
