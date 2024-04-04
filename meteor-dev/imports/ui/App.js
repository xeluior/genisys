import { Template } from "meteor/templating"
import { ReactiveVar } from 'meteor/reactive-var'
import "./App.html"
import { ClientsCollection } from "../../api/clients/clients"
import { PlaybooksCollection } from "../../api/clients/playbooks.js"
import { OutputLogsCollection } from "../../api/clients/outputLogs.js"
import { AnsibleCollection } from "../../api/clients/ansible.js"

// Var that holds the currently selected log to display in the Output Log section
var currentLogReactive = new ReactiveVar("")

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
  outputLog: function () {
    return OutputLogsCollection.find({}, { sort: { timestamp: -1 } })
  },
  logText: function () {
    return currentLogReactive.get()
  }
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
    // console.log(selectedValue)
    Meteor.call("Logs.GetSelected", selectedValue, function(err, res) {
      if (err) {
        return console.error(err)
      }

      currentLogReactive.set(res)
    })
  }
})
