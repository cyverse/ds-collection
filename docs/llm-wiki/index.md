---
okf_version: "0.1"
---

# CyVerse Data Store Collection Wiki

Curated knowledge about the `cyverse.ds` Ansible collection, which deploys and
maintains the CyVerse Data Store, in
[Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) v0.1.
Start here and descend through the section indexes. Each concept page's
`resource` field and Citations point back at the authoritative files in the
repo; validate and re-index with `tools/okf` (see the `validating-the-wiki`
skill).

# Sections

* [components/](/components/index.md) - Data Store subsystems: iRODS catalog providers and resource servers, the ICAT DBMS, AMQP, HAProxy, SFTP, and WebDAV.
* [runbooks/](/runbooks/index.md) - Procedures an operator or developer follows, spanning several playbooks or the testing harness.
* [ansible-playbooks/](/ansible-playbooks/index.md) - Individual playbooks under playbooks/.
* [ansible-roles/](/ansible-roles/index.md) - Roles under roles/ and their molecule scenarios.
* [ansible-plugins/](/ansible-plugins/index.md) - Custom modules, lookups, and tests under plugins/.
* [irods-rules/](/irods-rules/index.md) - iRODS rule files deployed to the Data Store and their tests.

# Meta

* [Maintaining This Wiki](/maintaining-the-wiki.md) - How to add, edit, migrate, and validate wiki pages.
