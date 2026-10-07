#!/usr/bin/env bash
#
# Usage:
#  config.sh OS VERSION
#
# Parameter:
#  OS       The name of the operating system being configured.
#  VERSION  the major version of the OS to configure.
#
# This script configures the common ansible requirements
#
# © 2025 The Arizona Board of Regents on behalf of The University of Arizona.
# For license information, see https://cyverse.org/license.

set -o errexit -o nounset -o pipefail

main() {
	if (( $# < 1 )); then
		printf 'The OS name is required as the first argument\n' >&2
		return 1
	fi

	if (( $# < 2 )); then
		printf 'The OS version number is required as the second argument\n' >&2
		return 1
	fi

	local os="$1"
	local version="$2"

	# Install required packages
	case "$os" in
		alma)
			install_alma_packages "$version"
			;;
		ubuntu)
			install_ubuntu_packages
			;;
		*)
			printf 'The OS %s is not supported\n' "$os" >&2
			return 1
			;;
	esac

	# Remove root's password
	passwd -d root

	# Configure root ssh access without password
	ssh-keygen -q -f /etc/ssh/ssh_host_key -N '' -t rsa

	if [[ "$os" != alma && ! -e /etc/ssh/ssh_host_dsa_key ]]; then
		ssh-keygen -q -f /etc/ssh/ssh_host_dsa_key -N '' -t dsa
	fi

	if ! [[ -e /etc/ssh/ssh_host_rsa_key ]]; then
		ssh-keygen -q -f /etc/ssh/ssh_host_rsa_key -N '' -t rsa
	fi

	update_pam_sshd_config
	update_sshd_config
	mkdir --parents /var/run/sshd

	# shellcheck disable=SC2174
	mkdir --parents --mode=0700 /root/.ssh
}

# Install the required AlmaLinux packages.
install_alma_packages() {
	local version="$1"

	dnf --assumeyes install epel-release

	# EL8 calls the repository EPEL packages depend on PowerTools rather than CRB.
	if (( version == 8 )); then
		dnf config-manager --set-enabled powertools
	else
		dnf config-manager --set-enabled crb
	fi

	dnf --assumeyes install \
		ca-certificates \
		dmidecode \
		iproute \
		jq \
		openssh-clients \
		openssh-server \
		passwd \
		procps-ng \
		python3 \
		python3-dns \
		python3-dnf-plugin-versionlock \
		python3-libselinux \
		python3-pip \
		python3-requests \
		python3-virtualenv \
		sudo

	# The iRODS images' service scripts track iRODS with a lock file here, and EL9 lacks the directory.
	mkdir --parents /var/lock/subsys

	dnf clean all
	rm --force --recursive /var/cache/dnf
}

install_ubuntu_packages() {
	apt-get update
	apt-get install --yes apt-utils 2> /dev/null

	apt-get install --yes \
		ca-certificates \
		dmidecode \
		iproute2 \
		jq \
		openssh-client \
		openssh-server \
		python-is-python3 \
		python3 \
		python3-apt \
		python3-dns \
		python3-pip \
		python3-requests \
		python3-selinux \
		python3-virtualenv \
		sudo

	apt-get clean autoclean
	rm --force --recursive /var/lib/apt/lists/*
}

update_pam_sshd_config() {
	sed --in-place '1iauth	sufficient	pam_permit.so' /etc/pam.d/sshd
}

update_sshd_config() {
	cat <<'EOF' | sed --in-place  --regexp-extended --file - /etc/ssh/sshd_config
s/#?PermitRootLogin .*/PermitRootLogin yes/
s/#?PermitEmptyPasswords no/PermitEmptyPasswords yes/
EOF
}

main "$@"
