FROM python:3.7-alpine

MAINTAINER item4

RUN apk update && apk add build-base libffi-dev libxml2-dev libxslt-dev tzdata postgresql-dev
RUN cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime
RUN echo "Asia/Seoul" > /etc/timezone
RUN pip install --upgrade pip setuptools wheel
RUN pip install pipenv

COPY ./Pipfile ./Pipfile.lock ./setup.py /yui/

WORKDIR /yui

RUN mkdir /yui/data
RUN pipenv install

COPY . /yui

CMD ["yui", "run"]

VOLUME /yui/data
