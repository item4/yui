YUI
===

YUI is Slack Bot for `item4.slack.com`_\.

.. _`item4.slack.com`: https://item4.slack.com


Requirements
------------

- Git
- Slack bot permission for bot account
- Python 3.6 or higher
- Linux OS (can not use in Windows)


Installation
------------

.. code-block:: bash

   $ git clone https://github.com/item4/yui.git
   $ cd yui
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


.. _`this test page`: https://api.slack.com/methods/users.info/test


Run
---

.. code-block:: bash

   $ yui run -c yui.config.toml


CLI for Database
----------------

Yui CLI support most of command of Alembic_.
You can use command with `yui` such as `yui revision --autogenerate -m "Test"`.


Contribute to YUI
-----------------

.. code-block:: bash

   $ mkdir -p .git/hooks/
   $ ln -s $(pwd)/hooks/pre-commit .git/hooks


License
-------

AGPLv3 or higher
