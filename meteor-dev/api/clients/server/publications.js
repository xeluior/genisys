import { Meteor } from 'meteor/meteor';
import { ClientsCollection } from '../clients';

Meteor.publish('Clients', function() {
    return ClientsCollection.find()
})