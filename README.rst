YUI
===

.. image:: https://github.com/item4/yui/workflows/CI/badge.svg
   :alt: CI Status

.. image:: https://codecov.io/gh/item4/yui/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/item4/yui
   :alt: Code Coverage Status

YUI는 다용도 Slack App 입니다.


실행 요구사항
------------

- Git
- Slack App 설치 및 App Token/Bot Token
- Python 3.11.0 혹은 그 이상 버전
- PostgresSQL
- memcached
- Poetry_ 1.2 이상


.. _Poetry: https://python-poetry.org/


설치
------

.. code-block:: bash

   $ git clone https://github.com/item4/yui.git
   $ cd yui
   $ mkdir log
   $ poetry install


설정
-------------

YUI를 실행하기 위해서는 ``~~~.config.toml`` 형식의 파일명을 가진 설정용 toml 파일이 필요합니다.

필요한 설정은 다음과 같습니다.

APP_TOKEN
  ``str``. Slack App Token 입니다.
  앱 설정 페이지 좌측 메뉴에서 ``Settings`` → ``Basic Information`` 페이지에서 ``App-Level Tokens`` 하단의 버튼을 눌러 생성할 수 있습니다.
  해당 토큰에는 ``connections:write`` scope를 반드시 포함해서 생성해야합니다.

  **해당 토큰의 내용은 공개 GitHub 저장소 등의 다른 사람이 볼 수 있는 곳에 올려지면 안 됩니다.**

BOT_TOKEN
  ``str``. Yui App에게 할당된 Bot Token입니다.
  앱 설정 페이지 좌측 메뉴에서 ``Features`` → ``OAuth & Permissions`` 페이지에서 ``OAuth Tokens for Your Workspace`` 단락 아래에서 ``Bot User OAuth Token`` 을 복사해서 사용할 수 있습니다.

  **해당 토큰의 내용은 공개 GitHub 저장소 등의 다른 사람이 볼 수 있는 곳에 올려지면 안 됩니다.**

PREFIX
  ``str``. Yui의 명령어를 실행할 때 사용할 명령어 접두사입니다.
  예를 들면, 명령어의 이름이 ``help`` 이고 ``PREFIX`` 값이 ``=`` 이라면 해당 명령어를 실행하려면 ``=help`` 라고 입력해야합니다.

RECEIVE_TIMEOUT
  ``int``. Slack과 Web Socket 통신시 timeout 설정값입니다.
  기본값은 ``300`` 입니다. (5분)

APPS
  ``list[str]``. Yui에서 사용할 APP 목록입니다.
  해당 목록에 추가하면 Yui가 기동되면서 자동으로 import합니다.
  정상적인 동작을 위해서는 반드시 ``yui.apps.core`` 를 추가해주세요.

  .. code-block:: toml

     APPS = [
         'yui.apps.core'
     ]

CHANNELS
  ``dict[str, str]``. 코드 내에서 사용될 채널 Alias와 매칭될 실제 채널 ID입니다.
  하나의 App을 여러 Slack Workspace에서 재사용하는 경우 유용합니다.

  For example,

  .. code-block:: toml

     [CHANNELS]
     general = 'C111111'
     do_not_use_gif = ['C222222', 'C333333']


USERS
  ``dict[str, str]``. 코드 내에서 사용될 사용자 Alias와 실제 사용자 ID입니다.
  하나의 App을 여러 Slack Workspace에서 재사용하는 경우 유용합니다.

  For example,

  .. code-block:: toml

     [USERS]
     owner = 'U1111'
     force_cleanup = ['U1111', 'U2222']

DATABASE_URL
  ``str``. SQLAlchemy를 사용하여 DB에 접속하는데에 사용됩니다.

DATABASE_ECHO
  ``bool``. ``true``로 설정하면 YUI 기동중에 발생하는 SQL을 로그에서 볼 수 있습니다.

NAVER_CLIENT_ID
  ``str``. 네이버 API 사용을 위한 클라이언트 ID 값입니다.
  다음 App이 요구합니다.
  * ``yui.apps.compute.translate``
  * ``yui.apps.search.book``
  사용을 원한다면 해당 값을 `네이버 개발자 페이지`_에서 발급받으세요.

NAVER_CLIENT_SECRET
  ``str``. 네이버 API 사용을 위한 클라이언트 비밀값입니다.

  **해당 설정의 내용은 공개 GitHub 저장소 등의 다른 사람이 볼 수 있는 곳에 올려지면 안 됩니다.**

