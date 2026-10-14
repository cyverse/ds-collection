#!/usr/bin/env bash
#
# Helpers for the test scripts that can run the testing environment on another
# iRODS release.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

# Fails when IRODS_VERSION is set but isn't a release number, e.g., 4.3.4.
# Input:
#  IRODS_VERSION  the iRODS release to check
irods_version::check() {
	if [[ -n "${IRODS_VERSION-}" && ! "$IRODS_VERSION" =~ ^[0-9]+(\.[0-9]+)+$ ]]; then
		printf 'The iRODS version %s is not a release number like 4.3.4\n' "$IRODS_VERSION" >&2
		return 1
	fi
}


# Fails when IRODS_UPGRADE_FROM is set but isn't a release number earlier than
# IRODS_VERSION, which defaults to 4.3.1.
# Input:
#  IRODS_UPGRADE_FROM  the iRODS release the environment starts on
#  IRODS_VERSION       the iRODS release it's upgraded to
irods_version::check_upgrade() {
	if [[ -z "${IRODS_UPGRADE_FROM-}" ]]; then
		return 0
	fi

	if ! IRODS_VERSION="$IRODS_UPGRADE_FROM" irods_version::check; then
		return 1
	fi

	local to="${IRODS_VERSION:-4.3.1}"

	local earliest
	earliest="$(printf '%s\n' "$IRODS_UPGRADE_FROM" "$to" | sort --version-sort | head --lines=1)"

	if [[ "$IRODS_UPGRADE_FROM" == "$to" || "$earliest" != "$IRODS_UPGRADE_FROM" ]]; then
		printf 'The iRODS version to upgrade from, %s, is not earlier than %s\n' \
			"$IRODS_UPGRADE_FROM" "$to" >&2
		return 1
	fi
}
