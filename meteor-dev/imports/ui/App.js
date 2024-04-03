import { Template } from "meteor/templating"
import "./App.html"
import { ClientsCollection } from "../../api/clients/clients"
import { PlaybooksCollection } from "../../api/clients/playbooks.js"
import { OutputLogsCollection } from "../../api/clients/outputLogs.js"
import { AnsibleCollection } from "../../api/clients/ansible.js"

Template.clientList.onCreated(function () {
  Meteor.subscribe("Clients")
  Meteor.subscribe("Playbooks")
  Meteor.subscribe("Ansible")
  Meteor.subscribe("OutputLogs")
})

Template.clientList.helpers({
  client: function () {
    return ClientsCollection.find({}, { sort: { createdAt: -1 } })
  },
  option: function () {
    return PlaybooksCollection.find({})
  },
  logs: function () {
    return OutputLogsCollection.find({})
  },
})

Template.clientList.events({
  "click .provision-button": function (event) {
    event.preventDefault()

    //Talk to will about the meteor way of doing this:
    const selectedOption = $(event.currentTarget)
      .closest("tr")
      .find(".form-select")
      .val()

    console.log("Selected Playbook:", selectedOption)

    Meteor.call("Clients.Provision", this._id, selectedOption, function (err, res) {
        if (err) {
          return console.error(err)
        }

        console.log("Clients.Provision Success!", res)
      }
    )
  },
  "click .delete-button": function (event) {
    event.preventDefault()

    Meteor.call("Clients.RemoveHost", this._id, function (err, res) {
      if (err) {
        return console.error(err)
      }

      console.log("Clients.RemoveHost Success!", res)
    })
  },
  "change .log-form": function (event) {

    let selectedValue = $(event.currentTarget).val()
    console.log(selectedValue)
    // Meteor.call("Logs.GetSelected", this.log)
  }
})
