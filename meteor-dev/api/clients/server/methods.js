import { Meteor } from "meteor/meteor"
import { check } from "meteor/check"
import { ClientsCollection } from "../clients"
import { AnsibleCollection } from "../ansible"
import fs from "fs"
const { spawn } = require("child_process")
import { Mongo } from "meteor/mongo"

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

    // Print the output of the command as ASCII
    commandResult.stdout.on("data", function (data) {
      function hex2a(hexx) {
        var hex = hexx.toString() //force conversion
        hex = hex.replace(/\s/g, '')
        var str = ""
        for (var i = 0; i < hex.length; i += 2)
          str += String.fromCharCode(parseInt(hex.substr(i, 2), 16))
        return str
      }

      console.log("stdout", hex2a(data))
    })

    // Return error if cmd_args are invalid/formatted incorrectly
    // NOTE: This only runs on errors associated with formatting the command, 
    // if the Ansible command fails because of something like the host being 
    // unreachable this will not trigger. 
    commandResult.stderr.on("data", function (data) {
      console.error(data)
      return {
        status: 400,
        message: `${client.hostname} failed provisioning, potential formatting issue with SSH key, playbook, or client hostname`,
      }
    })

    commandResult.on("close", (code) => {
      console.log(`ansible-playbook returned exit code ${code}`)
    })

    // Update client's provisioned status
    ClientsCollection.update(
      {
        _id: clientId,
      },
      {
        $set: {
          provisioned: true,
          provisionedAt: new Date(),
        },
      }
    )
    return {
      status: 200,
      message: `${client.hostname} successfully provisioned`,
    }
  },
  "Clients.RemoveHost": function (clientId) {
    ClientsCollection.remove({ _id: clientId })
  },
  RefreshConfig: function () {},
})
