import { Meteor } from 'meteor/meteor';
import { ClientsCollection } from '../clients';
import { PlaybooksCollection } from '../playbooks';

Meteor.publish('Clients', function() {
    return ClientsCollection.find()
})

Meteor.publish('Playbooks', function() {
    return PlaybooksCollection.find()
})