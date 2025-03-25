# iRODS configuration files

Here are the files used to configure iRODS. These are independent of environment.

## Command Scripts

Here are the command scripts executable through the `msiExecCmd` microservice. Only the general purpose ones are here. The ones used by optional components of the Data Store are stored elsewhere.

* [amqp-topic-send](var/lib/irods/msiExecCmd_bin/amqp-topic-send) publishes audit messages to a RabbitMQ broker.
* [correct-size](var/lib/irods/msiExecCmd_bin/correct-size) fixes data object replica sizes as a workaround for <https://github.com/irods/irods/issues/5160>. _Once this issue is fixed, this should be removed._
* [delete-scheduled-rule](var/lib/irods/msiExecCmd_bin/delete-scheduled-rule) removes a rule execution from the rule queue.
* [generate-uuid](var/lib/irods/msiExecCmd_bin/generate-uuid) generates a time-based UUID.
* [imeta-exec](var/lib/irods/msiExecCmd_bin/imeta-exec) calls imeta.
* [send-mail](var/lib/irods/msiExecCmd_bin/send-mail) sends an email message.

## Rule Bases

Here are the iRODS rule files.

* [cyverse.re](etc/irods/cyverse.re) hold shared logic callable from other rule bases.
* [cyverse_core.re](etc/irods/cyverse_core.re) acts as a switchyard for PEPs, deferring to other rule bases for actual implementations.
* [ipc-encryption.re](etc/irods/ipc-encryption.re) has the encryption enforcement logic.
* [cyverse_json.re](etc/irods/cyverse_json.re) provides the logic for creating JSON documents.
* [ipc-repl.re](etc/irods/ipc-repl.re) has the resource determination and asynchronous replication logic.
* [ipc-trash.re](etc/irods/ipc-trash.re) has the trash timestamp management logic.
* [cyverse_logic.re](etc/irods/cyverse_logic.re) has the CyVerse policy logic not implemented in another rule base.
* [cyverse_housekeeping.re](etc/irods/cyverse_housekeeping.re) provides the logic for the periodically run asynchronous tasks.
* [cve.re](etc/irods/cve.re) are workarounds for iRODS CVEs.
* [avra.re](etc/irods/avra.re) is for the AVRA project.
* [coge.re](etc/irods/coge.re) is for the CoGe service.
* [mdrepo.re](etc/irods/mdrepo.re) is for the MD-Repo service.
* [pire.re](etc/irods/pire.re) is for the BH-PIRE and EHT projects.
