FROM cyverse/irods:4.3.1

### Switch back to root for installation
USER root

RUN <<EOF
	apt-get update
	apt-get upgrade --yes

### Install support for UUID generation
	apt-get install --yes uuid-runtime

### Install support for periphery script
	apt-get install --yes moreutils

### Clean up installation artifacts
	apt-get clean

### Create vault base
	mkdir /irods_vault
EOF

### Install cmd scripts and config files
COPY var/lib/irods/ /var/lib/irods/
COPY etc/irods/ /etc/irods/

RUN <<EOF
	chown --recursive irods:irods /etc/irods /var/lib/irods
	chmod --recursive ug+rw /etc/irods /var/lib/irods
	chmod ug+x /var/lib/irods/irodsctl /var/lib/irods/msiExecCmd_bin/*
EOF

### Add script to handle start and stop extras
COPY periphery.sh /periphery

RUN <<EOF
	chown irods:irods /periphery
	chmod ug+x /periphery
EOF

EXPOSE 1247/tcp 1248/tcp 20000-20009/tcp 20000-20009/udp

ENV IRODS_CONTROL_PLANE_KEY=TEMPORARY__32byte_ctrl_plane_key
ENV IRODS_NEGOTIATION_KEY=TEMPORARY_32byte_negotiation_key
ENV IRODS_ZONE_KEY=TEMPORARY_zone_key

CMD [ "/periphery" ]

### Prepare onbuild instantiation logic
COPY on-build-instantiate.sh /on-build-instantiate
RUN chmod u+x /on-build-instantiate

ONBUILD ARG IRODS_CLERVER_USER=ipc_admin
ONBUILD ARG IRODS_DEFAULT_RES=CyVerseRes
ONBUILD ARG IRODS_HOST_UID
ONBUILD ARG IRODS_RES_SERVER
ONBUILD ARG IRODS_STORAGE_RES

ONBUILD RUN <<EOF
	/on-build-instantiate
	rm --force /on-build-instantiate
EOF

ONBUILD USER irods-host-user
ONBUILD ENV HOME=/var/lib/irods

ONBUILD ENV IRODS_STORAGE_RES="$IRODS_STORAGE_RES"
