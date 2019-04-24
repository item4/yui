FROM python:3.7

MAINTAINER item4 <item4@localhost>

RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | apt-key add - \
    && sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" >> /etc/apt/sources.list.d/pgdg.list' \
    && apt-get update -q \
    && apt-get install --no-install-recommends -y \
    build-essential\
    libffi-dev\
    libxml2-dev\
    libxslt-dev\
    tzdata\
    postgresql\
    curl\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip==19.0.3 setuptools wheel

ENV HOME="/home/kazuto"

RUN groupadd --gid 1007 kirigaya && useradd --create-home --uid 1007 --gid 1007 kazuto && mkdir -p $HOME/yui/data && chown -R kazuto:kirigaya $HOME/yui
USER kazuto

ENV PATH="${HOME}/.poetry/bin:${PATH}"
ENV TZ="Asia/Seoul"

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

COPY --chown=kazuto:kirigaya ./pyproject.toml ./poetry.lock ${HOME}/yui/

WORKDIR ${HOME}/yui/

RUN poetry install --no-dev

COPY --chown=kazuto:kirigaya . ${HOME}/yui/
CMD ["yui", "run"]

VOLUME ${HOME}/yui/data
