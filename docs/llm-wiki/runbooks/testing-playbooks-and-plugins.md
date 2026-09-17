---
type: Runbook
title: Testing Playbooks and Plugins
description: How the Docker-based harness in testing/ builds a small Data Store, runs a playbook or plugin test against it, checks idempotency, and tears it down — scripts, containers, inventories, tags, and known doc/code discrepancies.
resource: /testing/README.md
tags: [testing, docker, docker-compose, ansible-tester, idempotency, inventory]
timestamp: 2026-09-17T00:00:00Z
---

`testing/` holds the integration test harness for the collection's playbooks
and plugins. It has two parts: `testing/env/`, a docker-compose project that
stands up a simplified Data Store, and `testing/ansible-tester/`, an image
that runs Ansible against that environment. Roles are tested separately with
molecule (see [Testing Roles with Molecule](/runbooks/testing-roles-with-molecule.md)).

## Building and cleaning images

```bash
testing/build   # base images, compose images, and ansible-tester
testing/clean   # deletes them
```

`testing/build` passes `testing/config.inc` to `env/build` and
`ansible-tester/build`:

- `env/build` builds `test-env-base:<os>` from `env/base/Dockerfile.<os>` for
  alma10, alma9, centos7, ubuntu1804, ubuntu2004, ubuntu2204, and ubuntu2404,
  then runs `docker compose build` (or `docker-compose` if installed) with the
  project name `$ENV_NAME`.
- `ansible-tester/build` copies the repo's `requirements.txt` and
  `requirements.yml` into its build context and builds the `ansible-tester`
  image with `IRODS_CLERVER_PASSWORD` as a build arg.

`testing/clean` removes `ansible-tester`, every image matching `$ENV_NAME-*`,
and the `test-env-base` images.

## Configuration

`testing/config.inc` exports the values the compose file and scripts use:
`ENV_NAME=dstesting`, network `DOMAIN=dstesting_default`, zone `testing`,
clerver password `password`, last ephemeral port `20009`, provider system
group `irods_provider`, vault `/var/lib/irods/Vault`, resource names `replRes`
(CentOS consumer) and `ingestRes` (Ubuntu consumer, also the default
resource), schema validation from `file:///var/lib/irods/configuration_schemas`,
and the container host names, which have the form
`dstesting-<service>-1.dstesting_default`.

## The environment

`testing/env/docker-compose.yml` defines these services. All but `cbuoy` run
privileged with a TTY.

| Service | Image / build | Role in tests |
| --- | --- | --- |
| `amqp` | `test-env-base:ubuntu2204` | RabbitMQ host (in `unmanaged_systems`) |
| `dbms_configured` | `postgresql/Dockerfile.configured` | PostgreSQL with the ICAT DB for the zone |
| `dbms_unconfigured` | `postgresql/Dockerfile.unconfigured` | Bare DBMS hosts; started with `--scale dbms_unconfigured=2` |
| `provider_configured` | `irods-provider/Dockerfile.configured` | Configured catalog service provider |
| `provider_unconfigured` | `irods-provider/Dockerfile.unconfigured` | Unconfigured provider |
| `consumer_configured_centos` | `irods-consumer/Dockerfile.configured-centos` | Resource server hosting `replRes` |
| `consumer_configured_ubuntu` | `irods-consumer/Dockerfile.configured-ubuntu` | Resource server hosting `ingestRes` |
| `consumer_unconfigured` | `irods-consumer/Dockerfile.unconfigured` | Unconfigured consumer |
| `consumer_containerized_alma` | `test-env-base:alma10` | Host for a containerized resource server |
| `consumer_containerized_ubuntu` | `test-env-base:ubuntu2404` | Host for a containerized resource server |
| `sftp` | `sftp/Dockerfile` | SFTP host |
| `webdav_configured`, `webdav_unconfigured` | `webdav/Dockerfile.*` | WebDAV hosts |
| `cbuoy` | `test-env-base:alma9` | Member of the `cbuoy` inventory group |

