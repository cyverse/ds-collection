FROM test-env-base:alma9

RUN pip3 install --no-cache-dir 'moto[server]==5.0.28'

COPY --chmod=a+rx s3/service /service

EXPOSE 5000/tcp

CMD [ "/service" ]
