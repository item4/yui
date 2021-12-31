FROM python:3.10

MAINTAINER item4 <item4@localhost>

ENV HOME="/home/kazuto"
ENV TZ="Asia/Seoul"

RUN apt-get update -q \
    && apt-get install --no-install-recommends -y \
    build-essential\
    libffi-dev\
    libxml2-dev\
    libxslt-dev\
    tzdata\
    postgresql\
    postgresql-contrib\
    curl\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip setuptools wheel

RUN groupadd --gid 1007 kirigaya && useradd --create-home --uid 1007 --gid 1007 kazuto && mkdir -p $HOME/yui/data && chown -R kazuto:kirigaya $HOME
USER kazuto

COPY --chown=kazuto:kirigaya ./requirements.txt ${HOME}/yui/

WORKDIR ${HOME}/yui/

RUN pip install -r requirements.txt

COPY --chown=kazuto:kirigaya . ${HOME}/yui/
