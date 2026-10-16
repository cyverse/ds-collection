#!/usr/bin/env bash
#
# Helpers for the scripts that turn a freshly started testing environment into
# a small Data Store, with the Data Store's rule bases deployed. The scripts
# must define COLLECTION_DIR and source config.inc first.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

# Runs the playbooks that deploy the Data Store's rule bases and create what
# they depend on: the rodsadmin group, the r_transfer_totals table, and the
# AVRA, ESIIL, NCEMS, and PIRE resources and collections.
# Input:
#  IRODS_VERSION  (optional) the iRODS release the configured servers run
data_store_env::prepare() {
	data_store_env::run_playbook hosts-configured /wait-for-ready.yml

	# With --skip-tags=no_testing, irods_cfg's restart into test mode fails
	# intermittently, so the servers restart normally here.
	data_store_env::run_playbook hosts-configured /playbooks-under-test/irods_cfg.yml

	local playbook
	for playbook in irods_runtime_init dbms_icat; do
		data_store_env::run_playbook hosts-configured \
			--skip-tags=no_testing /playbooks-under-test/"$playbook".yml
	done

	# The avra and pire storage resources belong to the unconfigured consumer.
	for playbook in irods_resource_server avra_usage esiil_usage ncems_usage pire_usage; do
		data_store_env::run_playbook hosts-unconfigured-consumer \
			--skip-tags=no_testing /playbooks-under-test/"$playbook".yml
	done
}


# Upgrades the configured iRODS servers to IRODS_VERSION with irods_upgrade.yml.
# Input:
#  IRODS_VERSION  (optional) the iRODS release to upgrade to
data_store_env::upgrade() {
	data_store_env::run_playbook hosts-configured /wait-for-ready.yml
	data_store_env::run_playbook hosts-configured \
		--skip-tags=no_testing /playbooks-under-test/irods_upgrade.yml
}


# Runs a playbook in an ansible-tester container.
# Input:
#  $1             the inventory hosts file in the container's /inventory
#  $2...          the ansible-playbook options followed by the playbook's path
#                 in the container
#  IRODS_VERSION  (optional) passed to the playbook as irods_version
data_store_env::run_playbook() {
	local hosts="$1"
	shift

	data_store_env::run_in_tester \
		"ansible-playbook -i /inventory/$hosts ${IRODS_VERSION:+--extra-vars=irods_version=$IRODS_VERSION} $*"
}


# Runs a bash command in an ansible-tester container, mounting the collection
# the way ansible-tester/run does. It replaces the image's /test-playbook
# entrypoint, so it needs no terminal.
# Input:
#  $1  the command
data_store_env::run_in_tester() {
	local cmd="$1"

	docker run --rm --entrypoint bash \
		--env IRODS_HOST="$IRODS_PROVIDER_CONF_HOST" \
		--env IRODS_ZONE_NAME="$IRODS_ZONE_NAME" \
		--env PGHOST="$DBMS_HOST" \
		--network "$DOMAIN" \
		--platform=linux/amd64 \
		--volume "$COLLECTION_DIR":/root/.ansible/collections/ansible_collections/cyverse/ds:ro \
		--volume "$COLLECTION_DIR"/playbooks:/playbooks-under-test:ro \
		ansible-tester -c "$cmd"
}
