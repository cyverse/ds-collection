# iRODS Deployment Artifacts

Here are the files used to configure iRODS.

## Command Scripts

Here are the command scripts executable through the `msiExecCmd` microservice. Only the general purpose ones are here. The ones used by optional components of the Data Store are stored elsewhere.

### Common Command Scripts

The following command scripts are used to implement policy common to all of CyVerse.

* [amqp-topic-send](../../playbooks/files/irods/var/lib/irods/msiExecCmd_bin/amqp-topic-send) publishes audit messages to a RabbitMQ broker.
* [delete-scheduled-rule](../../playbooks/files/irods/var/lib/irods/msiExecCmd_bin/delete-scheduled-rule) removes a rule execution from the rule queue.
* [generate-uuid](../../playbooks/files/irods/var/lib/irods/msiExecCmd_bin/generate-uuid) generates a time-based UUID.
* [imeta-exec](../../playbooks/files/irods/var/lib/irods/msiExecCmd_bin/imeta-exec) calls imeta.
* [send-mail](../../playbooks/files/irods/var/lib/irods/msiExecCmd_bin/send-mail) sends an email message.

### MD-Repo Command Script

The command script [md-repo-touch-obj](../../playbooks/files/irods/mdrepo/var/lib/irods/msiExecCmd_bin/md-repo-touch-obj) is used to ensure that a data object being uploaded exists in the ICAT before it is uploaded by ticket.

## Rule Files

Here are the iRODS rule files.

### Common Rule Files

The following rules bases implement CyVerse-wide Data Store policy.

The following files contain the policy that is independent of deployment environment.

* [cyverse.re](../../playbooks/files/irods/etc/irods/cyverse.re) hold shared logic callable from other rule bases.
* [cyverse_core.re](../../playbooks/files/irods/etc/irods/cyverse_core.re) acts as a switchyard for PEPs, deferring to other rule bases for actual implementations.
* [cyverse_json.re](../../playbooks/files/irods/etc/irods/cyverse_json.re) provides the logic for creating JSON documents.
* [cve.re](../../playbooks/files/irods/etc/irods/cve.re) are workarounds for iRODS CVEs.
* [ipc-encryption.re](../../playbooks/files/irods/etc/irods/ipc-encryption.re) has the encryption enforcement logic.
* [ipc-repl.re](../../playbooks/files/irods/etc/irods/ipc-repl.re) has the resource residency and asynchronous replication logic.
* [ipc-trash.re](../../playbooks/files/irods/etc/irods/ipc-trash.re) has the trash timestamp management logic.
* [cyverse_logic.re](../../playbooks/files/irods/etc/irods/cyverse_logic.re) has the CyVerse policy logic not implemented in another rule base.
* [cyverse_housekeeping.re](../../playbooks/files/irods/etc/irods/cyverse_housekeeping.re) provides the logic for the periodically run asynchronous tasks.

The template [cyverse-env.re](../../playbooks/templates/irods/etc/irods/cyverse-env.re.j2) is for environment-dependent constants.

### AVRA Rule Files

Two rule bases implement the AVRA project's Data Store policy. The file [avra.re](../../playbooks/files/irods/etc/irods/avra.re) contains the AVRA policy that is independent of the deployment environment. The template [avra-env.re](../../playbooks/templates/irods/etc/irods/avra-env.re.j2) contains the environment-dependent AVRA constants.

### BH-PIRE and EHT Rule Files

Two rule bases implement the BH-PIRE and EHT projects' Data Store policy. The file [pire.re](../../playbooks/files/irods/etc/irods/pire.re) contains the BH-PIRE and EHT policy independent of the deployment environment. The template [pire-env.re](../../playbooks/templates/irods/etc/irods/pire-env.re.j2) contains the environment dependent BH-PIRE and EHT constants.

### CoGe Rule File

The rule base [coge.re](../../playbooks/files/irods/etc/irods/coge.re) is for the CoGe service.

### MD-Repo Rule Files

Two rule bases implement the MD Repo project's Data Store policy. The file [mdrepo.re](../../playbooks/files/irods/etc/irods/mdrepo.re) contains the policy that is independent of the deployment environment. The template [mdrepo-env.re](../../playbooks/templates/irods/etc/irods/mdrepo-env.re.j2) contains the environment-dependent MD Repo constants.

## Configuration Values

This section describes the locations where specific configuration values are set.

### DB Connection Configuration

The production Data Store uses PostgreSQL to host the ICAT DB. iRODS uses the account `irodsuser` to authenticate with PostgreSQL. It uses the CNAME `icat.cyverse.org` to connect PostgreSQL. These are set in the `plugins_configuration.database.postgres` section of `/etc/irods/server_config.json` on the catalog provider.

The ansible variables `irods_db_password`, `irods_db_user`, `irods_dbms_host`, `irods_dbms_pg_hba`, and `irods_dbms_port` are used to control the configuration.

### Rule Bases

