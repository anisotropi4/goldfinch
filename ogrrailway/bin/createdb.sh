#!/bin/sh
# based on arangodb docker here https://github.com/guidoeco/docker/tree/master/arangodb
. ar-env.sh

# create database, user and grant user read-write permissions to database 
${NODE} <<@@EOF2
const arangojs = require('arangojs');
const db = new arangojs.Database({url: 'http://ar-server:8529', databaseName: '_system' });
db.useBasicAuth("root", "${ARPASSWORD}");
function createdb() {
    db.listDatabases()
    .then(names => {
                 for (i in names ) {
                         console.log('name: ', names[i])
                         if (names[i] == "${ARDBN}") {
                                db.dropDatabase('${ARDBN}')
                                .then(info => { console.log('drop: ', info); },
                                      err => { console.error('names error: ', err)})};}})
          .then(t => { db.createDatabase('${ARDBN}')
                .then(info => { console.log('create: ', info);
		                            db.listDatabases()
                                .then(names => { console.log('names: ', names)},
                                      err => { console.error('names error: ', err)})},
                      err => { console.error('error create: ', err)})})
         }
const request = require('request');
function createuser(callback) {
    request.post('http://root:${ARPASSWORD}@${ARSVR}:8529/_api/user',
		 { json: { 'user': '${ARUSR}', 'passwd': '${ARPWD}' }},
		 function (error, response, body) {
		     if (!error && response.statusCode == 200) { console.log(body); }
            if (error) { console.error(error); }
		 });
};
createdb();
createuser();
@@EOF2

sleep 1
${NODE} <<@@EOF3
var request = require('request');
function grantpermissions() {
    request.put('http://root:${ARPASSWORD}@${ARSVR}:8529/_api/user/${ARUSR}/database/${ARDBN}',
		{ json: { 'grant': 'rw' }},
	     function (error, response, body) {
		 if (!error && response.statusCode == 200) {
			console.log(body)
		    }
	     });
};
grantpermissions();
@@EOF3
