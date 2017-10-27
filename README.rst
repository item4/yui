YUI
===

.. image:: https://travis-ci.org/item4/yui.svg?branch=master
   :target: https://travis-ci.org/item4/yui

YUI is Slack Bot for `item4.slack.com`_\.

.. _`item4.slack.com`: https://item4.slack.com


Requirements
------------

- Git
- Slack bot permission for bot account
- Python 3.6 or higher


Installation
------------

.. code-block:: bash

   $ git clone https://github.com/item4/yui.git
   $ cd yui
   $ mkdir log
   $ pip install -e .


Configuration
-------------

Yui must require `~~~.config.toml` file for run.
You must make config file before run.

Config key and value is below.

TOKEN
  string. Slack App Toekn

PREFIX
  string. Prefix for command.
  for example, if you set PREFIX to '=' and you want to run help command,
  you must type `=help`

HANDLERS
  list of str. Python module path of handlers.
  Yui import given paths automatically.
  You can use default command settings.

  .. code-block:: toml

     HANDLERS = [
         'yui.handlers'
     ]

MODELS
  list of str. Python module path of ORM Models.
  Yui import given path automatically.
  You can define ORM Model with SQLAlchemy (see this_ and use `yui.orm.Base`)

  .. warning::

     Yui **DO NOT** make table automatically.
     You must need to run `yui migrate` and `yui upgrade` to make table.

.. _this: http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/declarative/basic_use.html


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
  Do not upload this value on VCS.

LOGGING
  complex dict. Python logging config.
  You can use default setting.
  But if you want to change some value, you can override below example.

  .. code-block:: toml

      [LOGGING]
      version = 1

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
      maxBytes = 1024
      backupCount = 3

      [LOGGING.loggers.yui]
      handlers = ['console', 'file']
      propagate = true
      level = 'DEBUG'

.. _`this test page`: https://api.slack.com/methods/users.info/test
.. _`Naver developer page`: https://developers.naver.com


Run
---

.. code-block:: bash

   $ yui run -c yui.config.toml


CLI for Database
----------------

Yui CLI support most of command of Alembic_\.
You can use command with `yui` such as `yui revision --autogenerate -m "Test"`.

List of commands are below.

* `init_db`
* `revision`
* `migrate` (same as `revision` with `--autogenerate`
* `edit`
* `merge`
* `upgrade`
* `downgrade`
* `show`
* `history`
* `heads`
* `branches`
* `current`
* `stamp`

.. _Alembic: http://alembic.zzzcomputing.com/en/latest/


Yui on Docker
-------------

You can launch yui on docker.

.. code-block:: bash

   $ pwd
   /home/item4/
   $ mkdir yui
   $ cd yui
   $ vi my.config.toml
   $ docker pull item4/yui
   $ docker run --rm -v /home/item4/yui:/yui/data item4/yui yui upgrade head -c data/my.config.toml
   $ docker run -d --name my-yui -v /home/item4/yui:/yui/data item4/yui yui run -c my.config.toml


If you finished above lines, you can launch yui simply with this command.

.. code-block:: bash

   $ docker start my-yui


Contribute to YUI
-----------------

.. code-block:: bash

   $ mkdir -p .git/hooks/
   $ ln -s $(pwd)/hooks/pre-commit .git/hooks


License
-------

AGPLv3 or higher
