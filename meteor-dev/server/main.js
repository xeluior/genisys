import { Meteor } from "meteor/meteor"
import { ClientsCollection } from "../api/clients/clients"
import "../api/clients/server/publications"
import "../api/clients/server/methods"

const yaml = require("js-yaml")
const fs = require("fs")

const CONFIG_FILE_VAR = process.env.CONFIG_FILE || "/etc/genisys.yaml"
export const CONFIG_FILE = yaml.load(
  fs.readFileSync(String(CONFIG_FILE_VAR), "utf8")
)

Meteor.startup(() => {
  console.log("Meteor Started")

  // Inserting dummy data for testing
  if (process.env.NODE_ENV === "development") {
    ClientsCollection.insert([
      { hostname: "genisys0001", ip: "10.0.0.1" },
      { hostname: "genisys0002", ip: "10.0.0.10" },
      { hostname: "genisys0003", ip: "10.0.0.20" },
    ])
  }
})
