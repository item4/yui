FROM python:3.7

MAINTAINER item4

ENV HOME="/"
ENV PATH="${HOME}/.poetry/bin:${PATH}"

RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | apt-key add -
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
RUN apt-get update -q && apt-get install -y build-essential libffi-dev libxml2-dev libxslt-dev tzdata postgresql curl
RUN (echo "Asia/Seoul" | tee /etc/timezone) && dpkg-reconfigure --frontend noninteractive tzdata
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

RUN pip install --upgrade pip setuptools wheel
COPY ./pyproject.toml ./poetry.lock /yui/

WORKDIR /yui

RUN mkdir /yui/data
RUN poetry install --no-dev

COPY . /yui

CMD ["yui", "run"]

VOLUME /yui/data
