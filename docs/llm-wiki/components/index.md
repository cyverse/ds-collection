# components

* [AMQP Broker](/components/amqp-broker.md) - The RabbitMQ broker in the amqp group that hosts the topic exchange iRODS publishes Data Store events to.
* [Data Store Overview](/components/data-store-overview.md) - The Data Store's architecture as expressed by the collection's inventory groups, and which playbooks target each group.
* [HAProxy Proxy](/components/haproxy-proxy.md) - The HAProxy hosts in the proxy group that front iRODS, SFTP, and WebDAV, with per-client connection throttling and allow/block/VIP lists.
* [ICAT DBMS](/components/icat-dbms.md) - The PostgreSQL 12 primary and streaming replicas that host the iRODS ICAT database, including the custom r_transfer_totals table.
* [iRODS Catalog Service Provider](/components/irods-catalog-provider.md) - The iRODS servers in the irods_catalog group that own the ICAT connection, run the rule engine and periodic policies, and publish events to AMQP.
* [iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md) - The command scripts, rule files, and configuration values that make up an iRODS server deployment, and the variables and files that control each.
* [iRODS Resource Server](/components/irods-resource-server.md) - Catalog service consumers that host storage vaults, deployed either natively from OS packages or as a Docker Compose container.
* [SFTP](/components/sftp.md) - The SFTPGo service in the sftp group that serves SFTP access to the Data Store, authenticating users against iRODS with the sftpgo-auth-irods hook.
* [WebDAV](/components/webdav.md) - The webdav group's Apache httpd with davrods, fronted by a Varnish cache that purgeman invalidates from iRODS AMQP events.
