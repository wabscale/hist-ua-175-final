FROM python:3.9-alpine

VOLUME /opt/app
WORKDIR /opt/app

COPY requirements.txt requirements.txt
RUN apk --update --no-cache add alpine-sdk libffi-dev \
  && pip3 install -r requirements.txt \
  && adduser -D -u 1000 jc

USER jc
CMD jupyterlab --host 0.0.0.0
