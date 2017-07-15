from setuptools import find_packages, setup

install_requires = {
    # Async request
    'aiohttp >= 2.1.0',
    'cchardet >= 2.1.1',
    'aiodns >= 1.1.1',
    # CLI
    'Click >= 6.7',
    # Configuration
    'toml >= 0.9.2',
    # util
    'attrdict >= 2.0.0',
}

tests_require = {
    'pytest >= 3.1.2',
}

extras_require = {
    'tests': tests_require,
    'lint': {
        'flake8 >= 3.3.0',
        'flake8-import-order >= 0.12',
    },
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
