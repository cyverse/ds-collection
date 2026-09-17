# ansible-roles

* [firewalld Role](/ansible-roles/firewalld.md) - The cyverse.ds.firewalld role, which installs firewalld in place of ufw and manages a per-service maintenance, testing, or operation firewall configuration.
* [haproxy Role](/ansible-roles/haproxy.md) - The cyverse.ds.haproxy role, which installs HAProxy and renders its configuration for the iRODS, SFTP, WebDAV, and stats front ends, with connection tracking and allow, block, and VIP address lists.
* [irods_cfg Role](/ansible-roles/irods-cfg.md) - The cyverse.ds.irods_cfg role, which generates iRODS 4.3.1 configuration files (irods_environment.json, server_config.json, service_account.config), deploys rule bases and command scripts, and can initialize a new server with setup_irods.py.
* [postgresql_db Role](/ansible-roles/postgresql-db.md) - The cyverse.ds.postgresql_db role, which ensures a PostgreSQL database and its admin user exist and grants client hosts md5 access in pg_hba.conf.
* [postgresql Role](/ansible-roles/postgresql.md) - The cyverse.ds.postgresql role, which installs PostgreSQL from apt, applies CyVerse tuning through a conf.d file, and sets up streaming replication between a primary and its replicas.
* [rabbitmq_vhost Role](/ansible-roles/rabbitmq-vhost.md) - The cyverse.ds.rabbitmq_vhost role, which creates or removes a RabbitMQ vhost and manages its parameters, policies, user permissions, exchanges, queues, and bindings.
* [rabbitmq Role](/ansible-roles/rabbitmq.md) - The cyverse.ds.rabbitmq role, which installs pinned Erlang and RabbitMQ packages from Team RabbitMQ's apt repositories, enables the management plugin, and manages the broker admin user.
