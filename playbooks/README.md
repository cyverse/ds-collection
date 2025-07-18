# `cyverse.ds` Playbooks

These folder contains all of the playbooks used to deploy and configure a CyVerse Data Store.

## Playbooks

<!-- TODO: document remaining playbooks -->

* `proxy.yml` completely deploys the proxies
* `proxy_start.yml` starts HAProxy
* `proxy_stop.yml` stops HAProxy
* `proxy_block.yml` terminates all client connections to HAProxy and blocks new connections
* `proxy_unblock.yml` allows client connections to be made

## Tags

* `no_testing` for tasks that shouldn't be run within the containerized testing environment
* `non_idempotent` for tasks that aren't idempotent

## Variables

Variable                                   | Required | Default                              | Choices | Comments
------------------------------------------ | -------- | ------------------------------------ | ------- | --------
`amqp_admin_username`                      | no       | guest                                |         | The AMQP broker admin user
`amqp_admin_password`                      | no       | guest                                |         | The password for `amqp_admin_username`
`amqp_broker_port`                         | no       | 5672                                 |         | The port used by the broker
`amqp_irods_exchange`                      | no       | irods                                |         | The AMQP exchange used by iRODS to publish events
`amqp_irods_username`                      | no       | `amqp_admin_username`                |         | The user iRODS uses to connect to the AMQP vhost
`amqp_irods_password`                      | no       | `amqp_admin_password`                |         | The password iRODS uses to connect to the AMQP vhost
`amqp_irods_vhost`                         | no       | /                                    |         | The AMQP vhost iRODS connects to
`amqp_management_port`                     | no       | 15672                                |         | The port used by the management interface
`avra_base_collection`                     | no       |                                      |         | The base collection for the Avra project. If it isn't present no Avra rules will fire.
`avra_manager`                             | no       | `irods_clerver_user`                 |         | The iRODS user who is responsible for Avra data.
`avra_resource_hierarchy`                  | no       | `irods_resource_hierarchies[0]`      |         | The resource used by the Avra project
`cereus_collections`                       | no       | []                                   |         | A list of collections whose data belongs on the Cereus resource, each entry must be an absolute path
`cereus_resource_hierarchy`                | no       | `irods_resource_hierarchies[0]`      |         | the Cereus resource used for hosting data for Cereus related projects
`dbms_checkpoint_completion_target`        | no       | 0.9                                  |         | WAL checkpoint target duration fraction
`dbms_checkpoint_timeout`                  | no       | 15                                   |         | WAL checkpoint timeout in minutes
`dbms_effective_cache_size`                | no       | _see comment_                        |         | the value the query planner uses to estimate the total size of data caches in GiB, the default in 50% of the total memory
`dbms_effective_io_concurrency`            | no       | 200                                  |         | the number of concurrent disk I/O operations that can be executed simultaneously
`dbms_irods_password`                      | yes      |                                      |         | the password used to authenticate the iRODS PostgreSQL account
`dbms_irods_username`                      | no       | irods                                |         | the PostgreSQL account iRODS uses to connect to the ICAT DB
`dbms_log_line_prefix`                     | no       | < %m %r >                            |         | PostgreSQL log message prefix (see PostgreSQL documentation for possible values)
`dbms_log_min_duration`                    | no       | 1000                                 |         | the number of milliseconds a query should take before it is logged in the DBMS logs. `-1` disables query logging
`dbms_maintenance_work_mem`                | no       | 2                                    |         | the amount of memory in gibibytes for maintenance operations
`dbms_max_connections`                     | no       | 1500                                 |         | the maximum number of connections allowed to the DBMS (change requires restart)
`dbms_max_wal_senders`                     | no       | 120                                  |         | the maximum number of WAL sender processes (change requires restart)
`dbms_max_wal_size`                        | no       | 8                                    |         | the maximum size of a WAL file in gibibytes
`dbms_max_worker_processes`                | no       | _see comment_                        |         | the maximum number of concurrent worker processes, default is the number of processors (change requires restart)
`dbms_max_parallel_maintenance_workers`    | no       | 2*                                   |         | the maximum number of parallel processes per maintenance operations, *must be no larger than `max_worker_processes`, so if that is 1, then the default is 1
`dbms_max_parallel_workers_per_gather`     | no       | 2*                                   |         | the maximum number of parallel processes that can be started by a single gather or gather merge, *must be no larger than `max_worker_processes`, so if that is 1, then the default is 1
`dbms_mem_num_huge_pages`                  | no       | 60000                                |         | the number of huge memory pages supported by the DBMS
`dbms_min_wal_size`                        | no       | 2                                    |         | the minimum size of a WAL file in gibibytes
`dbms_pg_hba`                              | no       | /etc/postgresql/12/main/pg_hba.conf  |         | The absolute path to the pg_hba.conf file on the DBMS hosting the ICAT DB
`dbms_port`                                | no       | 5432                                 |         | the TCP port used by the DBMS (change requires restart)
`dbms_random_page_cost`                    | no       | 1.1                                  |         | the query planning cost of a random page retrieval relative to other costs
`dbms_reboot_allowed`                      | no       | false                                |         | whether or not the playbooks are allowed to reboot the DBMS server
`dbms_replication_password`                | maybe*   |                                      |         | the password for authenticating `dbms_replication_username`, *this is required if replication is being set up
`dbms_replication_start`                   | no       | false                                |         | whether or not the role should start replication. WARNING: THIS WILL DESTROY THE CURRENT REPLICA
`dbms_replication_username`                | no       | postgres                             |         | the DBMS user authorized to replicate the master node
`dbms_restart_allowed`                     | no       | false                                |         | whether or not the playbooks are allowed to restart PostgreSQL
`dbms_wal_keep_segments`                   | no       | 4000                                 |         | the number of WAL files held by the primary server for its replica servers
`dbms_work_mem`                            | no       | 32                                   |         | the allowed memory in mebibytes for each sort and hash operation
`infra_domain_name`                        | yes      |                                      |         | The public FQDN for the environment being configured. This is used for configuring services that require a public domain to work, like mail.
`infra_maintainer_keys`                    | no       | []                                   |         | A list of public ssh keys allowed or disallowed to connect as the `ansible_user` on all of the managed hosts, __see below__
`infra_mtu`                                | no       | 1500                                 |         | The MTU to set on the primary NIC
`infra_package_manager`                    |          | no                                   | auto    | The package manager to use
`infra_proxied_ssh`                        | no       | false                                |         | Whether or not the connection ansible uses to get to the managed node goes through a bastion host
`infra_reboot_on_pkg_change`               | no       | false                                |         | Whether or not to automatically reboot the host if a system package was upgraded
`infra_rebootable`                         | no       | true                                 |         | Whether or not the server being configured is rebootable
`infra_sysctl_net`                         | no       | []                                   |         | a list of sysctl network parameters to set for the server being configured, __see below__
`infra_txqueuelen`                         | no       | 1000                                 |         | The transmission queue length to set on the primary NIC
`irods_admin_password`                     | no       | `irods_clerver_password`             |         | The iRODS admin account password
`irods_admin_username`                     | no       | `irods_clerver_user`                 |         | The iRODS admin account name
`irods_amqp_exchange`                      | no       | irods                                |         | The AMQP exchange used to publish events
`irods_amqp_host`                          | no       | localhost                            |         | the FQDN or IP address of the server hosting the AMQP service
`irods_amqp_port`                          | no       | 5672                                 |         | The TCP port the RabbitMQ broker listens on
`irods_amqp_username`                      | no       | guest                                |         | The user iRODS uses to connect to the AMQP vhost
`irods_amqp_password`                      | no       | guest                                |         | The password iRODS uses to connect to the AMQP vhost
`irods_amqp_vhost`                         | no       | /                                    |         | The AMQP vhost iRODS connects to
`irods_allowed_clients`                    | no       | 0.0.0.0/0                            |         | The network/mask for the clients allowed to access iRODS.
`irods_become_svc_acnt`                    | no       | true                                 |         | Whether or not to perform actions normally performed by the service account as the service account
`irods_build_dir`                          | no       | /tmp                                 |         | The directory used for building artifacts for deployment
`irods_canonical_hostname`                 | no       | `groups['irods_catalog'][0]`         |         | The external FQDN used to access the data store services
`irods_canonical_zone_port`                | no       | 1247                                 |         | The port on the `canonical_hostname` host listening for connections to iRODS
`irods_check_routes_timeout`               | no       | 3                                    |         | The number of seconds the `check_route` playbook will wait for a response during a single port check
`irods_clerver_password`                   | no       | rods                                 |         | The password used to authenticate the clerver
`irods_clerver_user`                       | no       | rods                                 |         | the rodsadmin user to be used by the server being configured
`irods_db_password`                        | no       | testpassword                         |         | The password iRODS uses when connecting to the ICAT DB.
`irods_db_username`                        | no       | irods                                |         | The user iRODS uses when connecting to the ICAT DB.
`irods_dbms_host`                          | no       | `groups['irods_catalog'][0]`         |         | The host of the DBMS that provides the ICAT DB.
`irods_dbms_port`                          | no       | 5432                                 |         | The TCP port the DBMS listens on.
`irods_default_dir_mode`                   | no       | 0750                                 |         | The default permissions assigned to newly created directories in the vault
`irods_default_file_mode`                  | no       | 0600                                 |         | The default permissions assigned to newly created files in the vault
`irods_default_number_of_transfer_threads` | no       | 3                                    |         | The default maximum number of transfer streams for parallel transfer
`irods_default_repl_resource`              | no       | `irods_default_resource`             |         | The default resource for replication
`irods_default_resource`                   | no       | `irods_resource_hierarchies[0].name` |         | the name of the default resource
`irods_default_vault`                      | no       |                                      |         | The default path to the vault on the server being configured
`irods_federation`                         | no       | []                                   |         | A list of other iRODS zones to federate with, _see below_
`irods_host_aliases`                       | no       | []                                   |         | A list of other names and addresses used to refer to the host being configured.
`irods_init_repl_delay`                    | no       | 0                                    |         | the initial number of seconds iRODS waits before attempting to replicate a new or modified data object
`irods_max_num_re_procs`                   | no       | 4                                    |         | The maximum number of rule engine processes to run
`irods_negotiation_key`                    | no       | TEMPORARY_32byte_negotiation_key     |         | The negotiation key
`irods_odbc_driver`                        | no       | PostgreSQL                           |         | The name of the ODBC driver iRODS uses to communicate with the DBMS
`irods_other_host_entries`                 | no       | []                                   |         | A list of other FQDNs to add to /etc/hosts
`irods_parallel_transfer_buffer_size`      | no       | 100                                  |         | The transfer buffer size in MiB for each stream during parallel transfer
`irods_publish_rs_image`                   | no       | false                                |         | Whether or not to publish a freshly build resource server docker image to dockerhub.
`irods_re_host`                            | no       | `groups['irods_catalog'][0]`         |         | The FQDN or IP address of the iRODS rule engine host
`irods_report_email_addr`                  | no       | root@localhost                       |         | The address where reports are to be emailed.
`irods_resource_hierarchies`               | no       | `[ { "name": "demoResc" } ]`         |         | The list of resource hierarchies that need to exist, _see below_
`irods_restart_allowed`                    | no       | false                                |         | The services can be restarted if needed
`irods_rs_image`                           | no       | ds-irods-rs-onbuild                  |         | The name of the unpublished RS image to be generated
`irods_s3_cred`                            | no       | []                                   |         | The list of S3 credential pairs that allow iRODS to access managed S3 buckets, _see below_
`irods_server_control_plane_key`           | no       | TEMPORARY__32byte_ctrl_plane_key     |         | The server control plane key
`irods_server_port_range_end`              | no       | 20199                                |         | The last address in the range of auxiliary TCP and UDP ports
`irods_server_port_range_start`            | no       | 20000                                |         | The first address in the range of auxiliary TCP and UDP ports
`irods_service_account_name`               | no       | irods                                |         | The system account used to run the iRODS server processes
`irods_service_group_name`                 | no       | `irods_service_account_name`         |         | The system group used to run the iRODS server processes
`irods_storage_resources`                  | no       | []                                   |         | A list of storage resources hosted on the server being configured, _see below_
`irods_sysctl_kernel`                      | no       | []                                   |         | A list of sysctl kernel parameters to set on the iRODS catalog service provider, _see_below_
`irods_user_password_salt`                 | no       |                                      |         | The salt used when obfuscating user passwords stored in the catalog database
`irods_version`                            | no       | 4.3.1                                |         | The version of iRODS to work with
`irods_zone_key`                           | no       | TEMPORARY_zone_key                   |         | The zone key
`irods_zone_name`                          | no       | tempZone                             |         | The name of the zone
`mdrepo_cli_account`                       | no       | null                                 |         | The iRODS account used my the MD Repo CLI
`pire_manager`                             | no       | null                                 |         | The username that owns the PIRE project collection, if `null`, the collection isn't created.
`pire_resource_hierarchy`                  | no       | `irods_resource_hierarchies[0]`      |         | The resource used by the PIRE project
`proxy_allow_client_hosts`                 | no       | []                                   |         | A list of host names, IP addresses, and CIDR blocks of clients allowed limited concurrent iRODS connections
`proxy_block_client_hosts`                 | no       | []                                   |         | A list of host names, IP addresses, and CIDR blocks of clients not allowed to use the Data Store
`proxy_restart_allowed`                    | no       | false                                |         | Whether or not HAProxy can be restarted
`proxy_rsyslog_conf`                       | no       | /etc/rsyslog.d/haproxy.conf          |         | the path to the rsyslog configuration file for HAProxy
`proxy_stats_auth`                         | no       | null                                 |         | an object providing the authentication credentials for the HAProxy stats web interface _see below_
`proxy_stats_tls_crt`                      | no       | null                                 |         | the absolute path to the TLS certificate chain used for securing the HAProxy stats web interface
`proxy_stats_tls_crt_content`              | no       | null                                 |         | the content of the TLS certificate chain file
`proxy_irods_direct_max_conn`              | no       | 200                                  |         | the maximum number of connections to iRODS
`proxy_irods_reconn_ports`                 | no       | 20000-20399                          |         | the range of TCP range of ports that need to be forwarded to iRODS for reconnections
`proxy_sftp_port`                          | no       | 22                                   |         | the TCP port hosting the SFTP service whose communication will be forwarded to SFTPGo
`proxy_sftp_backend_port`                  | no       | 2022                                 |         | the TCP port that SFTPGo opens on the hosts
`proxy_vip_client_hosts`                   | no       | []                                   |         | a list of host names, IP addresses, and CIDR blocks of clients allowed unlimited concurrent iRODS connections.
`sftp_admin_password`                      | yes      |                                      |         | The password of the SFTPGo admin user
`sftp_admin_tls_cert_chain`                | no       |                                      |         | The TLS certificate chain contents for SFTPGo admin access, if not provided will not create file
`sftp_admin_tls_cert_chain_file`           | no       | /etc/ssl/certs/dummy-chain.crt       |         | The TLS certificate chain file for SFTPGo admin access
`sftp_admin_tls_key`                       | no       |                                      |         | The TLS key contents for SFTPGo admin access, if not provided, will not create file
`sftp_admin_tls_key_file`                  | no       | /etc/ssl/certs/dummy.key             |         | The TLS key file for SFTPGo admin access
`sftp_admin_ui_port`                       | no       | 18023                                |         | The SFTPGo admin UI service port number
`sftp_admin_username`                      | no       | admin                                |         | The SFTPGo admin account name
`sftp_irods_admin_password`                | yes      |                                      |         | The password for the rodsadmin user that creates the iRODS user for SFTP
`sftp_irods_admin_username`                | no       | rods                                 |         | The rodsadmin user that creates tbe iRODS user for SFTP
`sftp_irods_auth_scheme`                   | no       | native                               |         | The auth scheme of irods. 'pam' and 'pam_for_users' are also available.
`sftp_irods_host`                          | no       | localhost                            |         | The hostname of the iRODS server SFTP uses
`sftp_irods_port`                          | no       | 1247                                 |         | The iRODS SFTP will use to connect to iRODS
`sftp_irods_proxy_password`                | yes      |                                      |         | The password of the SFTPGo irods proxy user
`sftp_irods_proxy_username`                | no       | sftp                                 |         | The irods user who provides proxy access to SFTPGo
`sftp_irods_ssl_algorithm`                 | no       |                                      |         | The SSL encryption algorithm (required by PAM auth scheme)
`sftp_irods_ssl_ca_cert_path`              | no       |                                      |         | The SSL CA certificate file path (required by PAM auth scheme)
`sftp_irods_ssl_hash_rounds`               | no       | 0                                    |         | The SSL encryption hash rounds (required by PAM auth scheme)
`sftp_irods_ssl_key_size`                  | no       | 0                                    |         | The SSL encryption key size (required by PAM auth scheme)
`sftp_irods_ssl_salt_size`                 | no       | 0                                    |         | The SSL encryption salt size (required by PAM auth scheme)
`sftp_irods_zone`                          | no       | tempZone                             |         | The iRODS zone that SFTP connects to
`sftp_port`                                | no       | 2022                                 |         | The SFTP service port number
`sftp_proxy_allowed`                       | no       | `[]`                                 |         | A list of network/masks for the proxy servers allowed access to the SFTP servers
`sftp_user_host_allowed`                   | no       | `[]`                                 |         | A list of ip addresses of the user hosts allowed (whitelisted) for access to the SFTP servers
`sftp_user_host_rejected`                  | no       | `[]`                                 |         | A list of ip addresses of the user hosts rejected (blacklisted) for access to the SFTP servers
`sftp_vault_dir`                           | no       | /sftpgo_vault                        |         | The directory SFTPGo will use for saving state
`webdav_access_limit`                      | no       |                                      |         | If defined, the upper limit on the number of simultaneous requests that will be served by webdav
`webdav_allowed_src`                       | no       | `[ "0.0.0.0/0" ]`                    |         | A list of network/masks for the clients allowed direct access to the WebDAV servers
`webdav_amqp_exchange`                     | no       | irods                                |         | The AMQP exchange used to publish events
`webdav_amqp_host`                         | no       | localhost                            |         | the FQDN or IP address of the server hosting the AMQP service
`webdav_amqp_password`                     | no       | guest                                |         | The password iRODS uses to connect to the AMQP vhost
`webdav_amqp_port`                         | no       | 5672                                 |         | The TCP port the RabbitMQ broker listens on
`webdav_amqp_username`                     | no       | guest                                |         | The user iRODS uses to connect to the AMQP vhost
`webdav_amqp_vhost`                        | no       | /                                    |         | The AMQP vhost iRODS connects to
`webdav_auth_name`                         | no       | CyVerse                              |         | Authorization realm to use for the Data Store
`webdav_cache_dir`                         | no       | /var/cache/varnish                   |         | The directory varnish-cache will use for the WebDAV cache
`webdav_cache_max_file_size`               | no       | 10                                   |         | The maximum size in mebibytes of the largest WebDAV file varnish-cache will cache
`webdav_cache_max_ttl`                     | no       | 86400                                |         | The maximum cache TTL in seconds
`webdav_cache_size`                        | no       | 1000                                 |         | The maximum size in mebibytes the cache can be
`webdav_cache_ttl_fraction`                | no       | 0.1                                  |         | The fraction elapsed time since the last-modified time of a file for cache TTL (Time-to-live) configuration
`webdav_canonical_hostname`                | no       | localhost                            |         | The FQDN or IP address of the WebDAV service.
`webdav_irods_access_limit`                | no       |                                      |         | If defined, the upper limit on the number of simultaneous requests that will be served by davrods
`webdav_irods_host`                        | no       | localhost                            |         | The host name of the iRODS catalog provider WebDAV will use
`webdav_irods_password`                    | yes      |                                      |         | The password of the purgeman irods user
`webdav_irods_port`                        | no       | 1247                                 |         | The TCP port WebDAV will use to connect to iRODS
`webdav_irods_username`                    | no       | rods                                 |         | The irods user who converts data object uuid to path
`webdav_irods_zone`                        | no       | tempZone                             |         | The local iRODS zone
`webdav_max_request_workers`               | no       | 192                                  |         | The upper limit on the number of simultaneous requests that will be served. This typically have the value of `webdav_server_limit` multiplied by `webdav_threads_per_child`
`webdav_restart_allowed`                   | no       | false                                |         | Indicated if the WebDAV service can be restarted
`webdav_server_limit`                      | no       | 48                                   |         | the number of cpu cores to be used
`webdav_threads_per_child`                 | no       | 4                                    |         | the number of threads per core to be created
`webdav_tls_cert`                          | no       |                                      |         | The TLS certificate file contents
`webdav_tls_cert_file`                     | no       | /etc/ssl/certs/dummy.crt             |         | The TLS certificate file used for encrypted communication
`webdav_tls_chain`                         | no       |                                      |         | The TLS certificate chain file contents
`webdav_tls_chain_file`                    | no       | /etc/ssl/certs/dummy-chain.crt       |         | The TLS certificate chain file used for encrypted communication
`webdav_tls_key`                           | no       |                                      |         | The TLS key
`webdav_tls_key_file`                      | no       | /etc/ssl/certs/dummy.key             |         | The TLS key file used for encrypted communication
`webdav_varnish_service_port`              | no       | 6081                                 |         | The service port number for varnish-cache

