import { Template } from 'meteor/templating';
import { TasksCollection } from "../api/TasksCollection";
import './App.html';

Template.mainContainer.helpers({
  tasks() {
    Meteor.subscribe("tasks")
    let result = TasksCollection.find({})
    
    return result
  },
});