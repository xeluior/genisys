#!/usr/bin/env bash
CONFIG_FILE=/app/data/config.yaml
MONGO_URL=mongodb://localhost:3000/local
SRV_USR=genisys
SRV_DIR=/var/$SRV_USR
HOSTS=$SRV_DIR/hosts.json

sudo useradd -d $SRV_DIR -m -r -s /sbin/nologin -G vboxsf $SRV_USR
sudo pip install /app/genisys-0.1.0-py3-none-any.whl
sudo genisys install --file $CONFIG_FILE
sudo touch $HOSTS
sudo chown $SRV_USR:$SRV_USR $HOSTS
