FROM test-env-base:alma9

RUN dnf --assumeyes install python3-pip && \
	pip3 install --no-cache-dir 'moto[server]==5.0.28' && \
	dnf clean all && \
	rm --force --recursive /var/cache/dnf

COPY --chmod=a+rx s3/service.sh /service.sh

EXPOSE 5000/tcp

CMD [ "/service.sh" ]
