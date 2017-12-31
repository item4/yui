from setuptools import find_packages, setup

install_requires = [
    # Async request
    'aiohttp ~= 2.3.5',
    'cchardet ~= 2.1.1',
    'aiodns ~= 1.1.1',
    # Async util
    'async-timeout ~= 2.0.0',
    # Database
    'SQLAlchemy ~= 1.1.15',
    'sqlalchemy-utils ~= 0.32.21',
    'alembic ~= 0.9.6',
    # CLI
    'Click ~= 6.7',
    # Configuration
    'toml ~= 0.9.3',
    # Crontab
    'aiocron ~= 1.1',
    # Fuzzy Search
    'fuzzywuzzy[speedup] ~= 0.15.1',
    # HTML
    'lxml ~= 4.1.1',
    'cssselect ~= 1.0.1',
    # i18n
    'babel ~= 2.5.1',
    # JSON
    'ujson ~= 1.35',
    # RSS
    'libearth ~= 0.3.3',
    # util
    'attrdict ~= 2.0.0',
    'pytz ~= 2017.3',
]

tests_require = [
    'mypy ~= 0.550',
    'pytest ~= 3.3.0',
    'pytest-asyncio ~= 0.8.0',
    'pytest-cov ~= 2.5.1',
    'mocket ~= 2.1.1',
]

extras_require = {
    'tests': tests_require,
    'lint': [
        'flake8 ~= 3.5.0',
        'flake8-import-order ~= 0.15',
    ],
    'ci': [
        'codecov ~= 2.0.9',
    ]
}

setup(
    name='yui',
    version='0.0.0',
    description='Slack Bot for item4.slack.com',
    url='https://item4.slack.com',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'yui=yui.cli:main',
        ],
    }
)
