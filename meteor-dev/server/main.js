import { Meteor } from "meteor/meteor"
import { ClientsCollection } from "../api/clients/clients"
import { PlaybooksCollection } from "../api/clients/playbooks"
import "../api/clients/server/publications"
import "../api/clients/server/methods"

const yaml = require("js-yaml")
const fs = require("fs")

// const CONFIG_FILE_VAR = process.env.CONFIG_FILE || "/etc/genisys.yaml"
// export const CONFIG_FILE = yaml.load(
//   fs.readFileSync(String(CONFIG_FILE_VAR), "utf8")
// )

const temp_yaml_string = `---
ansible:
  inventory: /var/genisys/inventory
  ssh-key: /etc/genisys/ssh/id_rsa
  playbooks:
    - /etc/genisys/playbooks/firstrun.yaml
    - /etc/genisys/playbooks/script2.yaml`

export const CONFIG_FILE = yaml.load(temp_yaml_string)

Meteor.startup(() => {
  console.log("Meteor Started")

    PlaybooksCollection.dropCollectionAsync()

  CONFIG_FILE["ansible"]["playbooks"].forEach(element => {
    obj = {'playbook' : element}
    console.log(obj)
    PlaybooksCollection.insert(obj)
  });

  //   ClientsCollection.insert({ hostname: "genisys_Test", ip: "10.0.0.1" })
})