The Data Store uses three custom rule bases defined the in the files [`cve.re`](../../playbooks/files/irods/etc/irods/cve.re), [`cyverse_core.re`](../../playbooks/files/irods/etc/irods/cyverse_core.re), and [`cyverse_housekeeping.re`](../../playbooks/files/irods/etc/irods/cyverse_housekeeping.re). They need to be listed in `plugin_configuration.rule_engines]0].plugin_specific_configuration.re_rulebase_set` of `/etc/irods/server_config.json`. They need to be listed in that order and before `core.re`. For more information on the rule bases, see the section [Rule Files](#rule-files).

There is no ansible variable that controls this. The playbooks will ensure that the rule bases are configured correctly.

### Storage Policy

Unless there is a special policy configured for a given project, service, or dataset, all data will be stored first at the University of Arizona, and then asynchronously replicated to TACC. There is a brief delay before being replicated to let temporary files being deleted before wasting time replicating these files. The replication will almost always happen within a few minutes of being uploaded. The default resource used for storing data at the U of A is `CyVerseRes`. This is a random coordinating resource composed of several unix filesystem storage resources. The resource used for storing data at TACC is `taccRes`.

This policy is enforced in three places.

1. Set `irods_default_resource` to `CyVerseRes` in `/var/lib/irods/.irods/irods_environment.json`.
2. Use `acSetRescSchemeForCreate` to set `CyVerseRes` and `acSetRescSchemeForRepl` to set `taccRes` in `/etc/irods/core.re`.
3. Set `cyverse_DEFAULT_RESC` to `CyVerseRes` and `cyverse_DEFAULT_REPL_RESC` to `taccRes` in `/etc/irods/cyverse-env.re`.

The ansible variables `irods_default_resource` and `irods_default_repl_resource` are used to set these values.

### Vault

Each resource server that hosts a unixfilesystem resource, attaches the resource's vault at `/irods_vault/<hostname>`, where _\<hostname\>_ is hostname of the resource server without the domain name. `/irods_vault` is usually where the XFS filesystem used to store the replicas is mounted. Historically, we didn't have a policy, so older resource servers may be configured differently.

The ansible variable `irods_default_vault` is used to set this value.

### Host Entries

The production zone the `hosts_entries` field is set in `/etc/irods/server_config.json`. It includes all of the FQDN and CNAMEs for the local host. For the catalog provider, this includes `data.cyverse.org`, the CNAME for the proxy.

The ansible variable `irods_host_aliases` is used to set this value.

### Zone

For historical reasons, CyVerse uses the zone `iplant`. This is configured in `/etc/irods/server_config.json` and `/var/lib/irods/.irods/irods_environment.json`. It is also set in the rule file `/etc/irods/cyverse-env.re` in the constant `cyverse_ZONE`.

The ansible variable `irods_zone_name` is used to define the zone name.

### Ephemeral Ports

To support a large number of iRODS connections, we use the server port range 20000 - 20399. The range is configured in `/etc/irods/server_config.json`.

The ansible variables `irods_server_port_range_start` and `irods_server_port_range_end` are used to define this range.

### Encryption Policy

Because of bugs in iRODS, communication between iRODS servers and between servers and clients is not encrypted. This is configured using the rule `cyverse_logic_acPreConnect` defined in `/etc/irods/cyverse_logic.re` and by setting `client_server_policy` to `CS_NEG_REFUSE` in `/var/lib/irods/.irods/irods_environment.json`.

### Default Number of Transfer Threads

Following RENCI's recommendation, the default number of transfer threads is set to 3 in `/etc/irods/server_config.json` and `/var/lib/irods/.irods/irods_environment.json`.

The ansible variable `irods_default_number_of_transfer_threads` is used to set this value.

### Checksum Policy

All data object replicas receive MD5 checksums. To support metadata requirements for certain data publication repositories, we use the MD5 hash scheme for checksums. This is enforced in a few places.

1. In `/etc/irods/server_config.json`, `default_hash_scheme` is set to `MD5`, and `match_hash_policy` is set to `strict`.
2. In `/var/lib/irods/.irods/irods_environment.json`, `irods_default_hash_scheme` is set to `MD5`, and `irods_match_hash_policy` is set to `strict`.
3. Custom iRODS rule logic defined in `/etc/irods/cyverse_logic.re` ensures that every newly created data object receives a checksum.

### Maximum Number of Concurrent Delay Rule Executors

Through trial and error, CyVerse found that setting the maximum number of concurrent delay rule executors to 12 is optimal. This is configured in the `advanced_settings` object in the `/etc/irods/server_config.json`.

The ansible variable `irods_default_number_of_transfer_threads` is used to set this value.

### Federation

The production zone is federated with the two zones. It is federated with UAT zone `cyverse` hosted on `data.cyverse.rocks`. It is also federated with the TACC zone `corralZ` hosted on `c3-dtn04.corral.tacc.utexas.edu`. Ths is configured in the `federation` array of `/etc/irods/server_config.json`.

The ansible variable `irods_federation` controls this configuration.

### Event Publishing

CyVerse Data Store publishes iRODS changes events. See the [cyverse_logic.re](../../playbooks/files/irods/etc/irods/cyverse_logic.re) rule file for more information on the published events. We set the environment variable `IRODS_AMQP_URI` on the catalog provider to the reference the RabbitMQ server that hosts the `irods` exchange where events are published. It has the form `amqp://{{ RabbitMQ username }}:{{ password }}@{{ RabbitMQ host }}:{{ port }}/{{ vhost }}`, where everything is properly URL encoded.

The ansible variables `irods_amqp_exchange`, `irods_amqp_host`, `irods_amqp_password`, `irods_amqp_port`, `irods_amqp_user`, and `irods_amqp_vhost` control this configuration.
