import { Meteor } from "meteor/meteor"
import "../api/clients/server/publications"
import "../api/clients/server/methods"
import { InitializeCollections, CreateInventoryFile } from "./serverMethods"
import { CONFIG_FILE_VAR } from "./serverMethods"
import fs from "fs"

Meteor.startup(() => {
  console.log("Meteor Started")
  
  Meteor.call("FunctionThatDoesNotExist")

  Meteor.call("RefreshConfig")
  CreateInventoryFile()

  fs.watchFile(CONFIG_FILE_VAR, Meteor.bindEnvironment(() => {Meteor.call("RefreshConfig")}))
})
