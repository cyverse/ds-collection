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

## Rule Bases

Here are the iRODS rule files.

### Common Rule Bases

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

### AVRA Rule Bases

Two rule bases implement the AVRA project's Data Store policy. The file [avra.re](../../playbooks/files/irods/etc/irods/avra.re) contains the AVRA policy that is independent of the deployment environment. The template [avra-env.re](../../playbooks/templates/irods/etc/irods/avra-env.re.j2) contains the environment-dependent AVRA constants.

### BH-PIRE and EHT Rule Bases

Two rule bases implement the BH-PIRE and EHT projects' Data Store policy. The file [pire.re](../../playbooks/files/irods/etc/irods/pire.re) contains the BH-PIRE and EHT policy independent of the deployment environment. The template [pire-env.re](../../playbooks/templates/irods/etc/irods/pire-env.re.j2) contains the environment dependent BH-PIRE and EHT constants.

### CoGe Rule Base

The rule base [coge.re](../../playbooks/files/irods/etc/irods/coge.re) is for the CoGe service.

### MD-Repo Rule Bases

Two rule bases implement the MD Repo project's Data Store policy. The file [mdrepo.re](../../playbooks/files/irods/etc/irods/mdrepo.re) contains the policy that is independent of the deployment environment. The template [mdrepo-env.re](../../playbooks/templates/irods/etc/irods/mdrepo-env.re.j2) contains the environment-dependent MD Repo constants.
