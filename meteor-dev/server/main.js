import { Meteor } from 'meteor/meteor';
import { ClientsCollection } from '../api/clients/clients';
import '../api/clients/server/publications';
import '../api/clients/server/methods';

const yaml = require('js-yaml')
const fs = require('fs')

const CONFIG_FILE_VAR = process.env.CONFIG_FILE
export const CONFIG_FILE = yaml.load(fs.readFileSync(String(CONFIG_FILE_VAR), 'utf8'))

Meteor.startup(() => {
    console.log("Meteor Started")
});