#!/usr/bin/env bash
#
# Helpers for retrying a test run that failed because iRODS 4.3.1 segfaulted
# while starting (irods/irods#7747, fixed in 4.3.3).
#
# A test script retries by running itself as a child process through
# irods_crash::run_retrying, and doing its work only when
# irods_crash::is_attempt says it is that child.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

# Printed by irodsctl, setup_irods.py and the irods_ctl module when the server can't start
readonly IRODS_CRASH_MESSAGE='iRODS server failed to (re)?start'


# Succeeds when the current process is an attempt started by
# irods_crash::run_retrying.
# Input:
#  IRODS_CRASH_ATTEMPT  set in the environment of each attempt
irods_crash::is_attempt() {
	[[ -n "${IRODS_CRASH_ATTEMPT-}" ]]
}


# Runs an executable that brings up the testing environment, tests something,
# and tears the environment down. If it fails and its output says an iRODS
# server failed to start, it is run once more, so the retry gets a fresh
# environment. A server that fails to start for another reason fails the retry
# too. The command must be an executable rather than a function, since a
# function run here would ignore errexit.
# Input:
#  $1     the executable
#  $2...  its arguments
# Output:
#  the executable's stdout and stderr to stdout
# Exports:
#  IRODS_CRASH_ATTEMPT  set to the attempt number for the executable
# Return:
#  the status of the last attempt
irods_crash::run_retrying() {
	local output
	output="$(mktemp)"

	# The callers' pipefail passes the executable's status through tee.
	local rc
	if IRODS_CRASH_ATTEMPT=1 "$@" 2>&1 | tee "$output"; then
		rc=0
	else
		rc=$?
	fi

	if (( rc != 0 )) && grep --extended-regexp --quiet --regexp "$IRODS_CRASH_MESSAGE" "$output"; then
		cat <<'EOF' >&2
An iRODS server failed to start. This is usually the iRODS 4.3.1 startup
segfault (irods/irods#7747), which "journalctl -k | grep irodsServer" on the
host confirms. Retrying once in a fresh environment.
EOF
		rc=0
		IRODS_CRASH_ATTEMPT=2 "$@" || rc=$?
	fi

	rm --force "$output"
	return "$rc"
}
