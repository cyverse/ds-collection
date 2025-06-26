FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

COPY provider/apt.irods /etc/apt/preferences.d/irods

RUN apt update && \
	apt --yes install apt-utils && \
	apt --yes install \
		ca-certificates jq lsb-release moreutils python-is-python3 python3-pip systemd wget && \
### Install iRODS
	wget --output-document=/etc/apt/trusted.gpg.d/irods-signing-key.asc \
		https://packages.irods.org/irods-signing-key.asc && \
	echo deb [arch=amd64] https://packages.irods.org/apt/ "$(lsb_release --codename --short)" main \
		> /etc/apt/sources.list.d/renci-irods.list && \
	apt update && \
	apt --yes install irods-database-plugin-postgres irods-server && \
### Install PostgreSQL
	apt-get --yes install postgresql postgresql-contrib && \
	apt-get clean

### Set up iRODS server
COPY provider/unattended_installation.json /tmp/unattended_installation.json

RUN sudo --login --user=postgres \
		/usr/lib/postgresql/14/bin/pg_ctl \
			--log=/var/log/postgresql/postgresql-14-main.log \
			--options='--config_file=/etc/postgresql/14/main/postgresql.conf' \
			--pgdata=/var/lib/postgresql/14/main \
			start && \
	sudo --user=postgres psql --command="CREATE USER irods WITH PASSWORD 'testpassword'" && \
	sudo --user=postgres psql --command='CREATE DATABASE "ICAT"' && \
	sudo --user=postgres psql --command='GRANT ALL PRIVILEGES ON DATABASE "ICAT" TO irods' && \
	python /var/lib/irods/scripts/setup_irods.py --stdout --verbose \
		--json_configuration_file=/tmp/unattended_installation.json && \
	sudo --login --user=postgres \
		psql \
			--command="UPDATE r_grid_configuration SET option_value = 'localhost' WHERE namespace = 'delay_server' AND option_name = 'leader'" \
			ICAT && \
	sudo --login --user=postgres \
		psql --command="UPDATE r_resc_main SET resc_net = 'localhost' WHERE resc_name = 'resc'" \
			ICAT && \
	sudo --login --user=postgres \
		/usr/lib/postgresql/14/bin/pg_ctl --pgdata=/var/lib/postgresql/14/main stop && \
	jq '.catalog_provider_hosts |= [ "provider.molecule" ]' /etc/irods/server_config.json \
		| sudo --user=irods sponge /etc/irods/server_config.json

RUN pip install jsonschema

COPY provider/irods.service /etc/systemd/system

RUN systemctl enable irods

EXPOSE 1247/tcp
EXPOSE 1248/tcp

CMD [ "/lib/systemd/systemd" ]