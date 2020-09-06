#!/usr/bin/env bash
if [ "${TRAVIS_BRANCH}" = "main" ] && [ "${TRAVIS_PULL_REQUEST}" = false ]; then
    docker push item4/yui:latest
fi