An element of `infra_maintainer_keys` is either a string or a mapping with the following fields.

Field   | Required | Default | Choices        | Comments
--------|----------|---------|----------------|---------
`key`   | yes      |         |                | The public ssh key
`state` | no       | present | absent,present | 'present' indicates that this can be used to authorize a connection and 'absent' indicates the opposite

If it is a string, its value is assumed to be a public ssh key that can be used to authorized a connection.

`infra_sysctl_net` entry fields

Both of them are required.

Field   | Comments
--------|---------
`name`  | The parameter name to modify
`value` | The new value to set

`irods_federation` entry fields

All of them are required.

Field                    | Comments
------------------------ | --------
`catalog_provider_hosts` | A list of the catalog service providers in the federate, each indicated by its FQDN or IP address
`negotiation_key`        | The 32-byte encryption key of the federate
`zone_key`               | The shared authentication secret of the federate
`zone_name`              | The name of the federated zone

`irods_resource_hierarchies` entry fields

Field      | Required | Default | Comments
---------- | -------- | ------- | --------
`children` | no       | `[]`    | A list of child hierarchy definitions have the same form as an `irods_resource_hierarchies` entry
`context`  | no       |         | A context to attach to this resource
`name`     | yes      |         | The name of the resource
`type`     | no       |         | For a coordinating resource, this is the type of resource. For a storage resource this should not be provided.

`irods_s3_cred` entry fields

All of them are required.

Field        | Comments
-------------|---------
`name`       | the unique name identifying the file name holding the credentials
`access_key` | the key used to authorize access
`secret_key` | the key used to authenticate the access key

`irods_storage_resources` entry fields

All of them are required.

Field     | Comments
--------- | --------
`context` | The context to assign to the resource
`name`    | The name of the storage resource
`vault`   | The absolute path to the vault hold the files on this resource.

`irods_sysctl_kernel` entry fields

Both of them are required.

Field    | Comments
-------- | --------
`name`   | The parameter name to modify
`value`  | The new value to set

`proxy_stats_auth` object fields

Field      | Required | Default | Comments
---------- | -------- | ------- | --------
`username` | no       | ds      | the account authorized to access the stats web interface
`password` | yes      |         | the password used to authenticate the account
`realm`    | no       |         | the realm of the authentication system

## Command line variables

Initializing rodsadmin group permissions when a lot of data objects exist, can take a very long time. By default this is skipped, but if `init_rodsadmin_perms=true` is set on the command line,the `irods_runtime_init` playbook will ensure rodsadmin group permissions are set correctly.
