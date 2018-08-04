YUI
===

.. image:: https://travis-ci.org/item4/yui.svg?branch=master
   :target: https://travis-ci.org/item4/yui
   :alt: CI Test Status

.. image:: https://codecov.io/gh/item4/yui/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/item4/yui
   :alt: Code Coverage Status

.. image:: https://requires.io/github/item4/yui/requirements.svg?branch=master
   :target: https://requires.io/github/item4/yui/requirements/?branch=master
   :alt: Requirements Status

YUI is Multi-purpose Slack Bot.

Who do use YUI?
---------------

* item4(owner)'s private slack
* 9xd
* xnuk fan club
* PyJog


Requirements
------------

- Git
- Slack bot permission for bot account
- Python 3.7 or higher
- Pipenv


Installation
------------

.. code-block:: bash

   $ git clone https://github.com/item4/yui.git
   $ cd yui
   $ mkdir log
   $ pipenv install


Configuration
-------------

Yui must require ``~~~.config.toml`` file for run.
You must make config file before run.

Config key and value is below.

TOKEN
  string. Slack App Toekn

PREFIX
  string. Prefix for command.
  for example, if you set PREFIX to '=' and you want to run help command,
  you must type ``=help``

RECEIVE_TIMEOUT
  integer. timeout seconds for receiving data from Slask WebSocket.
  default is ``300`` (5min)

HANDLERS
  list of str. Python module path of handlers.
  Yui import given paths automatically.
  You must use core handlers.

  .. code-block:: toml

     HANDLERS = [
         'yui.handlers.core'
     ]

MODELS
  list of str. Python module path of ORM Models.
  Yui import given path automatically.
  You can define ORM Model with SQLAlchemy (see this_ and use ``yui.orm.Base``)

  .. warning::

     Yui **DO NOT** make table automatically.
     You must need to run ``yui migrate`` to make migration and ``yui upgrade`` to make tables.

.. _this: http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/declarative/basic_use.html


CHANNELS
  dictionary of str. Channel names used in code.
  it used for support same handler code with different server envrionment.

  For example,

  .. code-block:: toml

     [CHANNELS]
     general = '_general'
     do_not_use_gif = ['dev', '_notice']

  This config setting make you use `yui.command.C` and `yui.command.Cs` like this.

  .. code-block:: python3

     @box.comamnd('only-general', channel=only(C.general))
     async def only_general():
        # this will run only 'general'

     @box.command('gif', channel=not_(Cs.do_not_use_gif))
     async def gif():
        # this will not run at 'do_not_use_gif'

  For using yui without change codes, You must set these channel keys like it.

  .. code-block:: toml

     [CHANNELS]
     general = '_general'
     game = 'game'
     game_and_test = ['game', 'test']
     welcome = '_general'

DATABASE_URL
  string. URL to connect Database via SQLAlchemy.

DATABASE_ECHO
  bool. If you set it to true, you can see raw SQL in log

OWNER
  string. ID of owner.
  You can get ID value from `this test page`_

NAVER_CLIENT_ID
  string. ID for using Naver API.
  Yui use it for searching book.
  You might visit `Naver developer page`_

NAVER_CLIENT_SECRET
  string. SECRET Key for using Naver API.
  **Do not** upload this value on VCS.

GOOGLE_API_TOKEN
  string. API Token for using Google map API.
  You can generate this value on `Google API Console`_ and `this activation page`_
  **Do not** upload this value on VCS.

AQI_API_TOKEN
  string. API Token for using AQI API.
  You can get this value on `this request form`_
  **Do not** upload this value on VCS.

DNF_API_KEY
  string. API Key for using Neople API.
  **Do not** upload this value on VCS.

WEBSOCKETDEBUGGERURL
  string. URL of Chrome websocket debugger.
  This is using for access webpage via headless Chrome for bypass anti-DDoS tool such as CloudFlare.

  .. code-block:: toml

     WEBSOCKETDEBUGGERURL = 'http://localhost:9222/json/version'

  You can launch headless chrome by this command.

  .. code-block:: bash

     docker run --rm --name headless-chrome -d -p 9222:9222 --cap-add=SYS_ADMIN yukinying/chrome-headless-browser

