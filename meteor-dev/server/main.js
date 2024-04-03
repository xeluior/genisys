import { Meteor } from "meteor/meteor"
import "../api/clients/server/publications"
import "../api/clients/server/methods"
import { InitializeCollections, CreateInventoryFile } from "./serverMethods"
const yaml = require("js-yaml")



// const temp_yaml_string = `---
// ansible:
//   inventory: /var/genisys/inventory
//   ssh-key: /etc/genisys/ssh/id_rsa
//   playbooks:
//     - /etc/genisys/playbooks/firstrun.yaml
//     - /etc/genisys/playbooks/script2.yaml`

// export const CONFIG_FILE = yaml.load(temp_yaml_string)

Meteor.startup(() => {
  console.log("Meteor Started")

  InitializeCollections()
  CreateInventoryFile()
})
