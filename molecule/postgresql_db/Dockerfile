FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG LC_COLLATE=C

RUN apt-get update && \
	apt-get install --yes apt-utils && \
	apt-get upgrade --yes && \
	apt-get install --yes locales && \
	locale-gen en_US.UTF-8 && \
	apt-get install --yes postgresql python3 sudo && \
	apt-get clean autoclean && \
	rm --force --recursive /var/lib/apt/lists/*
