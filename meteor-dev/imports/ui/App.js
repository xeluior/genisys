import { Template } from "meteor/templating"
import "./App.html"
import { ClientsCollection } from "../../api/clients/clients"
import { PlaybooksCollection } from "../../api/clients/playbooks.js"

Template.clientList.onCreated(function () {
  Meteor.subscribe("Clients")
  Meteor.subscribe("Playbooks")
})

Template.clientList.helpers({
  client: function () {
    return ClientsCollection.find({}, { sort: { createdAt: -1 } })
  },
  provisionedClients: function () {
    return ClientsCollection.find(
      { provisioned: true },
      { sort: { createdAt: -1 } }
    )
  },
  option: function() {
    return PlaybooksCollection.find({})
  }
})

Template.clientList.events({
  "click .provision-button": function (event) {
    event.preventDefault()

    //Talk to will about the meteor way of doing this:
    const selectedOption = $(event.currentTarget).closest('tr').find('.form-select').val();

    console.log("Selected Playbook:", selectedOption)

    Meteor.call("Clients.Provision", this._id, selectedOption, function (err, res) {
      if (err) {
        return console.error(err)
      }

      console.log("Success!", res)
    })
  },
})
