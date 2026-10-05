# env

This folder contains the source for a set of Docker images that are intended to create a iRODS grid to be used for testing the ansible playbooks that configure an iRODS grid.

The environment consists of a set of containers. The `amqp` container hosts a RabbitMQ broker that in turn hosts the `irods` exchange, where the Data Store publishes messages to. The `dbms_configured` container hosts the PostgreSQL server that in turn hosts the ICAT DB. The iRODS servers all run on AlmaLinux 9. The `provider_configured` container hosts a configured iRODS catalog service provider. The `provider_unconfigured` container hosts an unconfigured service provider. The `consumer_configured_centos` container hosts a configured catalog service consumer acting as a resource server for `replRes` and `ingestRes`; it keeps its old name, though it no longer runs CentOS. The `consumer_unconfigured` container hosts an unconfigured service consumer. Finally, `consumer_containerized_alma` holds an unconfigured AlmaLinux 10 host, `consumer_containerized_alma9` an unconfigured AlmaLinux 9 host, and `consumer_containerized_ubuntu` an unconfigured Ubuntu 24.04 host.

The environment is controlled by docker-compose, but there are three programs that simplify the usage of docker-compose. `build` can be used to create all of the images. `clean` can be used to delete all of the images. Finally, `controller` can be used to bring up or tear down the grid. After its action, `controller` accepts compose files to apply over `docker-compose.yml`; pass the same files to `stop` as to `start`. Setting `IRODS_VERSION` builds and runs the configured catalog service provider on that iRODS release instead of 4.3.1. `build` also rebuilds the images of any other release already built, and `clean` deletes them.

The docker-compose file uses a set of environment variables. They can be passed to each of the `build`, `clean`, and `controller` programs in a file that exports them. Here's a complete example include file.

```bash
# The docker-compose project name.
export ENV_NAME=dstesting

# The name of the docker network.
export DOMAIN="$ENV_NAME"_default

# The DBMS user iRODS connects to the ICAT with. The same value has to reach
# both the DBMS and the catalog service provider images, or the provider
# authenticates as a role the DBMS never created.
export DB_USER=irodsuser

# The host name of the PostgreSQL server
export DBMS_HOST="$ENV_NAME"_dbms_configured_1."$DOMAIN"

# The end of the port range available for parallel transfer and reconnections.
# The beginning of the range is 20000.
export IRODS_LAST_EPHEMERAL_PORT=20009

# The name of the primary group the irods service account belongs to on the
# catalog service provider.
export IRODS_PROVIDER_SYSTEM_GROUP=irods_provider

# The absolute path to the vault of the second storage resource on the
# configured resource server
export IRODS_INGEST_VAULT=/var/lib/irods/ingest_vault

# The name of the default storage resource on the configured resource server
export IRODS_RES_CONF_CENTOS_NAME=replRes

# The name of the second storage resource on the configured resource server,
# which is the zone's default resource
export IRODS_RES_CONF_INGEST_NAME=ingestRes

# The URI for the schema used to validate the configuration files or 'off'
export IRODS_SCHEMA_VALIDATION=off

# The absolute path to the vault on the resource servers
export IRODS_VAULT=/var/lib/irods/Vault

# The name of the iRODS zone
export IRODS_ZONE_NAME=testing

# The host name of the configured catalog service consumer
export IRODS_CONSUMER_CONF_CENTOS_HOST="$ENV_NAME"_consumer_configured_centos_1."$DOMAIN"

# The name of the default resource to use
export IRODS_DEFAULT_RESOURCE="$IRODS_RES_CONF_INGEST_NAME"

# The host name of the configured catalog service provider
export IRODS_PROVIDER_CONF_HOST="$ENV_NAME"_provider_configured_1."$DOMAIN"

# The host name of the unconfigured service provider
export IRODS_PROVIDER_UNCONF_HOST="$ENV_NAME"_provider_unconfigured_1."$DOMAIN"
```
