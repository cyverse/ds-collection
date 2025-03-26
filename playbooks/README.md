# Data Store Deployment

<!-- TODO: introduce this file -->

## iRODS

Here are the files used to configure iRODS.

### Command Scripts

Here are the command scripts executable through the `msiExecCmd` microservice. Only the general purpose ones are here. The ones used by optional components of the Data Store are stored elsewhere.

* [amqp-topic-send](files/irods/var/lib/irods/msiExecCmd_bin/amqp-topic-send) publishes audit messages to a RabbitMQ broker.
* [correct-size](files/irods/var/lib/irods/msiExecCmd_bin/correct-size) fixes data object replica sizes as a workaround for <https://github.com/irods/irods/issues/5160>. _Once this issue is fixed, this should be removed._
* [delete-scheduled-rule](files/irods/var/lib/irods/msiExecCmd_bin/delete-scheduled-rule) removes a rule execution from the rule queue.
* [generate-uuid](files/irods/var/lib/irods/msiExecCmd_bin/generate-uuid) generates a time-based UUID.
* [imeta-exec](files/irods/var/lib/irods/msiExecCmd_bin/imeta-exec) calls imeta.
* [send-mail](files/irods/var/lib/irods/msiExecCmd_bin/send-mail) sends an email message.

### Rule Bases

Here are the iRODS rule files.

* [cyverse.re](files/irods/etc/irods/cyverse.re) hold shared logic callable from other rule bases.
* [cyverse-env.re](templates/irods/etc/irods/cyverse-env.re.j2) is for environment-dependent constants common to CyVerse as a whole.
* [cyverse_core.re](files/irods/etc/irods/cyverse_core.re) acts as a switchyard for PEPs, deferring to other rule bases for actual implementations.
* [ipc-encryption.re](files/irods/etc/irods/ipc-encryption.re) has the encryption enforcement logic.
* [cyverse_json.re](files/irods/etc/irods/cyverse_json.re) provides the logic for creating JSON documents.
* [ipc-repl.re](files/irods/etc/irods/ipc-repl.re) has the resource determination and asynchronous replication logic.
* [ipc-trash.re](files/irods/etc/irods/ipc-trash.re) has the trash timestamp management logic.
* [cyverse_logic.re](files/irods/etc/irods/cyverse_logic.re) has the CyVerse policy logic not implemented in another rule base.
* [cyverse_housekeeping.re](files/irods/etc/irods/cyverse_housekeeping.re) provides the logic for the periodically run asynchronous tasks.
* [cve.re](files/irods/etc/irods/cve.re) are workarounds for iRODS CVEs.
* [avra.re](files/irods/etc/irods/avra.re) is for the AVRA project.
* [avra-env.re](templates/irods/etc/irods/avra-env.re.j2) is environment dependent AVRA constants.
* [coge.re](files/irods/etc/irods/coge.re) is for the CoGe service.
* [mdrepo.re](files/irods/etc/irods/mdrepo.re) is for the MD-Repo service.
* [mdrepo-env.re](templates/irods/etc/irods/mdrepo-env.re.j2) is for environment dependent MD-Repo constants.
* [pire.re](files/irods/etc/irods/pire.re) is for the BH-PIRE and EHT projects.
* [pire-env.re](templates/irods/etc/irods/pire-env.re.j2) is for the environment dependent constants for the BH-PIRE and EHT projects.