`env/controller <inc> start` runs `up -d --scale dbms_unconfigured=2`;
`stop` runs `down --remove-orphans --volumes`, so nothing persists between
runs. The base entrypoint starts an optional service script and then `sshd`;
`env/base/config.sh` removes root's password and configures passwordless root
SSH, which is how `ansible-tester` reaches the containers. The configured
provider and consumers start iRODS with `irodsctl --test`, which writes
`/var/lib/irods/log/test_mode_output.log`.

## Running a playbook test

```bash
testing/test-playbook -P <playbook> [-S <setup1,setup2>] [-I <hosts-file>] [-i] [-p]
```

| Option | Meaning |
| --- | --- |
| `-P` | Playbook under test, relative to `playbooks/`; `.yml` is added if there's no extension |
| `-S` | Comma-separated playbooks to run first, in order |
| `-I` | Inventory hosts file in `ansible-tester/inventory/` (default `hosts-all`) |
| `-i` | Open a shell in the tester container afterward for inspection |
| `-p` | Use the `minimal` stdout callback for more readable output |

The script starts the environment, runs `ansible-tester/run`, and always stops
the environment afterward. `run` starts the `ansible-tester` container on the
`$DOMAIN` network with the collection mounted read-only at
`/root/.ansible/collections/ansible_collections/cyverse/ds`, `playbooks/`
mounted at `/playbooks-under-test`, and `IRODS_HOST`, `IRODS_ZONE_NAME`, and
`PGHOST` pointed at the configured provider, zone, and DBMS.

Inside the container, `test-playbook.sh` does the following:

1. Waits for every non-localhost inventory host to accept connections
   (`wait-for-ready.yml`, 100-second timeout).
2. Runs the setup playbooks, if any, with `--skip-tags=no_testing`.
3. Runs `ansible-playbook --syntax-check` on the playbook.
4. Runs the playbook with `--skip-tags=no_testing`.
5. If `playbooks/tests/<same filename>` exists, runs it as the test.
6. Runs the playbook again with `--skip-tags='no_testing, non_idempotent'`
   and fails if any output line starts with `changed:` or `fatal:`.
7. Prints `PASSED` or `FAILED`, then opens `bash` if `-i` was given (after
   removing `/root/.irods/.irodsA`).

The tester image also installs iCommands and `postgresql-client`, and sets
`IRODS_USER_NAME=rods`, `IRODS_PASSWORD` (the clerver password),
`PGDATABASE=ICAT`, `PGUSER=irodsuser`, and `PGPASSWORD=testpassword`, so the
inspection shell can query iRODS and the ICAT directly. Its apt preferences
pin `irods-*` packages to 4.3.1.

## Running a plugin test

```bash
testing/test-plugin <plugin_type> <plugin_name> [-I <hosts-file>] [-i] [-p] [-v]
```

`plugin_type` is the directory under `plugins/` (`module` is accepted for
`modules`); `plugin_name` may omit `.py`. The script requires both
`plugins/<type>/<name>.py` and `plugins/<type>/tests/<name>.yml` to exist. It
runs the same tester container, but mounts the plugin's `tests/` directory at
`/playbooks-under-test`, so the test playbook itself is the playbook under
test (syntax check, run, idempotency check). `-v` passes `-vvv` to Ansible.

Test playbooks exist for every module in `plugins/modules/` except
`json_patch` and `port_check_sender`, and for the `uuid` lookup
(`plugins/lookup/tests/uuid.yml`). The `warn_if_false` test plugin has none.

## Inventories

`testing/ansible-tester/inventory/` has five hosts files. They share the
same groups (only `hosts-all` also has `cbuoy`) and differ in which containers
fill them:

