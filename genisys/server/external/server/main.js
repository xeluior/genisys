import { Meteor } from 'meteor/meteor';
import { ClientsCollection } from '/imports/api/ClientsCollection';

const insertClient = client => ClientsCollection.insert(client);

Meteor.publish("tasks", () => {
  return ClientsCollection.find()
})

Meteor.startup(() => {
  if (ClientsCollection.find().count() === 0) {
    [
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
      ]
    ].forEach(insertTask)
  }
});