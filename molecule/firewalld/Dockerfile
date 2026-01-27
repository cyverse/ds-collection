FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && \
	apt upgrade --yes && \
	apt install --yes python-is-python3 systemd

CMD [ "/lib/systemd/systemd" ]
