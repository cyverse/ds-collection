#!/usr/bin/env bash
#
# Helpers for the scripts that run a batch of tests and report which passed.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

# Prints how many tests passed, followed by the name of each one that failed.
# Input:
#  $1     the plural noun naming the tests, e.g., scenarios
#  $2     the number of tests run
#  $3...  the names of the tests that failed
results::print_summary() {
	local noun="$1"
	local total="$2"
	shift 2
	local failed=("$@")

	printf '\n%d of %d %s passed\n' $(( total - ${#failed[@]} )) "$total" "$noun"

	local name
	for name in ${failed[@]+"${failed[@]}"}; do
		printf 'FAILED %s\n' "$name"
	done
}
