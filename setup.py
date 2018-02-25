from setuptools import find_packages, setup

setup(
    name='yui',
    version='0.0.0',
    description='Slack Bot for item4.slack.com',
    url='https://item4.slack.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'yui=yui.cli:main',
        ],
    }
)