LOGGING
  complex dict. Python logging config.
  You can use default setting.
  But if you want to change some value, you can override below example.

  .. code-block:: toml

      [LOGGING]
      version = 1
      disable_existing_loggers = false

      [LOGGING.formatters.brief]
      format = '%(message)s'

      [LOGGING.formatters.default]
      format = '%(asctime)s %(levelname)s %(name)s %(message)s'
      datefmt = '%Y-%m-%d %H:%M:%S'

      [LOGGING.handlers.console]
      class = 'logging.StreamHandler'
      formatter = 'brief'
      level = 'DEBUG'
      filters = []
      stream = 'ext://sys.stdout'

      [LOGGING.handlers.file]
      class = 'logging.handlers.RotatingFileHandler'
      formatter = 'default'
      level = 'WARNING'
      filename = 'log/warning.log'
      maxBytes = 102400
      backupCount = 3

      [LOGGING.loggers.yui]
      handlers = ['console', 'file']
      propagate = true
      level = 'DEBUG'

.. _`this test page`: https://api.slack.com/methods/users.info/test
.. _`Naver developer page`: https://developers.naver.com
.. _`Google API Console`: https://console.developers.google.com/apis/dashboard
.. _`this activation page`: https://developers.google.com/maps/documentation/geocoding/start?hl=ko#get-a-key
.. _`this request form`: http://aqicn.org/data-platform/token/#/


Run
---

.. code-block:: bash

   $ pipenv run yui run -c yui.config.toml


CLI for Database
----------------

Yui CLI support most of command of Alembic_\.
You can use command with ``yui`` such as ``pipenv run yui revision --autogenerate -m "Test"``.

List of commands are below.

* ``init_db``
* ``revision``
* ``migrate`` (same as ``revision`` with ``--autogenerate``
* ``edit``
* ``merge``
* ``upgrade``
* ``downgrade``
* ``show``
* ``history``
* ``heads``
* ``branches``
* ``current``
* ``stamp``

.. _Alembic: http://alembic.zzzcomputing.com/en/latest/


Yui with Docker-compose
------------------------

You can launch yui on docker-compose easily.

1. Install Docker-compose.

2. Craete ``docker-compose.yml`` file.

   .. code-block:: yml

      version: '3'
      services:
        bot_item4:
          image: item4/yui:latest
          volumes:
            - .:/yui/data
          environment:
            - YUI_CONFIG_FILE_PATH=data/yui.config.toml
          depends_on:
            - db
          links:
            - db
          command: ./data/run.sh
        db:
          image: postgres:alpine
          volumes:
            - ./postgres/data:/var/lib/postgresql/data
          environment:
            - POSTGRES_PASSWORD=MYSECRET
          healthcheck:
            test: "pg_isready -h localhost -p 5432 -q -U postgres"
            interval: 3s
            timeout: 1s
            retries: 10

3. Pull images

   .. code-block:: bash

      $ docker pull item4/yui
      $ docker pull postgres:alpine

4. Launch db container and create database

   .. code-block:: bash

      $ docker-compose up -d db
      $ docker ps  # and see container name
      $ docker exec -it <CONTAINER_NAME_HERE> psql -U postgres  # and typing create database dbname; for create db

5. Create config file with db info

6. Launch Yui

   .. code-block:: bash

      $ docker-compose up -d

You can see example files on ``example`` directory at this repo.


Contribute to YUI
-----------------

YUI must keep PEP-8 and some rules.
So you must install lint deps by ``pipenv install --dev`` and install pre-commit hook by below commands.

.. code-block:: bash

   $ mkdir -p .git/hooks/
   $ ln -s $(pwd)/hooks/pre-commit .git/hooks


License
-------

AGPLv3 or higher
