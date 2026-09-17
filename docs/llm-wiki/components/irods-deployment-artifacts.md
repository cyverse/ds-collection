---
type: Component
title: iRODS Deployment Artifacts
description: The command scripts, rule files, and configuration values that make up an iRODS server deployment, and the variables and files that control each.
resource: /docs/deployment-artifacts/irods.md
tags: [irods, configuration, rules, command-scripts, server-config]
timestamp: 2026-09-17T00:00:00Z
---

This page lists the custom files and configuration values deployed to iRODS
servers. Values described as production settings come from the source
document; the production inventory isn't in this repo.

## Command scripts

Scripts in `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/`, executable
through the `msiExecCmd` microservice:

| Script | Purpose |
| --- | --- |
| `add-transfer` | Adds a transfer event to the ICAT's `r_transfer_totals` table |
| `amqp-topic-send` | Publishes audit messages to a RabbitMQ broker |
| `delete-scheduled-rule` | Removes a rule execution from the rule queue |
| `generate-uuid` | Generates a time-based UUID |
| `ichksum-exec`, `imeta-exec`, `iquest-exec`, `irepl-exec` | Call `ichksum`, `imeta`, `iquest`, and `irepl` |
| `send-mail` | Sends an email message |

## Rule files

Common rule bases implementing CyVerse-wide policy, in
`playbooks/files/irods/etc/irods/`:

- [cve](/irods-rules/cve.md) — workarounds for iRODS CVEs.
- [cyverse](/irods-rules/cyverse.md) — shared logic callable from other rule
  bases; its environment-dependent constants are in the
  `cyverse-env.re.j2` template.
- [cyverse_core](/irods-rules/cyverse-core.md) — a switchyard for PEPs that
  defers to other rule bases.
- [cyverse_encryption](/irods-rules/cyverse-encryption.md) — encryption
  enforcement.
- [cyverse_json](/irods-rules/cyverse-json.md) — JSON document creation.
- [cyverse_repl](/irods-rules/cyverse-repl.md) — resource residency and
  asynchronous replication.
- [cyverse_transfer_tracking](/irods-rules/cyverse-transfer-tracking.md) —
  user transfer tracking.
- [cyverse_trash](/irods-rules/cyverse-trash.md) — trash timestamp management.
- [cyverse_logic](/irods-rules/cyverse-logic.md) — policy not implemented in
  another rule base.
- [cyverse_housekeeping](/irods-rules/cyverse-housekeeping.md) — periodically
  run asynchronous tasks.

Project rule bases, each a static `.re` file plus an `*-env.re.j2` template
for environment-dependent constants in
`playbooks/templates/irods/etc/irods/`:
[AVRA](/irods-rules/avra.md), [BH-PIRE and EHT](/irods-rules/pire.md),
[ESIIL](/irods-rules/esiil.md), and [NCEMS](/irods-rules/ncems.md).
[CoGe](/irods-rules/coge.md) has a single rule base for the CoGe service.

## Configuration values

### DB connection

The production Data Store hosts the ICAT DB on PostgreSQL. iRODS
authenticates as `irodsuser` and connects through the CNAME
`icat.cyverse.org`, set in `plugin_configuration.database.postgres` of
`/etc/irods/server_config.json` on the catalog provider. The variables are
`irods_dbms_host`, `irods_dbms_port`, `irods_db_username`, and
`irods_db_password`. The source document instead names `irods_db_user` and
`irods_dbms_pg_hba`, neither of which exists in the collection. See
[ICAT DBMS](/components/icat-dbms.md).

### Rule bases

The custom rule bases `cve`, `cyverse_core`, and `cyverse_housekeeping` must
be listed, in that order and before `core`, in the rule engine's
`re_rulebase_set` in `server_config.json`. No variable controls this; the
playbooks pass them as the `irods_cfg` role's additional rule bases.

### Storage policy

Unless a project, service, or dataset has a special policy, data is stored
first at the University of Arizona and asynchronously replicated to TACC after
a brief delay (so temporary files can be deleted first), usually within a few
minutes. In production the default resource is `CyVerseRes`, a random
coordinating resource over several unixfilesystem resources, and the
replication resource is `taccRes`. This is enforced in three places:

1. `irods_default_resource` in `irods_environment.json`.
2. The `acSetRescSchemeForCreate` and `acSetRescSchemeForRepl` PEPs, which
   set `CyVerseRes` and `taccRes`. The source document places them in
   `/etc/irods/core.re`; in the repo,
   [cyverse_core](/irods-rules/cyverse-core.md) defines them and routes them
   to [cyverse_repl](/irods-rules/cyverse-repl.md). The containerized
   resource server's templated `core.re` also defines them.
