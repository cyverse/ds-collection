#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

export IRODS_USER_PASSWORD
export IRODS_CATALOG_PROVIDER
export IRODS_ZONE_NAME

main() {
	log $$ 'Initializing clerver session ...'

	su --command="IRODS_HOST='$IRODS_CATALOG_PROVIDER' iinit" irods <<<"$IRODS_USER_PASSWORD" \
		> /dev/null

	log $$ 'Starting server ...'
	su --command='/usr/sbin/irodsServer -u' irods
}

log() {
	local pid="$1"
	local msg="$2"

	local ts
	ts="$(date --utc '+%FT%T.%N' | sed 's/......$/Z/')"

	printf \
		'{"log_category":"init","log_level":"info","log_message":"%s","server_host":"%s","server_pid":%s,"server_timestamp":"%s","server_type":"server","server_zone":"%s"}\n' \
		"$msg" "$HOSTNAME" "$pid" "$ts" "$IRODS_ZONE_NAME"
}

main "$@"