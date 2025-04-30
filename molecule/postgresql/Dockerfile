FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
	apt-get install --yes apt-utils && \
	apt-get upgrade --yes && \
	apt-get install --yes python3 systemd && \
	apt-get clean
