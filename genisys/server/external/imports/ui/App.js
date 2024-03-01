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
    event.preventDefault();

    // Find the closest row (tr element) to the clicked button
    const row = $(event.target).closest("tr");

    // Find the IP address in the same row
    const ipAddress = row.find("td:nth-child(3)").text(); // Assuming IP address is in the 3rd column (index 2)

    console.log("IP Address:", ipAddress);
  }
});