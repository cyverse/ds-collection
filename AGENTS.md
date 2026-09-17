# ds-collection

The `cyverse.ds` Ansible collection, which deploys and maintains the CyVerse
Data Store: an iRODS grid with its ICAT PostgreSQL DBMS, a RabbitMQ broker,
HAProxy, SFTPGo, and WebDAV. See `README.md` for control-node prerequisites.

## Layout

- `playbooks/` — the collection's playbooks, named by area (`infra_*`,
  `irods_*`, `dbms*`, `amqp*`, `proxy*`, `sftp*`, `webdav*`, and per-project
  `*_usage.yml`). Defaults live in `playbooks/group_vars/all/`, one file per
  area; variables are documented in `playbooks/README.md`.
- `playbooks/files/irods/etc/irods/*.re` and
  `playbooks/templates/irods/etc/irods/*-env.re.j2` — the iRODS rule logic
  deployed to the Data Store. `docs/deployment-artifacts/irods.md` describes it.
- `playbooks/tests/` — a test playbook per playbook, with the same filename.
  `playbooks/tests/rules/` holds Python `unittest` tests of the rule files.
- `plugins/` — custom modules (`irods_*`, `json_patch`, `port_check_*`), a
  lookup, and a test plugin. Module tests are playbooks in
  `plugins/modules/tests/<module>.yml`.
- `roles/` — roles tested with the matching scenarios in `molecule/`.
- `testing/` — the Docker-based harness for playbooks and plugins; see
  `testing/README.md`.
- `docs/llm-wiki/` — the OKF wiki (see below). `tools/okf/` validates it.

## Testing

- Playbooks: `testing/build` once to build the images, then
  `testing/test-playbook -P <playbook> [-S <setup,playbooks>] [-i]`. It runs a
  syntax check, the playbook, `playbooks/tests/<playbook>.yml`, and an
  idempotency re-run.
- Plugins: `testing/test-plugin module <name>`.
- Roles: `molecule test -s <scenario>` from the repo root.
- Tag tasks that can't run in the containers `no_testing`, and tasks that are
  intentionally not idempotent `non_idempotent`; the harness skips them.
- Lint with `ansible-lint` and `yamllint` (configured by `.ansible-lint` and
  `.yamllint`).

## Wiki upkeep

This repo has an OKF wiki at `docs/llm-wiki/` summarizing its playbooks, roles,
plugins, iRODS rules, and docs. After changing files under `playbooks/`,
`roles/`, `plugins/`, `molecule/`, `testing/`, `tools/`, `meta/`, or `docs/`
(outside `docs/llm-wiki/`), or the root `galaxy.yml`, requirements files, or
`README.md`, run the `updating-the-wiki` skill check before finishing the task:
find wiki pages that reference the changed files and refresh any that went
stale. Don't wait to be asked.

Wiki edits follow the `writing-wiki-pages` / `migrating-docs-to-wiki` skills
and must end with `okf index` + `okf check` (run via
`uv run --project tools/okf`) reporting 0 errors and 0 warnings — see
`validating-the-wiki`. The skills live in `skills/`; `.claude/skills` and
`.agents/skills` are symlinks to it.
