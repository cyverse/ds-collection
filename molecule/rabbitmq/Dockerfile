FROM ubuntu:22.04

RUN apt update && \
	apt upgrade --yes && \
	apt install --yes systemd

CMD [ "/lib/systemd/systemd" ]
