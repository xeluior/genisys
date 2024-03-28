import { Meteor } from "meteor/meteor"
import { check } from "meteor/check"
import { ClientsCollection } from "../clients"
import fs from "fs"
const { exec } = require('child_process')
Meteor.methods({
  "Clients.Provision": function (clientId, playbook) {
    check(clientId, String)

    const client = ClientsCollection.findOne({
      _id: clientId,
    })

    if (!client) {
      throw new Meteor.Error("client-not-found", "That client doesn't exist.")
    }

    fs.access("inventory", fs.constants.F_OK, (err) => {
      if (err) {
        console.log(`inventory does not exist, creating now`)
        fs.writeFileSync("inventory", "")
      } else {
        console.log(`inventory exists`)
      }
    })

    // Reading inventory file and adding hostname to inventory file
    fs.readFile('inventory', 'utf8', function (err, fileContent) {
        if (err) {
            console.error(`Error reading file: ${err}`);
            return;
        }
    
        // Check if the hostname
        if (fileContent.includes(client.hostname)) {
            console.log(`${client.hostname} already exists in the file.`);
        } else {
            // If 'client' is not in the file, add it to the end of the file
            fileContent += `${client.hostname}\n`;
    
            // Write the modified content back to the file
            fs.writeFile('inventory', fileContent, 'utf8', function (err) {
                if (err) {
                    console.error(`Error writing to file: ${err}`);
                    return;
                }
                console.log(`${client.hostname} added to the file.`);
                console.log(`Content of file: ${fileContent}`)
            });
        }
    });

    // Running Ansible command
    const command = `ansible-playbook -i inventory ${playbook} --limit ${client.hostname}`
    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing command: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Command stderr: ${stderr}`);
            return;
        }
        console.log(`Command stdout: ${stdout}`);
    });

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
  }
})
