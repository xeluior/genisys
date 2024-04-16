import { Meteor } from "meteor/meteor"
import "../api/clients/server/publications"
import "../api/clients/server/methods"
import { InitializeCollections, CreateInventoryFile } from "./serverMethods"
import { CONFIG_FILE_VAR } from "./serverMethods"
import fs from "fs"

const TESTING_MODE = process.env.GITHUB_RUNNER || false

Meteor.startup(() => {
  console.log("Meteor Started")
  
  Meteor.call("RefreshConfig")
  CreateInventoryFile()

  fs.watchFile(CONFIG_FILE_VAR, Meteor.bindEnvironment(() => {Meteor.call("RefreshConfig")}))


  //TESTING CODE THAT IS MEANT TO ERROR:
  Meteor.call("FAKE_METHOD")

  if(TESTING_MODE.localeCompare('True') === 0)
  {
    console.log("Server launched in testing mode, exiting now.")
    exit(0)
  }
})
