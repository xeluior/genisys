#!/usr/bin/env bash
CONFIG_FILE=/app/data/config.yaml
MONGO_URL=mongodb://localhost:3000/local

sudo genisys server -f $CONFIG_FILE &
mongosh $MONGO_URL --eval 'while (db["ClientsCollection"].findOne() == null); console.log("Client Added")'
sudo killall genisys
exit 0
