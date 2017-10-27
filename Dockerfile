FROM python:3-alpine

MAINTAINER item4

RUN apk update && apk add build-base libffi-dev libxml2-dev libxslt-dev
RUN pip install --upgrade pip setuptools wheel

COPY ./setup.py /yui/setup.py

WORKDIR /yui

RUN mkdir /yui/data
RUN pip install -e .

COPY . /yui

CMD ["yui", "run"]

VOLUME /yui/data
