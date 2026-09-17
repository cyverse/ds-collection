---
type: Runbook
title: Maintaining This Wiki
description: How to add, edit, migrate, and validate pages in this wiki — frontmatter rules, sections, generated indexes, the update log, and the okf tool.
resource: /tools/okf/README.md
tags: [wiki, okf, meta]
timestamp: 2026-09-17T00:00:00Z
---

This wiki is an
[Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
v0.1 bundle rooted at `docs/llm-wiki/`. Every `.md` file except the reserved
`index.md` and `log.md` is a **concept page**. The wiki summarizes; each page's
`resource` field and `# Citations` section point at the authoritative files in
the repo.

## Page anatomy

A concept page is YAML frontmatter followed by a markdown body:

```yaml
---
type: Component          # required, non-empty; see the section table below
title: Human-Readable Name
description: One sentence; indexes and search snippets are built from this.
resource: /playbooks/irods_catalog_provider.yml   # repo-root path; omit for abstract concepts
tags: [lowercase, keywords]
timestamp: 2026-09-17T00:00:00Z   # update on every meaningful change
---
```

`resource` is a path from the **repo root**, while bundle-absolute links in
page bodies are paths from **`docs/llm-wiki/`**.

## Sections

| Section | `type` | Holds |
| --- | --- | --- |
| `components/` | `Component` | A Data Store subsystem: iRODS catalog provider or resource server, the ICAT DBMS, AMQP broker, HAProxy, SFTP, or WebDAV |
| `runbooks/` | `Runbook` | A procedure spanning several playbooks, or the testing harness |
| `ansible-playbooks/` | `Playbook` | A single playbook under `playbooks/` |
| `ansible-roles/` | `Role` | A role under `roles/`, including its molecule scenarios |
| `ansible-plugins/` | `Plugin` | A module, lookup, or test plugin under `plugins/` |
| `irods-rules/` | `RuleSet` | An iRODS rule file under `playbooks/files/irods/etc/irods/` or its template |

Section names deliberately differ from the repo's top-level directories so a
repo path in a code span (`` `playbooks/irods_cfg.yml` ``) can't be mistaken
for a wiki link (`/ansible-playbooks/irods-cfg.md`) when grepping.

Link wiki pages with bundle-absolute paths (`/components/irods-catalog-provider.md`);
reference repo files outside the wiki as plain code spans
(`` `roles/irods_cfg/` ``), never markdown links.

## Reserved files

- `index.md` — a directory listing. The root one (this bundle's entry point) is
  hand-maintained and carries the only permitted frontmatter, `okf_version`.
  **Subdirectory index files are generated** — never edit them by hand.
- `log.md` — the update history: one `# ` title, then `## YYYY-MM-DD` groups,
  newest first.

## Making a change

1. Create or edit the concept page; set `timestamp` to now.
2. Add a line to [the update log](/log.md) under today's date group
   (newest group first).
3. Regenerate indexes and validate from the repo root:

```bash
uv run --project tools/okf okf index docs/llm-wiki
uv run --project tools/okf okf check docs/llm-wiki
```

4. `okf check` must finish with **0 errors**; treat warnings as things to fix
   or consciously accept (a dead link can be deliberate — it marks a page worth
   writing). Findings print as `file:line: SEVERITY CODE message`; codes and
   fixes are tabulated in the `validating-the-wiki` skill and
   `tools/okf/README.md`.

When converting an existing repo doc, migration is **copy, not move**: the
original stays put and becomes the page's `resource`.

## Tooling and skills

The validator/indexer lives at `tools/okf/` (uv-managed Python; see its
README). Five repo skills in `skills/` cover wiki work —
`writing-wiki-pages`, `migrating-docs-to-wiki`, `searching-the-wiki`,
`validating-the-wiki`, and `updating-the-wiki` (the end-of-task staleness
check that fires after ordinary collection work). Claude Code loads them from
`.claude/skills/` and other agents from `.agents/skills/`; both are symlinks
to `skills/`. The repo `AGENTS.md` (with `CLAUDE.md` symlinked to it) instructs
agents to run the staleness check after changes to the collection, so wiki
upkeep doesn't depend on being asked.

# Citations

[1] [Open Knowledge Format specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) — the format this wiki conforms to.
[2] `tools/okf/README.md` — tool usage, output format, exit codes.
[3] `skills/` — the five wiki skills.
[4] `AGENTS.md` — the standing instruction to keep the wiki current.
