import { Meteor } from 'meteor/meteor';
import { ClientsCollection } from '../api/clients/clients';
import '../api/clients/server/publications';
import '../api/clients/server/methods';

Meteor.startup(() => {
});