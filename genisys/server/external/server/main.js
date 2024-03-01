import { Meteor } from 'meteor/meteor';
import { ClientsCollection } from '/imports/api/ClientsCollection';
import yaml from 'js-yaml'
import fs from 'fs'
import path from 'path'

const insertClient = client => ClientsCollection.insert(client);

Meteor.publish("tasks", () => {
  return ClientsCollection.find()
})

Meteor.startup(() => {
  // Inserting dummy data for testing
  if (ClientsCollection.find().count() === 0) {
    [
      {
        "hostname": "genisys1",
        "ip": "127.0.0.1",
        "key": "val",
        "key2": "val2"
      },
      {
        "hostname": "genisys2",
        "ip": "127.0.0.1",
        "key": "val",
        "key2": "val2"
      },
      {
        "hostname": "genisys3",
        "ip": "127.0.0.1",
        "key": "val",
        "key2": "val2"
      },
      {
        "hostname": "genisys4",
        "ip": "127.0.0.1",
        "key": "val",
        "key2": "val2"
      }
    ].forEach(insertClient)
  }
  // Grabbing config file 

  console.log(path.resolve(process.cwd())) 

  const yamlPath = path.join(__dirname, '..', '..', '..', '..', 'documentation', 'example.yml');
  const doc = yaml.load(fs.readFileSync(yamlPath, 'utf8'))

  console.log(doc)

});