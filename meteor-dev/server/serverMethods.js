import { PlaybooksCollection } from "../api/clients/playbooks"
import { AnsibleCollection } from "../api/clients/ansible"

const fs = require("fs")
const yaml = require("js-yaml")

export const CONFIG_FILE_VAR = process.env.CONFIG_FILE || "/etc/genisys.yaml"


// const temp_yaml_string = `---
// ansible:
//   inventory: /var/genisys/inventory
//   ssh-key: /etc/genisys/ssh/id_rsa
//   playbooks:
//     - /etc/genisys/playbooks/firstrun.yaml
//     - /etc/genisys/playbooks/script2.yaml`

// export const CONFIG_FILE = yaml.load(temp_yaml_string)

export const InitializeCollections = async function () {
  console.log("Initializing Playbook Collection")
  const CONFIG_FILE = yaml.load(fs.readFileSync(String(CONFIG_FILE_VAR), "utf8"))

  PlaybooksCollection.dropCollectionAsync()
  AnsibleCollection.dropCollectionAsync()

  // Load playbooks into Mongo
  CONFIG_FILE["ansible"]["playbooks"].forEach((element) => {
    obj = { playbook: element }
    PlaybooksCollection.insert(obj)
  })

  // Putting ansible SSH key location into mongo collection for usage on client
  if (CONFIG_FILE["ansible"]["ssh-key"]) {
    obj = { "ssh-key": CONFIG_FILE["ansible"]["ssh-key"] }
    AnsibleCollection.insert(obj)
  }
}

export const CreateInventoryFile = function () {
  inv = 'inventory'

  fs.access(inv, fs.constants.F_OK, (err) => {
    if (err) {
      console.log(`${inv} does not exist, creating now`)
      fs.writeFileSync(inv, "[all_hosts]\n")
      return
    } 
    console.log(`inventory \"${inv}\" exists`)
    
  })

  return inv
}
