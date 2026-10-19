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
