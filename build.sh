#!/usr/bin/env bash
set -e

type poetry &>/dev/null || (printf 'poetry is not installed' && exit 1)

if ! type meteor &>/dev/null; then
  if [[ -d "${HOME}/.meteor" ]]; then
    export PATH="${HOME}/.meteor:${PATH}"
  else
    printf 'meteor is not installed'
    exit 1
  fi
fi

if type nvm &>/dev/null; then
  nvm use 14
fi

cd -- 'meteor-dev/'
meteor npm install
meteor build '../genisys/server/external'

cd -- '..'
poetry build