| File | Distinguishing hosts |
| --- | --- |
| `hosts-all` | Every container, including both unconfigured DBMS hosts, the unconfigured provider and consumer, the containerized hosts, and `cbuoy` |
| `hosts-configured` | Only configured hosts; empty `dbms_replicas` and `irods_resource_container` |
| `hosts-unconfigured-consumer` | Adds the unconfigured consumer and the containerized hosts; no `sftp` host |
| `hosts-unconfigured-dbms` | `dbms_unconfigured-1` as primary and `-2` as replica |
| `hosts-unconfigured-provider` | Adds the unconfigured provider to `irods_catalog`; no `sftp` host |

`unmanaged_systems` holds localhost, `amqp`, and the containerized hosts
where present; playbooks with host patterns such as
`all:!unmanaged_systems:!localhost` skip them.

## Writing tests

- Put a playbook's tests in `playbooks/tests/<playbook filename>`; the harness
  finds them by name. Test-only variables live in `playbooks/tests/group_vars/`
  and shared assertions in `playbooks/tests/tasks/`.
- Tag tasks that cannot run in a container (e.g. editing `/etc/hosts`)
  `no_testing`; they are skipped in every run.
- Tag tasks that are intentionally not idempotent (e.g. forced restarts)
  `non_idempotent`; they are skipped during the idempotency run.

## Discrepancies and caveats

These come from reading the scripts and READMEs, not from running them:

- `test-playbook` on Linux uses GNU `getopt` with the long option
  `--inventory`, but its `case` statement matches `-I|--inventory-hosts` and
  has no default branch, so `--inventory` would never be consumed and the
  option loop would not terminate. Use `-I`.
- `test-playbook` has no verbose option; it always passes an empty verbose
  argument. `test-plugin` supports `-v`.
- `test-plugin`'s docstring example (`./test_plugin --inspect ../irods/library
  irods_group`) uses an old script name and path.
- `testing/README.md` and `testing/env/README.md` omit the `sftp`, `webdav_*`,
  `dbms_unconfigured`, and `cbuoy` services, and `testing/README.md` also
  omits the containerized consumers.
- The example include file in `testing/env/README.md` uses the old `_1` host
  name form, defines `IRODS_CONSUMER_CONF_UBUNTU_HOST` twice (the first should
  be the CentOS host), and omits `IRODS_RES_CONF_CENTOS_NAME` and
  `IRODS_CLERVER_PASSWORD`, which the compose file uses.
- The `docker run` example in `testing/ansible-tester/README.md` passes only a
  playbook name, but the image's entrypoint expects six positional arguments
  (inspect, pretty, verbose, hosts, setup, playbook).
- Header comments in `env/build` and `env/clean` refer to five and four images.
- `inventory/host_vars/` contains `dstesting-apache-1.dstesting_default`, which
  matches no compose service.
- The scripts use GNU long options (`readlink --canonicalize`,
  `realpath --canonicalize-existing`, `tail --lines`), which BSD tools on macOS
  lack; only `testing/clean` and the option parsing in `test-playbook` have
  macOS branches.

# Citations

[1] `testing/README.md` — harness overview.
[2] `testing/env/README.md` — environment overview and include-file example.
[3] `testing/ansible-tester/README.md` — tester image and test stages.
[4] `testing/config.inc` — environment variables.
[5] `testing/build`, `testing/clean` — image lifecycle.
[6] `testing/test-playbook`, `testing/test-plugin` — test entry points.
[7] `testing/env/docker-compose.yml`, `testing/env/controller`, `testing/env/build`, `testing/env/clean` — environment definition and control.
[8] `testing/env/base/entrypoint.sh`, `testing/env/base/config.sh` — container startup and SSH access.
[9] `testing/ansible-tester/Dockerfile`, `testing/ansible-tester/run`, `testing/ansible-tester/test-playbook.sh`, `testing/ansible-tester/wait-for-ready.yml` — tester image and test stages.
[10] `testing/ansible-tester/inventory/` — test inventories.
[11] `playbooks/tests/`, `plugins/modules/tests/`, `plugins/lookup/tests/` — test playbooks.
