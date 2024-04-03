import { PlaybooksCollection } from "../api/clients/playbooks"
import { AnsibleCollection } from "../api/clients/ansible"

const fs = require("fs")
const yaml = require("js-yaml")

const CONFIG_FILE_VAR = process.env.CONFIG_FILE || "/etc/genisys.yaml"
export const CONFIG_FILE = yaml.load(fs.readFileSync(String(CONFIG_FILE_VAR), "utf8"))

export const InitializeCollections = function() {
    console.log("Initializing Playbook Collection")
    PlaybooksCollection.dropCollectionAsync()
    AnsibleCollection.dropCollectionAsync()
  
    // Load playbooks into Mongo
    CONFIG_FILE["ansible"]["playbooks"].forEach((element) => {
      obj = { playbook: element }
      PlaybooksCollection.insert(obj)
    })
  
    // Putting ansible SSH key into mongo collection for usage on client
    if (CONFIG_FILE["ansible"]["ssh-key"])
    {
      obj = {"ssh-key": CONFIG_FILE["ansible"]["ssh-key"]}
      AnsibleCollection.insert(obj)
    }
}

export const CreateInventoryFile = function() {
    fs.access("inventory", fs.constants.F_OK, (err) => {
        if (err) {
          console.log(`inventory does not exist, creating now`)
          fs.writeFileSync("inventory", "[all_hosts]\n")
        } else {
          console.log(`inventory exists`)
        }
      })
}