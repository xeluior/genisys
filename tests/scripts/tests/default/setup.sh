#!/usr/bin/env bash
sudo useradd -d /srv/genisys -m -r -s /sbin/nologin -U genisys
sudo pip install /app/genisys-0.1.0-py3-none-any.whl
sudo genisys install --file /app/data/config.yaml
