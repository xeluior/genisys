import { Meteor } from "meteor/meteor"
import { check } from "meteor/check"
import { ClientsCollection } from "../clients"
import { AnsibleCollection } from "../ansible"
import { OutputLogsCollection } from "../outputLogs"
const { spawn } = require("child_process")
import fs from "fs"
const yaml = require("js-yaml")
import { CONFIG_FILE_VAR } from "../../../server/serverMethods"
import { PlaybooksCollection } from "../playbooks"

Meteor.methods({
  "Clients.Provision": function (clientId, playbook) {
    // check(clientId, Mongo.ObjectID)

    // Find client in MongoDB
    const client = ClientsCollection.findOne({
      _id: clientId,
    })

    // Check if client exists
    if (!client) {
      throw new Meteor.Error("client-not-found", "That client doesn't exist.")
    }

    // Check if playbook as been selected
    if (playbook.localeCompare("None") === 0) {
      throw new Meteor.Error(
        "invalid-playbook",
        "Please select a playbook to run."
      )
    }

    // Reading inventory file and adding hostname to inventory file
    fs.readFile("inventory", "utf8", function (err, fileContent) {
      if (err) {
        console.error(`Error reading file: ${err}`)
        return
      }

      // Check if the hostname is in the file
      if (fileContent.includes(client.hostname)) {
        console.log(`${client.hostname} already exists in the file.`)
      } else {
        // If 'client.hostname' is not in the file, add it to the end of the file
        fileContent += `${client.hostname} ansible_host=${client.ip}\n`

        // Write the modified content back to the file
        fs.writeFile("inventory", fileContent, "utf8", function (err) {
          if (err) {
            console.error(`Error writing to file: ${err}`)
            return
          }
          console.log(`${client.hostname} added to the file.`)
          console.log(`Content of file: ${fileContent}`)
        })
      }
    })

    // Building Ansible command
    let command = "ansible-playbook"
    let cmd_args = [
      `-i`,
      `inventory`,
      `${playbook}`,
      `--limit`,
      `${client.hostname}`,
      `--ssh-common-args`,
      `'-o StrictHostKeyChecking=no'`,
      `--user`,
      `root`,
    ]

    // If SSH key found, append to command
    const ansibleObject = AnsibleCollection.findOne({
      "ssh-key": { $exists: true },
    })
    if (ansibleObject) {
      cmd_args.push(`--private-key`, `${ansibleObject["ssh-key"]}`)
    }

    // Run the command
    const commandResult = spawn(command, cmd_args)

    let cmd_result = ""
    // Print the output of the command as ASCII and log output in MongoDB
    commandResult.stdout.on("data", function (data) {
      function hexBufferToString(buffer) {
        const hexString = buffer.toString("hex")
        const hexPairs = hexString.match(/.{1,2}/g)
        const asciiString = hexPairs
          .map((hex) => String.fromCharCode(parseInt(hex, 16)))
          .join("")
        return asciiString
      }
      res = hexBufferToString(data)

      cmd_result += res
    })

    // Return error if cmd_args are invalid/formatted incorrectly
    // NOTE: This only runs on errors associated with formatting the command,
    // if the Ansible command fails because of something like the host being
    // unreachable this will not trigger.
    commandResult.stderr.on("data", function (data) {
      console.error(data)
      return {
        status: 400,
        message: `${client.hostname} failed provisioning due to command error, potential formatting issue with SSH key, playbook, or client hostname`,
      }
    })

    commandResult.on(
      "close",
      Meteor.bindEnvironment((code) => {
        console.log(`ansible-playbook returned exit code ${code}`)

        playbookTimestamp = new Date().getTime()
        logLabel = `${client.hostname}-${playbook}-${playbookTimestamp}`

        // Insert log into mongodb
        OutputLogsCollection.insert({
          label: logLabel,
          text: cmd_result,
          timestamp: playbookTimestamp,
        })
        console.log("Logged:\n", cmd_result, "\nas:", logLabel)

        if (code !== 0) {
          return {
            status: 400,
            message: `Ansible returned exit code ${code} while provisioning ${client.hostname}. Please see output log ${logLabel} on web UI for details.`,
          }
        }
      })
    )

    return {
      status: 200,
      message: `${client.hostname} successfully provisioned`,
    }
  },
  "Clients.RemoveHost": function (clientId) {
    toDelete = ClientsCollection.findOne({ _id: clientId })

    if (!toDelete) {
      throw new Meteor.Error("client-not-found", "That client doesn't exist.")
    }
    ClientsCollection.remove(toDelete)
    return {
      status: 200,
      message: 'Client successfully deleted.'
    }
  },
  "Logs.GetSelected": function (logLabel) {
    const log = OutputLogsCollection.findOne({ label: logLabel })

    if (!log) {
      return ""
    }

    return log.text
  },
  "RefreshConfig": async function () {
    console.log("Loading Playbook Collection")
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
  },
})
