#!/usr/bin/env bash
#
# Usage:
#  test-playbook INSPECT PRETTY VERBOSE HOSTS SETUP PLAYBOOK
#
# Parameters:
#  HOSTS     the inventory hosts to test against
#  INSPECT   if this is set to any value, a shell will be opened that allows
#            access to the volumes in the env containers.
#  PLAYBOOK  the name of the playbook being tested.
#  PRETTY    if this is set to any value, more info is dumped and newlines in
#            output are expanded.
#  SETUP     a comma-separated list of playbooks to be run, in order, prior to
#            the playbook under test PLAYBOOK
#  VERBOSE   if this is set to any value, ansible will be passed the verbose
#            flag -vvv
#
# This program executes and ansible playbook on the test environment.
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

set -o errexit -o nounset -o pipefail

readonly PLAYBOOK_DIR=/playbooks-under-test
readonly LIBRARY_DIR="$PLAYBOOK_DIR"/library
readonly TEST_DIR="$PLAYBOOK_DIR"/tests

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly NORMAL='\033[0m'

main() {
	local inspect="$1"
	local pretty="$2"
	local verbose="$3"
	local hosts="$4"
	local setup="$5"
	local playbook="$6"

	local inventory=/inventory/"$hosts"

	if [[ -n "$pretty" ]]; then
		export ANSIBLE_STDOUT_CALLBACK=minimal
	fi

	# add the option for module-path only if a library directory exists
	local modPath=
	if [[ -d "$LIBRARY_DIR" ]]; then
		modPath="$LIBRARY_DIR"
	fi

	local rc=0

	if ! wait_for_env "$inventory"; then
		display_failure 'ERROR: The environment did not come up'
		rc=1
	fi

	if (( rc == 0 )) && [[ -n "$setup" ]]; then
		if ! setup_env "$verbose" "$inventory" "$modPath" "$setup"; then
			display_failure 'ERROR: One of the setup playbooks failed'
			rc=1
		fi
	fi

	if (( rc == 0 )) && [[ -n "$playbook" ]]; then
		if ! do_test "$verbose" "$inventory" "$modPath" "$playbook"; then
			display_failure FAILED
			rc=1
		else
			display_success PASSED
		fi
	fi

	if [[ -n "$inspect" ]]; then
		printf 'opening shell for inspection of volumes\n'
		bash
	fi || true

	return $rc
}

display_failure() {
	local msg="$1"

	printf "$RED"'%s'"$NORMAL"'\n' "$msg"
}

display_success() {
	local msg="$1"

	printf "$GREEN"'%s'"$NORMAL"'\n' "$msg"
}

do_test() {
	local verbose="$1"
	local inventory="$2"
	local modPath="$3"
	local playbook="$4"

	local args=(--inventory-file="$inventory" --module-path="$modPath")

	local pbPath="$PLAYBOOK_DIR"/"$playbook"

	printf 'checking playbook syntax\n'
	if ! ansible-playbook --syntax-check "${args[@]}" "$pbPath"
	then
		return 1
	fi

	if [[ -n "$verbose" ]]
	then
		args+=(-vvv)
	fi

	printf 'running playbook\n'
	if ! ansible-playbook --skip-tags=no_testing "${args[@]}" "$pbPath"
	then
		return 1
	fi

	local testPath="$TEST_DIR"/"$playbook"

	if [[ -e "$testPath" ]]; then
		printf 'testing configuration\n'
		# shellcheck disable=SC2086
		if ! ansible-playbook "${args[@]}" "$testPath"
		then
			return 1
		fi
	fi

	printf 'checking idempotency\n'

	local idempotencyRes
	idempotencyRes="$(run_idempotency "$inventory" "$modPath" "$playbook")"

	if grep --quiet --regexp '^\(changed\|fatal\):' <<< "$idempotencyRes"; then
		echo "$idempotencyRes"
		printf 'failed: idempotency check\n'
		return 1
	else
		printf 'ok: idempotency check\n'
	fi
}

run_idempotency() {
	local inventory="$1"
	local modPath="$2"
	local playbook="$3"

	ansible-playbook \
			--inventory-file="$inventory" \
			--module-path="$modPath" \
			--skip-tags='no_testing, non_idempotent' \
			"$PLAYBOOK_DIR"/"$playbook" \
		2>&1
}

setup_env() {
	local verbose="$1"
	local inventory="$2"
	local modPath="$3"
	local setup="$4"

	local args=(--inventory-file="$inventory" --skip-tags=no_testing)

	if [[ -n "$verbose" ]]
	then
		args+=(-vvv)
	fi

	local setupArray
	IFS=, read -r -a setupArray <<< "$setup"

	local playbook
	for playbook in "${setupArray[@]}"
	do
		args+=("$PLAYBOOK_DIR"/"$playbook")
	done

	printf 'preparing environment for testing playbook\n'
	ansible-playbook "${args[@]}"
}

wait_for_env() {
	local inventory="$1"
	local output

	printf 'waiting for environment to be ready\n'
	if ! output="$(ansible-playbook --inventory-file="$inventory" /wait-for-ready.yml)"; then
		printf 'failed to bring up the environment\n%s' "$output"
		return 1
	fi
}

main "$@"
