# PostgreSQL Configuration

This page describes the custom configuration made to the production ICAT DBMS.

## Huge Pages

PostgreSQL requires transparent huge pages to be disabled for optimal performance. This is done by adding `transparent_hugepage=never` on the GRUB command line. PostgreSQL benefits from normal huge pages. The number of huge pages is set to 140,000 using the `vm.nr_huge_pages` using sysctl. The value can be controlled us in the ansible variable `dbms_mem_num_huge_pages`.

## /etc/postgresql/12/main/conf.d/cyverse.conf

Here is the custom configuration made to the PostgreSQL instances hosting the ICAT DB. The customizations are made in the file `/etc/postgresql/12/main/conf.d/cyverse.conf`.

### Concurrency

Following the recommendations were made by PGTune, the following concurrency configuration values have been set.

* `effective_io_concurrency`, the number of concurrent disk operations, is set to `200`. This can be controlled by the ansible variable `dbms_effective_io_concurrency`.
* `max_worker_processes`, the maximum number of background worker processes, is set to the number of cores on the hosting server. This can be controlled by the ansible variable `dbms_max_worker_processes`.
* `max_parallel_maintenance_workers`, The maximum number of background worker processes allowed for a single utility operation, is set to `4`. This can be controlled by the ansible variable `dbms_max_parallel_maintenance_workers`.
* `max_parallel_workers_per_gather`, the maximum number of background worker processes allowed for single parallel operation, is set to `4`. This can be controlled by the ansible variable `dbms_max_parallel_workers_per_gather`.

### Logging

Only two customizations are made to the logging configuration. To avoid overwhelming the PostgreSQL log, only queries that take longer than 1s are logged. This can be controlled by the ansible variable `dbms_log_min_duration`. A custom log line prefix is used that has the form `< YYYY-MM-DD hh:mm:ss.sss "MST" CLIENT_IP(PORT) >`. This can be controlled by the ansible variable `dbms_log_line_prefix`.

### Memory

Following best practices the following settings are applied.

* The effective cache size is set to 50% of total memory. This can be controlled by the ansible variable `dbms_effective_cache_size`.
* The shared buffer size is set to 25% of total memory.
* To speed up administrative operations, the working memory for maintenance has been maximized (set to 2 GiB). This can be controlled by the ansible variable `dbms_maintenance_work_mem`.
* The working memory is set to 179 MB. This can be controlled by the ansible variable `dbms_work_mem`.
* PostgreSQL is configured to use huge pages unless the ansible variable `dbms_mem_num_huge_pages` is set to 0.

### Network

The following network-related configuration has been made.

* PostgreSQL is configured to listen on all host IP addresses.
* To support the level CyVerse sees for concurrent user connections, the maximum number of connections is set to 600. This can be controlled by the ansible variable `dbms_max_connections`.

### Storage

Because CyVerse's production ICAT DBMS uses SSD for storage, the random page cost is set to `1.1`. This can be controlled by the ansible variable `dbms_random_page_cost`.

### Strings/Text

As required by iRODS, standard conforming strings is disabled.

### WAL

Following the recommendations made by PGTune, the following WAL configuration values have been set.

* `checkpoint_completion_target`, the checkpoint duration fraction, is set to `0.9`. This can be controlled by the ansible variable `dbms_checkpoint_completion_target`.
* `max_wal_size`, the maximum file size, is set to `4GB`. This can be controlled by the ansible variable `dbms_max_wal_size`.
* `min_wal_size`, the minimum file size, is set to `1GB`. This can be controlled by the ansible variable `dbms_min_wal_size`.
* `wal_buffers`, the amount of shared memory used for WAL, is set to `16MB`.

Following best practices, the `checkpoint_timeout` is set to `15min`. This can be controlled by the ansible variable `dbms_checkpoint_timeout`.

### Replication

The DBMS has a warm replica. Failover is performed manually following standard PostgreSQL failover procedures with one additional step. The DNS alias icat.cyverse.org needs to be pointed at the new primary DBMS host.

There are a few configuration values that can be controlled through ansible.

* The PostgreSQL user `replicator` manages replication between servers. This can be controlled by the ansible variables `dbms_replication_username` and `dbms_replication_password`.
* 4,000 WAL files are held by the primary for the replica. This can be controlled by the ansible variable `dbms_wal_keep_segments`.

## /etc/postgresql/12/main/pg_hba.conf

pg_hba.conf is modified to allow all members of the `irods_catalog` ansible group to access the ICAT database.

## ICAT DB

The ICAT database is owned by the PostgreSQL user `irodsuser`. This can be controlled by the ansible variable `dbms_irods_username`. The password can be controlled by the ansible variable `dbms_irods_password`.
