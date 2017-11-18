#!/usr/bin/env bash
if [ "${TRAVIS_BRANCH}" = "master" ] && [ "${TRAVIS_PULL_REQUEST}" = false ]; then
    docker push item4/yui:latest
fi
