import { Template } from 'meteor/templating';
import { ClientsCollection } from "../api/ClientsCollection";
import './App.html';

Template.dynamicTable.helpers({
  tableHeaders() {
    Meteor.subscribe("tasks")
    // Assuming the first document in the collection contains all possible keys
    const firstDocument = ClientsCollection.findOne();
    if (firstDocument) {
      let keys = Object.keys(firstDocument)
      return keys; 
    }
    return [];
  },
  tableRows() {
    Meteor.subscribe("tasks")
    doc = ClientsCollection.find({}).fetch()
    let arr = [];

    for(let i = 0; i < doc.length; i++)
    {
      arr[i] = (Object.values(doc[i]))
    }

    return arr
  },
});

Template.dynamicTable.events({
  "click .provision-button"(event) {
    event.preventDefault()

    console.log("Pressed")
  }
})