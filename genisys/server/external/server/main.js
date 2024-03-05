import { Meteor } from 'meteor/meteor';
import { ClientsCollection } from '../api/clients/clients';
import { Picker } from 'meteor/communitypackages:picker';
import '../api/clients/server/publications';
import '../api/clients/server/methods';
import bodyParser from 'body-parser';

Picker.middleware(bodyParser.urlencoded({ extended: false }));
Picker.middleware(bodyParser.json());

const insertClient = client => ClientsCollection.insert(client);

const postRoutes = Picker.filter(function(req, res){
  return req.method === 'POST';
})

// Post route for adding clients
postRoutes.route('/api/add-client', async function (params, req, res) {
  console.log('Someone is adding a new client!', req.body);

  if(!('hostname' in req.body && 'ip' in req.body)) {
    console.log("Bad request body");

    res.writeHead(400);
    res.end(JSON.stringify({
      status: 400,
      message: 'Missing IP or Hostname in request body'
    }));
    return;
  }

 const clientId= ClientsCollection.insert({
  ...req.body,
  createdAt: new Date()
 });
  res.writeHead(200);
  res.end(JSON.stringify({
    clientId: clientId,
    status: 200,
    message: 'Added new client'
  }));
});

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
});