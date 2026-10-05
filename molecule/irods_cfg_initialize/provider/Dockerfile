FROM almalinux:9

RUN dnf --assumeyes install epel-release && \
	dnf config-manager --set-enabled crb && \
	dnf --assumeyes install jq moreutils python3-dnf-plugin-versionlock python3-pip sudo && \
### Install iRODS
	rpm --import https://packages.irods.org/irods-signing-key.asc && \
	curl --silent --show-error --output /etc/yum.repos.d/renci-irods.yum.repo \
		https://packages.irods.org/renci-irods.yum.repo && \
	dnf --assumeyes makecache && \
	dnf --assumeyes install \
		irods-database-plugin-postgres-4.3.1 \
		irods-icommands-4.3.1 \
		irods-runtime-4.3.1 \
		irods-server-4.3.1 && \
	yum versionlock add \
		irods-database-plugin-postgres-4.3.1 \
		irods-icommands-4.3.1 \
		irods-runtime-4.3.1 \
		irods-server-4.3.1 && \
### Install PostgreSQL and the PostgreSQL 12 ODBC driver
	dnf --assumeyes install postgresql-contrib postgresql-server && \
	printf '%s\n' \
			'[pgdg12-archive]' \
			'name=PostgreSQL 12 RPMs for RHEL/Rocky Linux/AlmaLinux 9' \
			'baseurl=https://yum-archive.postgresql.org/12/redhat/rhel-9-x86_64' \
			'enabled=1' \
			'gpgcheck=0' \
		> /etc/yum.repos.d/pgdg-12.repo && \
	dnf --assumeyes install postgresql12-odbc && \
	printf '%s\n' \
			'[PostgreSQL]' \
			'Description = PostgreSQL 12 ODBC Driver' \
			'Driver = /usr/pgsql-12/lib/psqlodbc.so' \
			'Setup = /usr/pgsql-12/lib/psqlodbcw.so' \
		| odbcinst -i -d -r && \
	dnf clean all && \
	rm --force --recursive /var/cache/dnf

### Set up iRODS server
COPY provider/unattended_installation.json /tmp/unattended_installation.json

RUN mkdir --parents /run/postgresql && \
	chown postgres:postgres /run/postgresql && \
	sudo --login --user=postgres initdb --auth=ident && \
	sed --in-place --regexp-extended \
		's/^(host +all +all +(127\.0\.0\.1\/32|::1\/128) +)ident$/\1md5/' \
		/var/lib/pgsql/data/pg_hba.conf && \
	sudo --login --user=postgres pg_ctl start --wait && \
	sudo --login --user=postgres psql --command="CREATE USER irods WITH PASSWORD 'testpassword'" && \
	sudo --login --user=postgres psql --command='CREATE DATABASE "ICAT"' && \
	sudo --login --user=postgres psql --command='GRANT ALL PRIVILEGES ON DATABASE "ICAT" TO irods' && \
	python3 /var/lib/irods/scripts/setup_irods.py --stdout --verbose \
		--json_configuration_file=/tmp/unattended_installation.json && \
	sudo --login --user=postgres \
		psql \
			--command="UPDATE r_grid_configuration SET option_value = 'localhost' WHERE namespace = 'delay_server' AND option_name = 'leader'" \
			ICAT && \
	sudo --login --user=postgres \
		psql --command="UPDATE r_resc_main SET resc_net = 'localhost' WHERE resc_name = 'resc'" \
			ICAT && \
	sudo --login --user=postgres pg_ctl stop && \
	jq '.catalog_provider_hosts |= [ "provider.molecule" ]' /etc/irods/server_config.json \
		| sudo --user=irods sponge /etc/irods/server_config.json

RUN pip3 install jsonschema

COPY provider/irods.service /etc/systemd/system

RUN systemctl enable postgresql irods

EXPOSE 1247/tcp
EXPOSE 1248/tcp

CMD [ "/usr/sbin/init" ]
