#!/usr/bin/env bash
export CONFIG_FILE=/app/data/config.yaml
export MONGO_URL=mongodb://localhost:3000/local

sudo -E genisys server -f $CONFIG_FILE &
mongosh $MONGO_URL --eval 'while (db["ClientsCollection"].findOne() == null); console.log("Client Added")'
sudo killall genisys
exit 0
