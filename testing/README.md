# testing

This folder contains the test harness for the DS playbooks. It consists of a simplified Data Store and a playbook runner.

## The Environment

The environment consists of a set of containers. The `amqp` container hosts the RabbitMQ broker that in turn hosts the `irods` exchange, where the Data Store publishes messages to. The `dbms_configured` container hosts the PostgreSQL server that in turn hosts the ICAT DB. The `provider_configured` container hosts a configured iRODS catalog service provider. The `provider_unconfigured` container hosts an unconfigured service provider. The `consumer_configured_centos` container hosts a configured CentOS catalog service consumer acting as a resource server. The `consumer_configured_ubuntu` container hosts a configured Ubuntu catalog service consumer acting as a resource server. Finally, the `consumer_unconfigured` container hosts an unconfigured service consumer.

## Requirements

The harness needs Docker with the Compose v2 plugin (`docker compose`), and bash 4 or later for the scripts that use associative arrays. The inventories name containers the way Compose v2 does, so the older `docker-compose` v1 binary resolves to host names that don't exist.

On macOS the scripts stick to options the BSD tools share with the GNU ones, and `portability.sh` papers over the differences that remain, so no GNU coreutils install is needed. What is needed:

* macOS 12.3 or later, the first release whose `readlink` accepts `-f`.
* bash 4 or later ahead of `/bin/bash` on `PATH`, since macOS ships bash 3.2.
* An x86_64 Docker daemon. iRODS, PostgreSQL 12 for EL7, and the CentOS 7 repositories publish x86_64 packages only, which is why the compose file and the image builds ask for `linux/amd64`. On Apple Silicon, run a fully emulated x86_64 virtual machine — for example `colima start --arch x86_64`, which needs `qemu` and `lima-additional-guestagents` installed. Do not use Rosetta translation: iRODS cannot run under it, because every translated process's `/proc/<pid>/exe` points at the translator outside the container, which aborts `irodsctl`, and the server then accepts connections without servicing them.

`test-playbook` and `test-plugin` start the tester with `docker run --interactive --tty`, so they need a terminal. To run them from a script or a CI job, give them a pseudo-terminal with `script`, whose syntax differs between platforms. On macOS, use `script -q /dev/null testing/test-playbook -P <playbook>`. On Linux, util-linux's `script` rejects that form, so use `script -qec "testing/test-playbook -P <playbook>" /dev/null`, where `-e` passes the command's exit status through.

## Building the Harness

There are two convenience scripts for building the docker images for the environment. `build` builds all the required images, and `clean` deletes them.

## Testing

`test-playbook` is a convenience script for running a playbook against the testing environment. This script will bring up the environment, run the playbook and any tests, and then tear down the environment. It performs the tests in the following order.

1. If there is a setup playbook, it runs this playbook.
1. If there is a playbook to test, it does the following.
   1. It performs a syntax checkout on the playbook under test.
   1. It runs the playbook on the testing inventory.
   1. If there are any tests of the playbook, it runs those tests.
   1. It performs an idempotency check of the playbook.
1. If the inspect option was provided, it opens a command prompt.

Tests can be defined for a given playbook. They should be placed in a playbook with the same name inside the `playbooks/tests` folder.

## The iRODS rule tests

The `unittest` modules in `playbooks/tests/rules` run against a live server, and nothing here invokes them. A freshly started environment lacks several things they depend on, and each gap fails a different set of tests:

* The Data Store's rule bases, which the provider image doesn't install. `irods_cfg.yml` deploys them. Without them, every rule call fails with `NO_MICROSERVICE_FOUND_ERR`.
* The `rodsadmin` group, which `irods_runtime_init.yml` creates. Without it, every user creation fails with `CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME`, because `cyverse_logic_acCreateCollByAdmin` can't grant the group access to the new home collection and then fails to give it a UUID.
* The `r_transfer_totals` table, which `dbms_icat.yml` creates. `cyverse_transfer_tracking.py` empties it in every `tearDown`.
* The AVRA, ESIIL, NCEMS, and PIRE resources and collections, which `irods_resource_server.yml` and the four `*_usage.yml` playbooks create. The `avra` and `pire` storage resources belong to the unconfigured consumer, so these playbooks run against the `hosts-unconfigured-consumer` inventory.
* iRODS running in test mode, which writes the `/var/lib/irods/log/test_mode_output.log` that many tests read. Run without `--skip-tags=no_testing`, `irods_cfg.yml` restarts iRODS without `--test`. With the skip, its restart into test mode fails intermittently. The steps below therefore run it without the skip, then restart each server in test mode by hand.

From the collection root, with the environment stopped:

```bash
. testing/config.inc
testing/env/controller testing/config.inc start

tester() {
  docker run --rm -i --entrypoint bash \
    --env IRODS_HOST="$IRODS_PROVIDER_CONF_HOST" \
    --env IRODS_ZONE_NAME="$IRODS_ZONE_NAME" \
    --env PGHOST="$DBMS_HOST" \
    --network "$DOMAIN" \
    --platform=linux/amd64 \
    --volume "$PWD":/root/.ansible/collections/ansible_collections/cyverse/ds:ro \
    --volume "$PWD"/playbooks:/playbooks-under-test:ro \
    ansible-tester -c "$1"
}

tester 'ansible-playbook -i /inventory/hosts-configured /wait-for-ready.yml'
tester 'ansible-playbook -i /inventory/hosts-configured /playbooks-under-test/irods_cfg.yml'
for p in irods_runtime_init dbms_icat; do
  tester "ansible-playbook --skip-tags=no_testing -i /inventory/hosts-configured /playbooks-under-test/$p.yml"
done
for p in irods_resource_server avra_usage esiil_usage ncems_usage pire_usage; do
  tester "ansible-playbook --skip-tags=no_testing -i /inventory/hosts-unconfigured-consumer /playbooks-under-test/$p.yml"
done
for svc in provider_configured consumer_configured_centos consumer_configured_ubuntu consumer_unconfigured; do
  docker exec "$ENV_NAME-$svc-1" su - irods -c '/var/lib/irods/irodsctl --test restart'
done

tester 'cd /playbooks-under-test/tests/rules && python cyverse_logic.py'
```

Use containers rather than `test-playbook`, which always stops the environment afterward and takes the setup with it. `tester` mounts the collection the way `ansible-tester/run` does and replaces the image's `/test-playbook` entrypoint with `bash`, so it needs no terminal. Run each module in its own container, as `python <module>.py`, since several module names contain hyphens and can't be run with `-m`. A module that stops partway can leave a mock rule base deployed, which is another reason to keep them apart. On an x86_64 host the setup takes about four minutes. Stop the environment with `testing/env/controller testing/config.inc stop`.

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

<!-- TODO: document test-plugin -->