---
name: writing-wiki-pages
description: Use when creating or editing a concept page in the OKF wiki at docs/llm-wiki/ — frontmatter shape, section and type vocabulary, link style, and log/index upkeep; e.g. "add a wiki page about the irods_cfg role" or "update the WebDAV wiki page".
---

# Writing Wiki Pages

## Overview

The repo has a curated knowledge wiki at `docs/llm-wiki/`, an
[Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
v0.1 bundle. Every `.md` file except the reserved `index.md` and `log.md` is a
**concept page**: YAML frontmatter (with a required `type`) followed by a
markdown body. Subdirectory `index.md` files are **generated** by the `okf`
tool; `docs/llm-wiki/index.md` (bundle root) and `docs/llm-wiki/log.md` are
hand-maintained.

## When to Use

- Creating a brand-new concept page, or editing an existing one's frontmatter
  or body.
- NOT for converting an existing repo doc into a wiki page — see
  `migrating-docs-to-wiki`.
- NOT for looking up answers in the wiki — see `searching-the-wiki`.
- NOT for running the validator or fixing its findings — see
  `validating-the-wiki` (but you must run it after any edit; see below).

## Quick Reference

Frontmatter template for a new page:

```yaml
---
type: Component
title: Human-Readable Name
description: One sentence used in indexes and search snippets.
resource: /playbooks/path/to/authoritative/file
tags: [lowercase, keywords]
timestamp: 2026-09-17T00:00:00Z
---
```

`resource` is a path from the **repo root** (e.g. `/roles/irods_cfg/README.md`),
not from `docs/llm-wiki/`.

Sections and the `type` each uses (free-form per spec, but stay consistent):

| Section | `type` | Use for |
| --- | --- | --- |
| `components/` | `Component` | A Data Store subsystem: iRODS catalog provider or resource server, ICAT DBMS, AMQP broker, HAProxy, SFTP, WebDAV |
| `runbooks/` | `Runbook` | A procedure spanning several playbooks, or the `testing/` harness |
| `ansible-playbooks/` | `Playbook` | A single playbook under `playbooks/` |
| `ansible-roles/` | `Role` | A role under `roles/`, including its `molecule/` scenarios |
| `ansible-plugins/` | `Plugin` | A module, lookup, or test plugin under `plugins/` |
| `irods-rules/` | `RuleSet` | A rule file under `playbooks/files/irods/etc/irods/` or its `*-env.re.j2` template |

Link style inside page bodies:

| Target | Form | Example |
| --- | --- | --- |
| Another wiki page | Bundle-absolute (preferred) | `[WebDAV](/components/webdav.md)` |
| Sibling page | Relative is allowed | `[WebDAV](./webdav.md)` |
| Repo file outside `docs/llm-wiki/` | Plain code span, never a markdown link | `` `roles/irods_cfg/` `` |
| External source | Full URL | `[spec](https://example.org/spec)` |

## Writing a Page

1. Pick the section from the table above and a lowercase-kebab filename; the
   path minus `.md` becomes the concept ID.
2. Write the frontmatter from the template. `type` is required and must be
   non-empty; `title`, `description`, and `timestamp` are lint-checked. Set
   `timestamp` to now (ISO 8601) on every meaningful edit.
3. Write the body. Cite sources at the bottom under a `# Citations` heading —
   repo paths as plain code spans, external material as URLs.
4. Add an entry to `docs/llm-wiki/log.md` under a `## YYYY-MM-DD` heading for
   today. Newest date group goes **first**; add to the existing group if
   today's already there.
5. Regenerate indexes and validate.

**REQUIRED SUB-SKILL:** after any wiki edit, run `validating-the-wiki` — the
edit is not done until `okf index` has been run and `okf check` reports 0
errors and 0 warnings.

## Common Mistakes

- **Putting frontmatter in `index.md` or `log.md`.** Reserved files take no
  frontmatter (only the bundle root `docs/llm-wiki/index.md` carries
  `okf_version`). A dated entry in `log.md` is the changelog; a concept page's
  own metadata lives in its frontmatter.
- **Hand-editing a subdirectory `index.md`.** They are generated from concept
  frontmatter; the validator flags drift (OKF106). Fix the page's `title`/
  `description` and re-run `okf index` instead.
- **Leaving `type` empty or missing.** It's the only hard-required field
  (OKF003); pick from the section table above.
- **Linking to files outside `docs/llm-wiki/`.** A markdown link that escapes
  the bundle is flagged (OKF108), and a bundle-absolute link like
  `/playbooks/irods_cfg.yml` resolves inside the wiki and dies (OKF101). Use the
  `resource` field or a plain code-span path in Citations.
- **Naming a page after a repo directory.** Sections are `ansible-playbooks/`,
  `ansible-roles/`, and `ansible-plugins/`, not `playbooks/`, `roles/`, or
  `plugins/`, so wiki links and repo paths stay distinguishable.
- **Forgetting the log entry.** Every meaningful change gets a line in
  `docs/llm-wiki/log.md`, newest-first.