3. `cyverse_DEFAULT_RESC` and `cyverse_DEFAULT_REPL_RESC` in
   `cyverse-env.re`.

The variables are `irods_default_resource` and `irods_default_repl_resource`.

### Vault

Each resource server attaches a unixfilesystem resource's vault at
`/irods_vault/<hostname>` (the short host name), where `/irods_vault` is
usually the XFS filesystem holding replicas. Older resource servers may
differ. The variable is `irods_default_vault`.

### Host entries

`hosts_entries` in `server_config.json` lists every FQDN and CNAME for the
local host; for the production catalog provider this includes
`data.cyverse.org`, the proxy's CNAME. The variable is `irods_host_aliases`.

### Zone

Production uses the zone `iplant`, set in `server_config.json`,
`irods_environment.json`, and `cyverse_ZONE` in `cyverse-env.re`. The variable
is `irods_zone_name`.

### Ephemeral ports

To support many iRODS connections, production uses the server port range
20000–20399 in `server_config.json`, controlled by
`irods_server_port_range_start` and `irods_server_port_range_end` (collection
defaults 20000 and 20199).

### Encryption policy

Because of iRODS bugs, server-to-server and client-to-server communication
isn't encrypted. This is configured by the `cyverse_logic_acPreConnect` rule
and by `client_server_policy` `CS_NEG_REFUSE` in `irods_environment.json`.

### Transfer threads

Following RENCI's recommendation, the default number of transfer threads is 3
in `server_config.json` and `irods_environment.json`, controlled by
`irods_default_number_of_transfer_threads`.

### Checksum policy

All replicas receive MD5 checksums, to support metadata requirements of some
publication repositories. `default_hash_scheme` in `server_config.json` and
`irods_default_hash_scheme` in `irods_environment.json` are `MD5`, and
[cyverse_logic](/irods-rules/cyverse-logic.md) ensures new data objects
receive a checksum. The source document also says `match_hash_policy` in
`server_config.json` and `irods_match_hash_policy` in `irods_environment.json`
are `strict`; the playbooks set neither, and the `irods_cfg` role's default
for both is `compatible`.

### Concurrent delay rule executors

CyVerse found 12 concurrent delay rule executors optimal in production. The
setting is `number_of_concurrent_delay_rule_executors` in the
`advanced_settings` object of `server_config.json`, controlled by
`irods_max_num_re_procs` (collection default 4). The source document names
`irods_default_number_of_transfer_threads` here, but the playbooks pass
`irods_max_num_re_procs` to the setting.

### Federation

Production is federated with the UAT zone `cyverse` on `data.cyverse.rocks`
and the TACC zone `corralZ` on `c3-dtn04.corral.tacc.utexas.edu`, configured in
the `federation` array of `server_config.json` by `irods_federation`.

### Event publishing

The Data Store publishes iRODS change events; see
[cyverse_logic](/irods-rules/cyverse-logic.md). The catalog provider's
`IRODS_AMQP_URI` environment variable references the RabbitMQ server that
hosts the exchange where events are published. It has the form
`amqp://<user>:<password>@<host>:<port>/<vhost>`. The source document says
every part is URL-encoded, but `irods_catalog_provider.yml` only replaces `/`
in the vhost with `%2F`. The exchange name reaches the rules as
`cyverse_AMQP_EXCHANGE` in `cyverse-env.re`. The variables are
`irods_amqp_host`, `irods_amqp_port`, `irods_amqp_vhost`,
`irods_amqp_username`, `irods_amqp_password`, and `irods_amqp_exchange`; the
source document's `irods_amqp_user` doesn't exist. See
[AMQP Broker](/components/amqp-broker.md).

# Citations

[1] `docs/deployment-artifacts/irods.md` — the source document.
[2] `playbooks/files/irods/var/lib/irods/msiExecCmd_bin/` — command scripts.
[3] `playbooks/files/irods/etc/irods/` — static rule files.
[4] `playbooks/templates/irods/etc/irods/` — environment-dependent rule templates.
[5] `playbooks/irods_catalog_provider.yml` — rule base list and AMQP URI construction.
[6] `playbooks/group_vars/all/irods.yml` — variable names and collection defaults.
[7] `roles/irods_cfg/vars/server_config.yml`, `roles/irods_cfg/defaults/main.yml`, `roles/irods_cfg/templates/macros.j2` — `match_hash_policy` and delay rule executor settings.
[8] `playbooks/templates/irods/docker-rs/run/etc/irods/core.re.j2` — containerized resource server `core.re`.
