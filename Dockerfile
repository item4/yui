FROM python:3

MAINTAINER item4

RUN pip install --upgrade pip setuptools wheel

COPY ./setup.py /yui/setup.py

WORKDIR /yui

RUN mkdir /yui/data
RUN pip install -e .

COPY . /yui

CMD ["yui", "run"]

VOLUME /yui/data
