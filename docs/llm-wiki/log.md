# Wiki Update Log

## 2026-09-17

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
