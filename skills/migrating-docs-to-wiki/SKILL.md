---
name: migrating-docs-to-wiki
description: Use when converting an existing repo doc (docs/, playbooks/README.md, roles/*/README.md, testing/**/README.md) into an OKF wiki concept page — choosing section and type, adding frontmatter, wiring citations, and updating log and indexes; e.g. "move the limiting-concurrency doc into the wiki".
---

# Migrating Docs to the Wiki

## Overview

Existing prose docs can be converted into concept pages under
`docs/llm-wiki/`. Candidates in this repo:

- `docs/*.md` and `docs/deployment-artifacts/irods.md`
- `playbooks/README.md` (playbook list, tags, and variables)
- `roles/*/README.md`
- `testing/README.md`, `testing/env/README.md`, `testing/ansible-tester/README.md`

Migration is **copy, not move**: the original stays in place and the wiki
page's `resource` field points back at it as the canonical source.

## When to Use

- Converting an existing repo doc into the wiki, wholesale or condensed.
- NOT for writing a brand-new page from scratch — see `writing-wiki-pages`.
- Never migrate a table of contents or boilerplate: `docs/README.md` (an
  outline of TODOs), `docs/deployment-artifacts/README.md` (a pointer to
  `irods.md`), or `plugins/README.md` (Ansible collection template text).
  `index.md` is also a reserved OKF filename.

**REQUIRED SUB-SKILL:** `writing-wiki-pages` for the frontmatter, section and
type vocabulary, and link rules; `validating-the-wiki` before calling the
migration done.

## Migration Procedure

1. Choose the target section and `type` (see the table in
   `writing-wiki-pages`), and a lowercase-kebab filename. A role README becomes
   a `Role` page in `ansible-roles/`; a harness README becomes a `Runbook` in
   `runbooks/`.
2. Copy the doc body. Drop the doc's `# ` title line — the wiki page's title
   lives in frontmatter. Long docs may be condensed; short docs copy verbatim.
   Large variable tables (e.g. in `playbooks/README.md` or
   `roles/irods_cfg/README.md`) can be summarized with a pointer to the
   original rather than duplicated.
3. Add frontmatter with `resource` set to the original's repo-root path (e.g.
   `/docs/limiting-concurrency.md`).
4. Rewrite links: doc-to-doc links that now have wiki counterparts become
   bundle-absolute wiki links; links to repo files with no wiki page become
   plain code-span paths (a markdown link gets flagged — OKF108 if it climbs
   out of the bundle relatively, OKF101 dead link if written bundle-absolute).
5. Add a `# Citations` section naming the source doc and the main playbooks,
   roles, plugins, or rule files it describes.
6. Leave the original file unmodified.
7. Add a `## YYYY-MM-DD` entry to `docs/llm-wiki/log.md` (newest-first) noting
   the migration.
8. Run `okf index` and `okf check` per `validating-the-wiki`; finish at 0
   errors, 0 warnings.

## Common Mistakes

- **Deleting or gutting the original.** The original remains the authoritative
  `resource` until a deliberate decision retires it. Role READMEs in particular
  ship with the collection.
- **Leaving relative links pointing at the old location.** A link like
  `[irods](irods.md)` copied from `docs/deployment-artifacts/README.md` now
  resolves inside the wiki. Rewrite it: wiki link if a counterpart page exists,
  plain code-span path otherwise.
- **Migrating listings.** TOC files aren't concepts; their role is played by
  the generated wiki indexes.
- **Skipping the log entry and re-index.** A migration adds a page, so
  `docs/llm-wiki/log.md` gets an entry and `okf index` must run.
