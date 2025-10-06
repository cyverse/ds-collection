#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

export IRODS_USER_PASSWORD
export IRODS_CATALOG_PROVIDER

echo "Initializing clerver session"

su --command="IRODS_HOST='$IRODS_CATALOG_PROVIDER' iinit" irods <<<"$IRODS_USER_PASSWORD" \
	&> /dev/null

echo "Starting server"
su --command='/usr/sbin/irodsServer -u' irods