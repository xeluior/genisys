import { Template } from 'meteor/templating';
import './App.html';
import { ClientsCollection } from '../../api/clients/clients';

Template.clientList.onCreated(function(){
  Meteor.subscribe("Clients");
});

Template.clientList.helpers({
  client: function(){
    return ClientsCollection.find({}, {sort: { createdAt: -1}});
  },
  provisionedClients: function(){
    return ClientsCollection.find({provisioned: true}, {sort: { createdAt: -1}});
  }
});

Template.clientList.events({
  "click .provision-button": function(event) {
    event.preventDefault();

    console.log("Hostname:", this.hostname);

    Meteor.call('Clients.Provision', this._id, function(err, res){
      if(err){
        return console.error(err);
      }

      console.log('Success!', res);
    });
  }
});