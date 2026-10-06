#!/usr/bin/env bash
#
# Usage:
#  systemd.sh SSH-UNIT
#
# Parameter:
#  SSH-UNIT  the unit that runs sshd, sshd on AlmaLinux and ssh on Ubuntu
#
# This script prepares an image to boot systemd. It enables the unit that runs sshd and masks the
# units that shouldn't run in a test container. The containers are privileged, so many of these
# would act on the host.
#
# © 2026 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

set -o errexit -o nounset -o pipefail

main() {
	if (( $# < 1 )); then
		printf 'The unit that runs sshd is required as the first argument\n' >&2
		return 1
	fi

	local sshUnit="$1"

	systemctl enable "$sshUnit"

	local maskedUnits=(
		console-getty.service
		getty.target

		# These would change host-wide kernel settings, modules, crash records, or the clock.
		systemd-binfmt.service
		systemd-modules-load.service
		systemd-pstore.service
		systemd-sysctl.service
		systemd-timesyncd.service

		# These would mount kernel file systems the containers don't need.
		dev-hugepages.mount
		proc-sys-fs-binfmt_misc.automount
		sys-fs-fuse-connections.mount
		sys-kernel-config.mount
		sys-kernel-debug.mount
		sys-kernel-tracing.mount

		# These would scrub or trim the host's file systems.
		e2scrub_all.timer
		e2scrub_reap.service
		fstrim.timer

		# Docker provides DNS.
		systemd-resolved.service

		# These would update packages or fetch news during tests.
		apt-daily-upgrade.timer
		apt-daily.timer
		dnf-makecache.timer
		motd-news.timer
	)

	# Not every unit exists on every distribution, and masking a missing one is harmless.
	systemctl mask "${maskedUnits[@]}"
}

main "$@"
