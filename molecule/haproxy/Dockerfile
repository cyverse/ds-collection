FROM ubuntu:24.04

RUN apt update && \
	apt upgrade --yes && \
	apt install --yes systemd

CMD [ "/lib/systemd/systemd" ]
