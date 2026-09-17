# ansible-playbooks

* [amqp_exchange.yml](/ansible-playbooks/amqp-exchange.md) - Creates the iRODS vhost, user permissions, and topic exchange on the RabbitMQ broker using the rabbitmq_vhost role.
* [amqp.yml](/ansible-playbooks/amqp.md) - Installs and configures the RabbitMQ broker on the amqp hosts using the rabbitmq role.
* [avra_usage.yml](/ansible-playbooks/avra-usage.md) - Creates the Avra project's resource hierarchy and project collection in iRODS and binds the collection to the resource.
* [dbms_icat.yml](/ansible-playbooks/dbms-icat.md) - Creates the ICAT database and its iRODS admin user on the primary DBMS, plus the r_transfer_totals table and its unique index.
* [dbms.yml](/ansible-playbooks/dbms.md) - Tunes the DBMS hosts' boot parameters and installs and configures PostgreSQL on the primary and replica DBMS hosts using the postgresql role.
* [esiil_usage.yml](/ansible-playbooks/esiil-usage.md) - Creates the ESIIL project's resource hierarchy and project collection in iRODS and binds the collection to the resource.
* [infra_ansible_support.yml](/ansible-playbooks/infra-ansible-support.md) - Installs the packages Ansible needs on managed hosts, points CentOS 7 at the vault repositories, and removes unattended-upgrades from Ubuntu.
* [infra_connectivity.yml](/ansible-playbooks/infra-connectivity.md) - Installs or removes maintainer SSH public keys in the connecting user's authorized_keys on managed hosts.
* [infra_fail2ban.yml](/ansible-playbooks/infra-fail2ban.md) - On CentOS hosts running fail2ban, whitelists the vault.centos.org address range in jail.conf.
* [infra_mail.yml](/ansible-playbooks/infra-mail.md) - Installs sendmail on managed hosts for alert mail and, for hosts inventoried by IP address, configures sendmail masquerading as the infra domain.
* [infra_network.yml](/ansible-playbooks/infra-network.md) - Tunes networking — MTU and transmit queue length on physical hosts' default interface and net.* sysctl settings on all managed hosts.
* [infra_ping.yml](/ansible-playbooks/infra-ping.md) - Checks Ansible connectivity to every managed host by gathering facts.
* [infra_reboot.yml](/ansible-playbooks/infra-reboot.md) - Reboots managed hosts whose infra_rebootable setting allows it.
* [infra_rng_tools.yml](/ansible-playbooks/infra-rng-tools.md) - Installs rng-tools on managed hosts so Ansible tasks have enough entropy for random number generation.
* [infra_selinux.yml](/ansible-playbooks/infra-selinux.md) - Disables SELinux on managed hosts where it is enabled.
* [infra_system_packages.yml](/ansible-playbooks/infra-system-packages.md) - Upgrades all system packages on managed hosts and optionally reboots hosts whose packages changed.
* [infra_timezone.yml](/ansible-playbooks/infra-timezone.md) - Sets managed hosts' timezone to America/Phoenix and restarts cron.
* [irods_catalog_provider.yml](/ansible-playbooks/irods-catalog-provider.md) - Fully deploys iRODS catalog service providers — provisioning, PostgreSQL client and ODBC setup, initial iRODS setup through the irods_cfg role, start, clerver authentication, and run-time initialization.
* [irods_cfg.yml](/ansible-playbooks/irods-cfg.md) - Re-deploys iRODS configuration, rule files, and command scripts to already set up catalog providers and resource servers through the irods_cfg role, and removes retired files.
* [irods_check_routes.yml](/ansible-playbooks/irods-check-routes.md) - Verifies network reachability of the iRODS zone, control plane, and ephemeral ports between catalog providers and resource servers, stopping iRODS during the check and restarting it afterward.
* [irods_free_space.yml](/ansible-playbooks/irods-free-space.md) - Updates each storage resource's free_space value in the iRODS catalog to match the space actually available on its vault file system.
* [irods_hosts.yml](/ansible-playbooks/irods-hosts.md) - Maintains a managed block in /etc/hosts on iRODS hosts that resolves the DBMS, catalog providers, resource servers, federated providers, AMQP broker, and other listed names.
* [irods_log.yml](/ansible-playbooks/irods-log.md) - Installs rsyslog on iRODS hosts, routes iRODS server, delay server, and agent messages to /var/log/irods/irods.log, and configures weekly log rotation.
* [irods_provision.yml](/ansible-playbooks/irods-provision.md) - Installs the iRODS server packages pinned to the configured version on native CentOS and Ubuntu iRODS hosts, creates the service account, and refreshes /etc/hosts.
* [irods_resource_container.yml](/ansible-playbooks/irods-resource-container.md) - Deploys containerized iRODS resource servers on AlmaLinux and Ubuntu hosts — installs Docker, generates the iRODS configuration with irods_cfg, and builds and runs an iRODS 4.3.1 resource server image with docker compose.
* [irods_resource_hierarchies.yml](/ansible-playbooks/irods-resource-hierarchies.md) - Creates the coordinating resource hierarchies listed in irods_resource_hierarchies using the irods_resource_hierarchy module.
* [irods_resource_server.yml](/ansible-playbooks/irods-resource-server.md) - Deploys native (non-containerized) iRODS resource servers — provisioning, clerver user creation on the catalog, initial iRODS setup as a catalog consumer, start, and storage resource creation.
* [irods_restart_all.yml](/ansible-playbooks/irods-restart-all.md) - Restarts iRODS on every iRODS host in dependency order — stopping consumers, restarting catalog providers, then starting consumers.
* [irods_restart_rs.yml](/ansible-playbooks/irods-restart-rs.md) - Restarts iRODS on resource servers that aren't catalog providers, leaving catalog providers running.
* [irods_runtime_init.yml](/ansible-playbooks/irods-runtime-init.md) - Performs one-time run-time initialization of an iRODS zone — rodsadmin group, standard collections and UUIDs, anonymous access, housekeeping rule scheduling, and conversion of ds-service users to rodsuser.
* [irods_s3_cred.yml](/ansible-playbooks/irods-s3-cred.md) - Deploys the S3 credential files iRODS uses to reach S3 buckets into /etc/irods/s3-credentials and removes credential files that are no longer listed.
* [irods_specific_queries.yml](/ansible-playbooks/irods-specific-queries.md) - Registers the SQL files in files/irods/specific-queries/ as iRODS specific queries, using each file name as the query alias.
* [irods_stop_all.yml](/ansible-playbooks/irods-stop-all.md) - Stops iRODS on all hosts that have the service account — resource servers first, then catalog providers — recording the result in stop_all_result for a parent playbook.
* [irods_storage_resources.yml](/ansible-playbooks/irods-storage-resources.md) - Creates vault directories and unixfilesystem storage resources for native resource servers, then initializes each resource's free space.
* [ncems_usage.yml](/ansible-playbooks/ncems-usage.md) - Creates the NCEMS project's resource hierarchy and project collection in iRODS and binds the collection to the resource with units required.
* [pire_usage.yml](/ansible-playbooks/pire-usage.md) - Creates the BH-PIRE/EHT resource hierarchy, the pire group, and the eht and bhpire shared collections in iRODS, binding the collections to the resource.
* [proxy_block.yml](/ansible-playbooks/proxy-block.md) - Drains and disables the SFTP, WebDAV, and iRODS backend servers in HAProxy, cutting off client access to the Data Store.
* [proxy_start.yml](/ansible-playbooks/proxy-start.md) - Starts the haproxy service on the proxy hosts and enables it at boot.
* [proxy_stop.yml](/ansible-playbooks/proxy-stop.md) - Stops the haproxy service on the proxy hosts and disables it at boot.
* [proxy_unblock.yml](/ansible-playbooks/proxy-unblock.md) - Re-enables the iRODS, WebDAV, and SFTP backend servers in HAProxy, restoring client access after proxy_block.yml.
* [proxy.yml](/ansible-playbooks/proxy.md) - Deploys HAProxy on the proxy hosts, fronting iRODS, SFTP, and WebDAV, using the haproxy role.
* [sftp_start.yml](/ansible-playbooks/sftp-start.md) - Starts the sftpgo service on the SFTP hosts and enables it at boot.
* [sftp_stop.yml](/ansible-playbooks/sftp-stop.md) - Stops the sftpgo service on the SFTP hosts and disables it at boot.
* [sftp.yml](/ansible-playbooks/sftp.md) - Installs and configures SFTPGo and the sftpgo-auth-irods plugin on the SFTP hosts, creates SFTPGo's iRODS proxy user, and wires an SFTPGo API key into the auth plugin.
* [webdav_start.yml](/ansible-playbooks/webdav-start.md) - Starts and enables varnish, varnishncsa, httpd, and purgeman on the WebDAV hosts.
* [webdav_stop.yml](/ansible-playbooks/webdav-stop.md) - Stops and disables purgeman, httpd, varnishncsa, and varnish on the WebDAV hosts.
* [webdav.yml](/ansible-playbooks/webdav.md) - Deploys the WebDAV service — Apache with davrods, a Varnish cache in front, purgeman for cache invalidation, static landing pages, and TLS — on the webdav hosts.
