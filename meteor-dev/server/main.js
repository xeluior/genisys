import { Meteor } from "meteor/meteor"
import "../api/clients/server/publications"
import "../api/clients/server/methods"
import { InitializeCollections, CreateInventoryFile } from "./serverMethods"

Meteor.startup(() => {
  console.log("Meteor Started")

  InitializeCollections()
  CreateInventoryFile()
})
