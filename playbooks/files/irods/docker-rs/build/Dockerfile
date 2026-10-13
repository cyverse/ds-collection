FROM ubuntu:22.04

ARG IRODS_HOST_UID
ARG IRODS_NETCDF_PACKAGES
ARG IRODS_SERVER_PORT_RANGE_START
ARG IRODS_SERVER_PORT_RANGE_END
ARG IRODS_VAULT_PATH
ARG IRODS_VERSION
ARG IRODS_ZONE_PORT

ENV DEBIAN_FRONTEND=noninteractive

COPY <<'EOF' /etc/timezone
America/Phoenix
EOF

COPY <<'EOF' /etc/apt/sources.list.d/renci-irods.list
deb [arch=amd64] https://packages.irods.org/apt/ jammy main
EOF

RUN <<'EOF'
	set -o errexit

# Install dependencies
	apt-get update
	apt-get install --yes apt-utils ca-certificates gnupg wget
	wget --quiet --output-document=- https://packages.irods.org/irods-signing-key.asc | apt-key add -
	apt-get update
	apt-get upgrade --yes

# Install iRODS
	if [ -z "$IRODS_VERSION" ]; then
		echo 'The IRODS_VERSION build arg is required; it comes from the .env file' >&2
		exit 1
	fi

	set -- \
		irods-icommands="$IRODS_VERSION-*" \
		irods-runtime="$IRODS_VERSION-*" \
		irods-server="$IRODS_VERSION-*" \
		irods-resource-plugin-s3="$IRODS_VERSION.*"

	# Only the word splitting of the space-separated list is wanted, not globbing.
	set -o noglob
	for pkg in $IRODS_NETCDF_PACKAGES; do
		set -- "$@" "$pkg=$IRODS_VERSION.*"
	done
	set +o noglob

	apt-get install --yes "$@"

	groupadd --non-unique --system --gid="$IRODS_HOST_UID" irods

	useradd --non-unique --system \
		--uid="$IRODS_HOST_UID" \
		--gid="$IRODS_HOST_UID" \
		--comment='iRODS Administrator (host user)' \
		--home-dir=/var/lib/irods \
		--shell=/bin/bash \
		irods

	mkdir --parents /irods_vault /etc/irods /var/lib/irods/.irods
	chown --recursive irods:irods /etc/irods /var/lib/irods

# Clean up packages
	apt-get remove --yes wget
	apt-get autoremove --yes
	apt-get clean
	rm --force --recursive /var/lib/apt/lists/* /tmp/*
EOF

VOLUME ${IRODS_VAULT_PATH}

EXPOSE ${IRODS_ZONE_PORT}/tcp 1248/tcp
EXPOSE ${IRODS_SERVER_PORT_RANGE_START}-${IRODS_SERVER_PORT_RANGE_END}/tcp
EXPOSE ${IRODS_SERVER_PORT_RANGE_START}-${IRODS_SERVER_PORT_RANGE_END}/udp

COPY --chmod=u+x entrypoint.sh .
ENTRYPOINT [ "./entrypoint.sh" ]