GOOGLE_API_TOKEN
  ``str``. 구글 API 사용을 위한 API 키입니다.
  해당 값은 `Google API Console`_ 과 `활성화 설정 페이지`_ 를 이용해 생성해야합니다.

  **해당 토큰의 내용은 공개 GitHub 저장소 등의 다른 사람이 볼 수 있는 곳에 올려지면 안 됩니다.**

OPENWEATHER_API_KEY
  ``str``. OpenWeather API 사용을 위한 API 키입니다.
  해당 값은 `OpenWeather 공식 웹사이트`_에서 발급받을 수 있습니다.

  **해당 토큰의 내용은 공개 GitHub 저장소 등의 다른 사람이 볼 수 있는 곳에 올려지면 안 됩니다.**

WEBSOCKETDEBUGGERURL
  ``str``. Chrome websocket debugger URL.
  headless chrome을 통해 웹페이지에 접속해야하는 경우 사용됩니다.

  .. code-block:: toml

     WEBSOCKETDEBUGGERURL = 'http://localhost:9222/json/version'

  docker를 사용하면 편리합니다.

  .. code-block:: bash

     docker run --rm --name headless-chrome -d -p 9222:9222 --cap-add=SYS_ADMIN yukinying/chrome-headless-browser

CACHE
  캐시 설정입니다.
  기본값을 그대로 사용하셔도 되지만 기본값을 덮어쓰고 싶으신 경우 아래와 같이 재정의해주세요.

  .. code-block:: toml

     [CACHE]
     HOST = 'localhost'
     PORT = 11211
     PREFIX = 'YUI_'


LOGGING
  YUI 로깅 설정입니다.
  자세한 내용은 내부 코드를 참조해주세요.

.. _`네이버 개발자 페이지`: https://developers.naver.com
.. _`Google API Console`: https://console.developers.google.com/apis/dashboard
.. _`활성화 설정 페이지`: https://developers.google.com/maps/documentation/geocoding/start?hl=ko#get-a-key
.. _`OpenWeather 공식 웹사이트`: https://openweathermap.org/api


실행
-------

.. code-block:: bash

   $ yui run -c yui.config.toml


``YUI_CONFIG_FILE_PATH`` 환경변수를 정의하면 ``-c`` 인자를 생략할 수 있습니다.

.. code-block:: bash

   $ export YUI_CONFIG_FILE_PATH="yui.config.toml"
   $ yui run


CLI for Database
----------------

YUI의 CLI는 대부분의 Alembic_ 명령어를 지원합니다.
``revision`` 명령어를 사용한다면 ``yui revision --autogenerate -m "Test"`` 같은 형태로 사용하실 수 있습니다.

지원되는 명령어는 다음과 같습니다.

* ``revision``
* ``migrate``
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


YUI with Docker-compose
------------------------

YUI의 여러 요구사항을 docker-compose를 이용하면 간단히 관리할 수 있습니다.

1. docker와 docker-compose를 설치해주세요.
2. ``docker-compose.yml`` 파일을 만들어주세요. (내용은 예제 폴더를 참조)
3. YUI가 사용하는 이미지를 다운로드 받아주세요.

   .. code-block:: bash

      $ docker pull item4/yui
      $ docker pull postgres:14

4. 먼저 DB 컨테이너만 실행하여 사용자와 database를 생성합니다.

   .. code-block:: bash

      $ docker-compose up -d db
      $ docker-compose exec db createuser [사용자명]
      $ docker-compose exec db psql -U postgres
      # on psql console
      \password [사용자명]
      create database [DB명]

5. 위 단락에서 지정한 값을 config 파일에 반영합니다.
6. YUI를 docker-compose로 실행합니다.

   .. code-block:: bash

      $ docker-compose up -d

자세한 내용은 예제 폴더를 참조해주세요.


YUI에 코드 기여하기
-----------------

YUI는 PEP8 등의 몇가지 코드 컨벤션을 따르고 있습니다.
이를 위해서는 ``poetry install`` 이후에 반드시 추가적으로 아래와 같은 방법으로 Git Hook을 설치해주셔야합니다.

.. code-block:: bash

   $ pre-commit install


License
-------

MIT


스폰서가 되어주세요!
----------------

* `Buy Me A Coffee`_
* `Become a patron`_

.. _`Buy Me A Coffee`: https://www.buymeacoffee.com/item4
.. _`Become a patron`: https://www.patreon.com/item4
