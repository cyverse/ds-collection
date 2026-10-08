# testing

This folder contains the test harness for the DS playbooks. It consists of a simplified Data Store and a playbook runner.

## The Environment

The environment consists of a set of containers. The `amqp` container hosts the RabbitMQ broker that in turn hosts the `irods` exchange, where the Data Store publishes messages to. The `dbms_configured` container hosts the PostgreSQL server that in turn hosts the ICAT DB. The iRODS servers all run on AlmaLinux 9. The `webdav_configured` and `webdav_unconfigured` containers run AlmaLinux 8, because davrods 4.3.0_1.5.0, the release the WebDAV hosts use, doesn't install on AlmaLinux 9. They, the `sftp` container, and the `dbms_configured` and `dbms_unconfigured` containers boot systemd, so playbooks can start, stop and enable their services; the other containers run only sshd and the services their images start. The `provider_configured` container hosts a configured iRODS catalog service provider. The `provider_unconfigured` container hosts an unconfigured service provider. The `consumer_configured_centos` container hosts a configured catalog service consumer acting as a resource server for `replRes` and `ingestRes`; it keeps its old name, though it no longer runs CentOS. Finally, the `consumer_unconfigured` container hosts an unconfigured service consumer.

## Requirements

The harness needs Docker with the Compose v2 plugin (`docker compose`), and bash 4 or later for the scripts that use associative arrays. The inventories name containers the way Compose v2 does, so the older `docker-compose` v1 binary resolves to host names that don't exist.

On macOS the scripts stick to options the BSD tools share with the GNU ones, and `portability.sh` papers over the differences that remain, so no GNU coreutils install is needed. What is needed:

* macOS 12.3 or later, the first release whose `readlink` accepts `-f`.
* bash 4 or later ahead of `/bin/bash` on `PATH`, since macOS ships bash 3.2.
* An x86_64 Docker daemon. iRODS publishes x86_64 packages only, which is why the compose file and the image builds ask for `linux/amd64`. On Apple Silicon, run a fully emulated x86_64 virtual machine — for example `colima start --arch x86_64`, which needs `qemu` and `lima-additional-guestagents` installed. Do not use Rosetta translation: iRODS cannot run under it, because every translated process's `/proc/<pid>/exe` points at the translator outside the container, which aborts `irodsctl`, and the server then accepts connections without servicing them.

The test scripts give the tester container a terminal only when they have one, so they also run from scripts and CI jobs. `--inspect` needs a terminal.

## Building the Harness

There are two convenience scripts for building the docker images for the environment. `build` builds all the required images, and `clean` deletes them. Some images build from base images that `build` creates locally, so if your buildx builder uses the `docker-container` driver, run it as `BUILDX_BUILDER=default testing/build`.

The environment's images build `FROM` the `test-env-base` images, which a buildx builder that uses the `docker-container` driver can't see in Docker's image store. So unless `BUILDX_BUILDER` names a builder, `env/build` and `env/controller` use the Docker driver builder of the current Docker context, whatever builder is selected.

## Testing

`test-playbook` is a convenience script for running a playbook against the testing environment. This script will bring up the environment, run the playbook and any tests, and then tear down the environment. It performs the tests in the following order.

1. If there is a setup playbook, it runs this playbook.
1. If there is a playbook to test, it does the following.
   1. It performs a syntax checkout on the playbook under test.
   1. It runs the playbook on the testing inventory.
   1. If there are any tests of the playbook, it runs those tests.
   1. It performs an idempotency check of the playbook.
1. If the inspect option was provided, it opens a command prompt.

Before testing, the tester waits for every host to accept SSH connections, and for each configured iRODS server to accept connections on port 1247.

Tests can be defined for a given playbook. They should be placed in a playbook with the same name inside the `playbooks/tests` folder.

`test-playbook --irods-version <version>`, or the `IRODS_VERSION` environment variable, runs the configured iRODS servers on another iRODS release, such as 4.3.4, and passes it to the setup playbooks, the playbook under test, and its tests as `irods_version`. Tests that check an iRODS version should compare against `_irods_version` from `playbooks/group_vars/all/irods.yml`, not a literal release.

