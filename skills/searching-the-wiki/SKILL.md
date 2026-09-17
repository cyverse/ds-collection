---
name: searching-the-wiki
description: Use when answering questions about how the Data Store collection deploys or operates something — consult docs/llm-wiki/ before digging through playbooks/, roles/, plugins/, or the iRODS rule files; e.g. "how are resource servers configured" or "how does the replication rule logic work".
---

# Searching the Wiki

## Overview

`docs/llm-wiki/` is the curated knowledge layer for this repo (OKF v0.1
format). It's the fastest place to answer "how does X work here" questions:
each concept page has frontmatter (`type`, `title`, `description`, `tags`) and
a body, and its `resource` field plus `# Citations` section point at the
authoritative files in the repo. The wiki summarizes; the cited files are
ground truth.

## When to Use

- Answering operational or architectural questions about the Data Store
  collection before grepping `playbooks/`, `roles/`, `plugins/`, or
  `playbooks/files/irods/etc/irods/` from scratch.
- NOT for creating or editing pages — see `writing-wiki-pages`.
- If the answer is missing or stale, say so; offer to add it via
  `writing-wiki-pages` or `migrating-docs-to-wiki`.

## Quick Reference

```bash
# Entry point: sections and their indexes
cat docs/llm-wiki/index.md

# Search frontmatter metadata
grep -rl 'tags: \[.*irods' docs/llm-wiki/
grep -rl 'type: Runbook' docs/llm-wiki/

# Search page content
grep -ril 'resource hierarchy' docs/llm-wiki/
```

Navigation: start at `docs/llm-wiki/index.md`, follow a section link
(e.g. `/components/index.md`), pick the page by its one-line description.
Bundle-absolute links like `/components/webdav.md` resolve relative to
`docs/llm-wiki/`, i.e. `docs/llm-wiki/components/webdav.md`. A page's
`resource` field is different: it's relative to the repo root.

## Trust Model

- Frontmatter `description` lines in the indexes are reliable summaries — they
  are generated from the pages themselves.
- A page's `timestamp` says when it last had a meaningful change; for anything
  operationally destructive (stopping or restarting iRODS, blocking the proxy,
  catalog or DBMS changes), verify against the file named in `resource` /
  Citations before acting.
- `docs/llm-wiki/log.md` records what changed and when, newest-first.

## Common Mistakes

- **Treating a dead link as an error.** In OKF, a link to a nonexistent page
  marks knowledge that isn't written yet — fall back to the repo source, and
  optionally offer to write the missing page.
- **Trusting the wiki over its sources for risky actions.** The wiki is a
  summary; the `resource` file and the playbooks, roles, and rule files it
  cites are authoritative.
- **Grepping the collection first.** Check the wiki first — if it answers the
  question, you're done; if not, you've lost a few seconds.
