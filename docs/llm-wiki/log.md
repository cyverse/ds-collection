# Wiki Update Log

## 2026-09-17

* **Update**: Checked the pages' statements about iRODS itself against the
  iRODS 4.3.1 documentation (https://docs.irods.org/4.3.1/) and, where the docs
  are silent, the `irods/irods` source at tag 4.3.1. Corrections:
  * [cve.re](/irods-rules/cve.md),
    [cyverse_encryption.re](/irods-rules/cyverse-encryption.md), and
    [cyverse_logic.re](/irods-rules/cyverse-logic.md): a `failmsg` after `cut`
    makes the operation fail with `CUT_ACTION_PROCESSED_ERR` (-1089000), not
    the code passed to `failmsg`.
  * [iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md):
    the local host's aliases belong in `host_resolution.host_entries`, and the
    environment key is `irods_client_server_policy`.
  * [Installing the Audit Plugin](/runbooks/installing-the-audit-plugin.md):
    the 4.3.1 package is `irods-rule-engine-plugin-audit-amqp`. This is added
    as a note; the migrated command is unchanged.
  * [irods_restart_all.yml](/ansible-playbooks/irods-restart-all.md): 4.3.1's
    `irodsctl status` prints `No iRODS servers running.`, so the shared running
    check never detects a stopped server.
  * [irods_user Module](/ansible-plugins/irods-user.md): 4.3.1 reports a
    mismatched password as `CAT_INVALID_AUTHENTICATION`, which the module
    doesn't catch, so it can set a password only for a user who has none.

* **Update**: Recorded three latent issues found during the review:
  * [cyverse_logic.re](/irods-rules/cyverse-logic.md): the read-only branch of
    `cyverse_logic_api_replica_close_post` passes unbound variables to
    `_cyverse_logic_ensureUUID`.
  * [avra.re](/irods-rules/avra.md), [esiil.re](/irods-rules/esiil.md),
    [ncems.re](/irods-rules/ncems.md), and [pire.re](/irods-rules/pire.md):
    each test's "equal to the default resource" `setUp` runs `sed` with no file
    argument.
  * [cve.re](/irods-rules/cve.md): `test_cyversecore_called` only exercises a
    PEP that the mock defines and the deployed rule files have commented out.

* **Update**: Reviewed every page against its sources and corrected 40 of
  them. Notable corrections:
  * [irods_cfg Role](/ansible-roles/irods-cfg.md): a null `irods_cfg_re` still
    renders both rule engine plugins, with only the `core` rule base.
  * [irods_resource_container.yml](/ansible-playbooks/irods-resource-container.md):
    most of its test playbook is `TODO` placeholders.
  * [cve.re](/irods-rules/cve.md): the `iput -p` physical-path check is commented
    out for issue 8106 on every iRODS version.
  * [esiil.re](/irods-rules/esiil.md) and [ncems.re](/irods-rules/ncems.md): the
    template test does check their env templates.
  * Several rule pages overstated test coverage that is skipped or marked
    unimplemented.
  * [iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md) now
    flags each place where `docs/deployment-artifacts/irods.md` disagrees with
    the code, rather than silently correcting it.
  * [webdav.yml](/ansible-playbooks/webdav.md): its test never checks the Varnish
    version, because it passes `version:` where the shared task reads `ver`.

* **New**: Populated every section from the repo's own sources — 9
  [components](/components/index.md) pages including the
  [Data Store Overview](/components/data-store-overview.md), 6
  [runbooks](/runbooks/index.md), one
  [playbook](/ansible-playbooks/index.md) page for each of the 47 playbooks, 7
  [role](/ansible-roles/index.md) pages, 18 [plugin](/ansible-plugins/index.md)
  pages, and 15 [iRODS rule](/irods-rules/index.md) pages with their
  `*-env.re.j2` templates folded in.
* **Migration**: `docs/deployment-artifacts/irods.md` became
  [iRODS Deployment Artifacts](/components/irods-deployment-artifacts.md),
  `docs/install-audit.md` became
  [Installing the Audit Plugin](/runbooks/installing-the-audit-plugin.md),
  `docs/limiting-concurrency.md` became
  [Limiting Concurrent Connections per User](/runbooks/limiting-concurrency.md),
  and the three `testing/` READMEs were merged into
  [Testing Playbooks and Plugins](/runbooks/testing-playbooks-and-plugins.md).
  Role READMEs were condensed into their role pages. The originals are
  unchanged.
* **Note**: Where a README, doc comment, or rule-file header disagrees with the
  code it describes, the pages describe the code and call out the mismatch.
  Undocumented facts, such as how `playbooks/tests/rules/` is invoked, are
  stated as undocumented rather than guessed.

* **Initialization**: Created the bundle with empty `components/`, `runbooks/`,
  `ansible-playbooks/`, `ansible-roles/`, `ansible-plugins/`, and `irods-rules/`
  sections, plus [Maintaining This Wiki](/maintaining-the-wiki.md). The `okf`
  validator/indexer was copied to `tools/okf` from the cyverse-de/deployments
  repository, and the wiki skills were ported to `skills/`.