iRODS 4.3.1 occasionally segfaults while starting ([irods/irods#7747](https://github.com/irods/irods/issues/7747), fixed in 4.3.3). Both the EL7 and EL9 builds crash this way, in `libirods_plugin_dependencies.so`. When it happens, the playbook fails with `iRODS server failed to start` or `iRODS server failed to restart`, usually in a restart handler or in `setup_irods.py`. Sometimes the server crashes just after a restart reports success, and the next task that talks to it fails with `Could not connect to specified host and port: <host>:1247`. The servers that depend on the crashed one then fail to start as well. The host's kernel log records every crash, so `journalctl -k | grep irodsServer` shows whether a failure was this bug.

So that these crashes don't fail a test, `test-playbook`, `test-plugin`, `test-rules`, and `test-leaks` retry once, using `irods_crash.sh`. When a run fails and its output contains any of these messages, the script tears down the environment, brings up a fresh one, and runs everything again. A server that fails to start for any other reason fails the retry too, so the retry doesn't hide real problems. `test-playbook` and `test-plugin` don't retry with `--inspect`, because the inspection shell needs the terminal and its output isn't captured. A configured server that never accepts connections fails the wait before testing with `iRODS server failed to start`, so it's retried too.

## Running every test

`test-all` runs each playbook's test with the inventory and setup playbooks it needs, each plugin's test with `hosts-configured`, and the iRODS rule tests, each in a fresh environment. It prints a line per test as it finishes, then how many passed and which failed, and writes each test's output to a log in `./test-results`, or the directory given with `-o`. It exits nonzero if any test failed.

```bash
testing/test-all                         # every test
testing/test-all -v 4.3.4                # every test, on iRODS 4.3.4
testing/test-all --list                  # the IDs of the tests
testing/test-all playbook/irods_cfg rules  # the named tests
```

A playbook test that needs an inventory other than `hosts-all`, or setup playbooks, is listed in the `PLAYBOOK_INVENTORIES` and `PLAYBOOK_SETUPS` tables at the top of the script. Add a new test there when it needs them.

## The iRODS rule tests

The `unittest` modules in `playbooks/tests/rules` test the rule logic against a live server. `test-rules` starts the environment, prepares it for them, runs them, prints a summary, and stops the environment. It exits nonzero if any module failed.

```bash
testing/test-rules                   # every module
testing/test-rules cyverse_logic     # the named modules
testing/test-rules -v 4.3.4          # every module, on iRODS 4.3.4
```

As with `test-playbook`, `--irods-version`, or `IRODS_VERSION`, runs the configured iRODS servers on another release and passes it to the setup playbooks as `irods_version`. Without it, `irods_resource_server.yml` would provision the servers for the default release.

A freshly started environment lacks several things the tests depend on, so before running them `test-rules` does the following. Preparing the environment takes about four minutes on an x86_64 host.

* It runs `irods_cfg.yml` to deploy the Data Store's rule bases, which the provider image doesn't install. Without them, every rule call fails with `NO_MICROSERVICE_FOUND_ERR`.
* It runs `irods_runtime_init.yml` to create the `rodsadmin` group. Without it, every user creation fails with `CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME`.
* It runs `dbms_icat.yml` to create the `r_transfer_totals` table, which `cyverse_transfer_tracking.py` empties in every `tearDown`.
* It runs `irods_resource_server.yml` and the four `*_usage.yml` playbooks to create the AVRA, ESIIL, NCEMS, and PIRE resources and collections.
* It restarts every iRODS server in test mode, which writes the `/var/lib/irods/log/test_mode_output.log` that many tests read.

Each module runs in its own container, since a module that stops partway can leave a mock rule base deployed.

## Molecule

The roles are tested with the molecule scenarios in `molecule/`, which run on the host rather than in this environment. `test-molecule` runs them with the setup they need.

```bash
testing/test-molecule                              # every scenario
testing/test-molecule haproxy irods_cfg_upgrade    # the named scenarios
```

It runs each scenario even when an earlier one fails, prints a summary, and exits nonzero if any failed. Along the way, it does the following.

* It tests a copy of the working tree, uncommitted changes included, placed at `ansible_collections/cyverse/ds` in a temporary directory. `irods_cfg_upgrade` calls `json_patch` by its bare name, which Ansible resolves only when the playbook itself sits at such a path, so a symlink isn't enough.
* It installs `requirements.txt` and the `requirements.yml` collections into `.venv-molecule` at the collection root, and reinstalls them when either file changes. With `uv` it uses Python 3.12, since ansible-core 2.16 supports controller Pythons 3.10 through 3.12; without it, it uses `python3`. Delete `.venv-molecule` to force a clean install.
* It puts `.venv-molecule/bin` first on `PATH`, because molecule runs whichever `ansible` it finds there.
* It sets `DOCKER_HOST` from the current Docker context when it isn't already set, because molecule reaches Docker through the Python SDK, which ignores contexts. This matters for daemons like colima's.
* It points `ANSIBLE_HOME` into the temporary directory. Otherwise molecule installs the collection under test and the scenarios' Galaxy roles into `~/.ansible`, where they shadow any other `cyverse.ds`.

The `postgresql`, `haproxy`, `rabbitmq`, `firewalld`, and `irods_cfg_initialize` scenarios boot systemd in privileged containers. Their Dockerfiles embed `testing/env/base/systemd.sh`, like the testing environment's systemd images, so editing that script changes them too. The `postgresql` scenario skips `no_testing` tasks, because the role's huge pages and swappiness tasks would change the host's kernel settings.

## PEP memory leaks

Defining some PEPs makes the iRODS agent serving a connection leak memory in proportion to the data it moves, whatever the PEP's body does (see irods/irods#8106). `test-leaks` measures this so a baseline can be recorded and a fix checked against it.

```bash
testing/test-leaks                                     # iRODS 4.3.1
testing/test-leaks --irods-version 4.3.5               # iRODS 4.3.5
testing/test-leaks --data-store-rules                  # with the Data Store's rule bases
testing/test-leaks --cases testing/leak-check/exec_cmd_cases.yml
testing/test-leaks -o /tmp/leaks -- -e leak_check_threshold_mib=32
```

It starts the environment, runs `leak-check/leak_check.yml` against the catalog service provider, prints a summary, and stops the environment. Options after `--` go to `ansible-playbook`. The default run takes about five minutes.

The probe, `leak-check/files/leak_probe.py`, runs each workload and size once as a control, with no PEP defined, and once for each PEP in `leak_check_peps`, defined with an empty body. It samples the resident memory of the agent serving the workload, and the difference between a PEP's growth and its control's is the leak. The workloads target `leakCheckResc`, a resource on the provider, since a resource elsewhere would move the work to another server's agent.

| Workload   | Client             | Requests                                                | Sizes
| ---------- | ------------------ | ------------------------------------------------------- | ------------
| `put`      | `iput -r`          | one `DATA_OBJ_PUT` per file                             | small, large
| `bulk_put` | `iput -b -r`       | `BULK_DATA_OBJ_PUT`, many files per request             | small
| `write`    | python-irodsclient | one `DATA_OBJ_WRITE` per operation, to one data object  | small, large
| `read`     | python-irodsclient | one `DATA_OBJ_READ` per operation, from one data object | small, large

`small` is 1000 operations of 64 KiB and `large` is 100 of 4 MiB, so a leak per byte can be told from a leak per request. Transfer buffers swing an agent's memory by tens of MiB, so growth is measured on the floor: the rise of the lowest sample from the run's first quarter to its last, extrapolated over the run. `LEAK?` marks a leak over `leak_check_threshold_mib`, 16 MiB by default. The `agents` column counts the agents that served the workload out of all that started during it. The results, with every sample, go to `alma9-<version>.json` in `./leak-check-results`, or the directory given with `-o`.

* `--data-store-rules` deploys the Data Store's rules with `irods_cfg.yml`, `irods_runtime_init.yml`, and `dbms_icat.yml`, then runs each workload in `leak_check_workloads` once against them, with no PEP added and no control, so the leak is the agent's whole growth. The environment has no AMQP broker, so `amqp-topic-send` is replaced with a script that succeeds without output, the way a real publish does; otherwise every failed publish would add `msiExecCmd`'s leak. The results file ends in `-data-store.json`.
* `--cases <file>` runs the cases in a vars file under the stock rule bases; it can't be combined with `--data-store-rules`. The file can set any of the playbook's `leak_check_*` variables, including `leak_check_command_scripts` for scripts the cases' rules call with `msiExecCmd`. The results file ends in the cases file's name. `leak-check/exec_cmd_cases.yml` reproduces a leak in `msiExecCmd`, described at the top of that file.
* `--irods-version <version>` runs the provider on another iRODS release, such as 4.3.5 to compare against the default 4.3.1. It builds that version's provider image the first time it's needed and tags it with the version, so the default image stays. `testing/build` rebuilds it along with the default.

<!-- TODO: document test-plugin -->