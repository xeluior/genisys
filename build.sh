#!/usr/bin/env bash
set -e

type meteor &>/dev/null || (printf 'meteor is not installed' && exit 1)
type poetry &>/dev/null || (printf 'poetry is not installed' && exit 1)

if type nvm &>/dev/null; then
  nvm use 14
fi

cd -- 'meteor-dev/'
meteor npm install
meteor build '../genisys/server/external'

cd -- '..'
poetry build
