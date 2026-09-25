#!/usr/bin/env bash
#
# Helpers that hide the differences between the GNU tools on Linux and the BSD
# tools on macOS. Source this from the scripts that run on the developer's
# machine; the scripts that run inside the containers always have GNU tools.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

# Parses a command line, using long options only where getopt supports them.
# BSD getopt takes neither long options nor `--`, and it needs the unquoted
# "$*" splitting that GNU getopt makes unnecessary.
# Input:
#  $1     the short options, in getopt's form, e.g., hP:
#  $2     the long options, in getopt's form, e.g., help,playbook:
#  $3     the name to report errors under
#  $4...  the command line to parse
# Output:
#  the normalized command line to stdout, ready for `eval set --`
portability::getopt() {
	local shortOpts="$1"
	local longOpts="$2"
	local name="$3"
	shift 3

	if portability::have_gnu_getopt; then
		getopt --longoptions "$longOpts" --options "$shortOpts" --name "$name" -- "$@"
	else
		#shellcheck disable=SC2048,SC2086
		getopt "$shortOpts" $*
	fi
}


# Succeeds when getopt is GNU getopt. GNU getopt exits with 4 when asked
# whether it's GNU getopt; BSD getopt rejects the option instead.
portability::have_gnu_getopt() {
	getopt --test > /dev/null 2>&1
	(( $? == 4 ))
}


# Runs docker compose, preferring the v2 plugin. The inventories name
# containers the way v2 does, so a v1 binary would resolve to host names that
# don't exist.
# Input:
#  $@  the arguments to pass to docker compose
portability::compose() {
	if docker compose version > /dev/null 2>&1; then
		docker compose "$@"
	elif command -v docker-compose > /dev/null; then
		docker-compose "$@"
	else
		printf 'Neither "docker compose" nor "docker-compose" is available.\n' >&2
		printf 'Install the docker compose plugin.\n' >&2
		return 1
	fi
}


# Fails when the shell is too old for the associative arrays and readarray the
# scripts use. macOS ships bash 3.2 as /bin/bash, so a newer one needs to come
# first in PATH.
# Input:
#  $1  the minimum major version of bash required
portability::require_bash() {
	local required="$1"

	if (( BASH_VERSINFO[0] < required )); then
		printf 'bash %s or later is required, but this is bash %s.\n' \
			"$required" "$BASH_VERSION" >&2

		return 1
	fi
}
