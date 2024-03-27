import { Meteor } from "meteor/meteor"
import { check } from "meteor/check"
import { ClientsCollection } from "../clients"
import fs from "fs"

Meteor.methods({
  "Clients.Provision": function (clientId) {
    check(clientId, String)

    const client = ClientsCollection.findOne({
      _id: clientId,
    })

    if (!client) {
      throw new Meteor.Error("client-not-found", "That client doesn't exist.")
    }

    fs.access("inventory", fs.constants.F_OK, (err) => {
      if (err) {
        console.log(`inventory does not exist`)
        fs.writeFileSync("inventory", "")
      } else {
        console.log(`inventory exists`)
      }
    })

    fs.readFileSync("inventory", function (file) {
      // check if client.hostname exists in file, do nothing
      // if client.hostname is not in file, add to the end of the file and write the file out.
      console.log("file", file)
    })

    ClientsCollection.update(
      {
        _id: clientId,
      },
      {
        $set: {
          provisioned: true,
          provisionedAt: new Date(),
          // provisionedBy: Meteor.user()
        },
      }
    )
    return {
      status: 200,
      message: `${client.hostname} successfully provisioned`,
    }
  },
  TestYaml: function () {
    const exampleYaml = Assets.get("example.yml.tpl")

    const replace = {
      interface: "eth0",
      subnet: "10.0.0.0/24",
    }
    // replace {{key}} with value
    // fs.writeFile...
  },
})
