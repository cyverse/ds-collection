FROM almalinux:9

RUN dnf --assumeyes install epel-release && \
	dnf config-manager --set-enabled crb && \
	dnf --assumeyes install \
		chkconfig \
		iproute \
		procps-ng \
		python3 \
		python3-dnf-plugin-versionlock \
		python3-pip \
		sudo && \
	dnf clean all && \
	rm --force --recursive /var/cache/dnf
