# testing

This folder contains the test harness for the DS playbooks. It consists of a simplified Data Store and a playbook runner.

## The Environment

The environment consists of a set of containers. The `amqp` container hosts the RabbitMQ broker that in turn hosts the `irods` exchange, where the Data Store publishes messages to. The `dbms_configured` container hosts the PostgreSQL server that in turn hosts the ICAT DB. The `provider_configured` container hosts a configured iRODS catalog service provider. The `provider_unconfigured` container hosts an unconfigured service provider. The `consumer_configured_centos` container hosts a configured CentOS catalog service consumer acting as a resource server. The `consumer_configured_ubuntu` container hosts a configured Ubuntu catalog service consumer acting as a resource server. Finally, the `consumer_unconfigured` container hosts an unconfigured service consumer.

## Requirements

The harness needs Docker with the Compose v2 plugin (`docker compose`), and bash 4 or later for the scripts that use associative arrays. The inventories name containers the way Compose v2 does, so the older `docker-compose` v1 binary resolves to host names that don't exist.

On macOS the scripts source `portability.inc`, which papers over the differences between the GNU tools and the BSD ones, so no GNU coreutils install is needed. Two things still are:

* bash 4 or later ahead of `/bin/bash` on `PATH`, since macOS ships bash 3.2.
* An x86_64 Docker daemon. iRODS, PostgreSQL 12 for EL7, and the CentOS 7 repositories publish x86_64 packages only, which is why the compose file and the image builds ask for `linux/amd64`. On Apple Silicon, run a fully emulated x86_64 virtual machine — for example `colima start --arch x86_64`, which needs `qemu` and `lima-additional-guestagents` installed. Do not use Rosetta translation: iRODS cannot run under it, because every translated process's `/proc/<pid>/exe` points at the translator outside the container, which aborts `irodsctl`, and the server then accepts connections without servicing them.

`test-playbook` and `test-plugin` start the tester with `docker run --interactive --tty`, so they need a terminal. To run them from a script or a CI job, give them a pseudo-terminal, e.g. `script -q /dev/null testing/test-playbook -P <playbook>`.

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

The `unittest` modules in `playbooks/tests/rules` run against a live server, and nothing here invokes them. They need the Data Store's rule bases deployed, which the provider image doesn't install, so a freshly started environment isn't enough: every rule call fails with `NO_MICROSERVICE_FOUND_ERR` until `irods_cfg.yml` has run.

1. Start the environment with `env/controller config.inc start`.
1. Run `irods_cfg.yml` against the `hosts-configured` inventory from an `ansible-tester` container. Use a container rather than `test-playbook`, which always stops the environment afterward and takes the deployed rules with it.
1. Run the modules from `/playbooks-under-test/tests/rules` in a container started the same way.

Both containers join the `$DOMAIN` network with the collection and `playbooks` mounted as `ansible-tester/run` mounts them, and with `IRODS_HOST`, `IRODS_ZONE_NAME`, and `PGHOST` set from `config.inc`. Neither needs a terminal.

<!-- TODO: document test-plugin -->